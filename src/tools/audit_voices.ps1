# Audits an installed OpenEVV through SAPI itself, as a screen reader uses it: every
# OpenEVV voice SAPI lists speaks its language's sample (sample.txt, and digits) into
# memory, and one TSV row a voice says how long, how loud and how voiced the audio was.
# Run it once from each PowerShell to audit both bitnesses:
#
#   powershell -File src\tools\audit_voices.ps1 -Out audit64.tsv
#   C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe -File src\tools\audit_voices.ps1 -Out audit32.tsv
#
# -Only takes a comma-separated list of language tags. A row whose status is not "ok",
# or whose audio is under a second or barely voiced, is a voice to listen to.
param(
    [string]$Out,
    [string]$Only = "",
    [int]$TimeoutMs = 30000
)
$ErrorActionPreference = "Stop"
Add-Type -TypeDefinition @"
public static class AudioStats {
    // returns peak, fraction of 10 ms frames whose RMS > 300
    public static double[] Stats(byte[] b) {
        if (b == null || b.Length < 2) return new double[] {0, 0};
        int n = b.Length / 2; int peak = 0; int frames = 0, voiced = 0;
        double acc = 0; int cnt = 0;
        for (int i = 0; i < n; i++) {
            int s = (short)(b[2*i] | (b[2*i+1] << 8));
            int a = s < 0 ? -s : s; if (a > peak) peak = a;
            acc += (double)s * s; cnt++;
            if (cnt == 110) { frames++; if (System.Math.Sqrt(acc / cnt) > 300) voiced++; acc = 0; cnt = 0; }
        }
        return new double[] {peak, frames == 0 ? 0 : (double)voiced / frames};
    }
}
"@
$bits = if ([IntPtr]::Size -eq 8) { 64 } else { 32 }
$root = "C:\Program Files\OpenEVV SAPI5\languages"
$builtin = @{ dede = "Guten Tag. Eins, zwei, drei."; eses = "Hola. Uno, dos, tres."; esus = "Hola. Uno, dos, tres.";
    frfr = "Bonjour. Un, deux, trois."; frca = "Bonjour. Un, deux, trois."; itit = "Buongiorno. Uno, due, tre.";
    plpl = "Dzień dobry. Jeden, dwa, trzy."; jajp = "こんにちは。一、二、三。"; enus = "Hello. One, two, three."; engb = "Hello. One, two, three." }
$v = New-Object -ComObject SAPI.SpVoice
$tokens = $v.GetVoices("Vendor=OpenEVV", "")
$count = $tokens.Count
"# $bits-bit: $count OpenEVV voices listed" | Out-File -FilePath $Out -Encoding utf8
"bits`tidx`ttag`tpreset`tname`tchars`tseconds`tspc`tpeak`tvoiced`tms`tstatus" | Out-File -FilePath $Out -Append -Encoding utf8
for ($i = 0; $i -lt $count; $i++) {
    $t = $tokens.Item($i)
    $tag = $t.GetAttribute("OpenEvvLanguage")
    $preset = $t.GetAttribute("OpenEvvPreset")
    if ($Only -and ($Only -split ",") -notcontains $tag) { continue }
    $name = $t.GetDescription(0)
    if ($builtin.ContainsKey($tag)) { $text = $builtin[$tag] }
    else {
        $text = [IO.File]::ReadAllText("$root\$tag\sample.txt", [Text.Encoding]::UTF8).Trim()
        $text = $text + " 1 2 3."
    }
    $ms = New-Object -ComObject SAPI.SpMemoryStream
    $ms.Format.Type = 10   # SAFT11kHz16BitMono, 22050 bytes a second
    $status = "ok"
    $sw = [Diagnostics.Stopwatch]::StartNew()
    try {
        $v.Voice = $t
        $v.AudioOutputStream = $ms
        [void]$v.Speak($text, 1)   # SVSFlagsAsync
        if (-not $v.WaitUntilDone($TimeoutMs)) {
            $status = "TIMEOUT"
            [void]$v.Speak("", 3)    # purge
            [void]$v.WaitUntilDone(5000)
        }
    } catch {
        $status = "ERROR " + $_.Exception.Message.Replace("`t", " ").Replace("`r", " ").Replace("`n", " ")
    }
    $elapsed = $sw.ElapsedMilliseconds
    $data = [byte[]]$ms.GetData()
    $secs = if ($data) { $data.Length / 22050.0 } else { 0 }
    $st = [AudioStats]::Stats($data)
    $spc = $secs / [Math]::Max(1, $text.Length)
    "{0}`t{1}`t{2}`t{3}`t{4}`t{5}`t{6:N2}`t{7:N3}`t{8}`t{9:N2}`t{10}`t{11}" -f $bits, $i, $tag, $preset, $name, $text.Length, $secs, $spc, $st[0], $st[1], $elapsed, $status |
        Out-File -FilePath $Out -Append -Encoding utf8
    $v.AudioOutputStream = $null
}
"# done" | Out-File -FilePath $Out -Append -Encoding utf8
