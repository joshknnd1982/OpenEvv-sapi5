<#
  The installer's choice of languages, tested by installing the accessibility probe with
  different choices and looking at what lands in {app}\languages.

    powershell -File installer\test_language_choice.ps1 -Probe PATH\OpenEVV-SAPI5-AccessibilityProbe.exe

  The probe is installer\openevv.iss compiled with /DProbe: the same components, the same [Code], but
  per user, with no registration, and each language pack installs only its language.ini. What each
  choice must leave behind is worked out here from languages\*\language.ini, not from the generated
  lists the installer is made from, so a mistake in them is found.

  Covered: the four types, single languages with the module pack they need (and no other), an
  upgrade that adds languages, one that removes them (and the module packs nothing uses any more),
  an upgrade with nothing on the command line offering exactly what is installed (from a full
  installation, from a partial one, and from one where a language was deleted by hand), a pack
  that somebody added by hand beside the installed ones keeping the module pack it needs, and
  the uninstall.

  With -Walker PATH\installer_a11y.exe the wizard itself is walked too, as a person clicking through
  it: what the languages page shows checked on a fresh install and when upgrading, and what is
  installed when setup is done.
#>
param(
    [Parameter(Mandatory = $true)][string]$Probe,
    [string]$Languages = '',
    [string]$Walker = ''
)
$ErrorActionPreference = 'Stop'
if (-not $Languages) { $Languages = Join-Path (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)) 'languages' }
if (-not $Walker) {
    $w = Join-Path (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)) 'build_x64\bin\Release\installer_a11y.exe'
    if (Test-Path $w) { $Walker = $w }
}
$Key = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\{DB3F06B0-C03E-4F87-9739-B953FC329AAF}_is1'
$Work = Join-Path $env:TEMP 'OpenEVV_language_choice'
$Dir = Join-Path $Work 'app'
$failures = 0
$checks = 0

# ---- what the repository says -----------------------------------------------------------------
function Read-Pack($folder) {
    $ini = Join-Path $folder.FullName 'language.ini'
    if (-not (Test-Path $ini)) { return $null }
    $p = [ordered]@{ Tag = $folder.Name; Template = ''; Hidden = $false; Order = 1000 }
    $section = ''
    foreach ($line in (Get-Content -LiteralPath $ini -Encoding UTF8)) {
        $l = $line.Trim()
        if ($l -match '^\[(.+)\]$') { $section = $Matches[1]; continue }
        if ($section -eq 'Language' -and $l -match '^(Template|Hidden|Order)=(.*)$') {
            switch ($Matches[1]) {
                'Template' { $p.Template = $Matches[2].Trim() }
                'Hidden' { $p.Hidden = ($Matches[2].Trim() -notin @('', '0')) }
                'Order' { $p.Order = [int]$Matches[2] }
            }
        }
    }
    [pscustomobject]$p
}
$packs = @(Get-ChildItem -LiteralPath $Languages -Directory | ForEach-Object { Read-Pack $_ } | Where-Object { $_ })
$visible = @($packs | Where-Object { -not $_.Hidden })
$native = @($visible | Where-Object { -not $_.Template })
$espeak = @($visible | Where-Object { $_.Template })
$hiddenTags = @($packs | Where-Object { $_.Hidden } | ForEach-Object { $_.Tag })
if ($native.Count -ne 10 -or $espeak.Count -lt 100 -or $hiddenTags.Count -lt 5) {
    throw "languages\ looks wrong: $($native.Count) native, $($espeak.Count) eSpeak NG, $($hiddenTags.Count) module packs"
}

function Component($tag) {
    $p = $packs | Where-Object { $_.Tag -eq $tag }
    $g = if ($p.Template) { 'espeak' } else { 'openevv' }
    "$g\" + ($tag -replace '-', '_')
}
# The packs a choice of languages leaves installed: the languages, and the module packs they speak with.
function Expect($tags) {
    $set = New-Object 'System.Collections.Generic.SortedSet[string]'
    foreach ($t in $tags) {
        [void]$set.Add($t)
        $tpl = ($packs | Where-Object { $_.Tag -eq $t }).Template
        if ($tpl) { [void]$set.Add($tpl) }
    }
    ,@($set)
}

# ---- running the probe --------------------------------------------------------------------------
function Probe-Installed { Test-Path $Key }
function Run-Probe([string[]]$more, [string]$log) {
    $args = @('/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', "/DIR=$Dir", "/LOG=$log") + $more
    $p = Start-Process -FilePath $Probe -ArgumentList $args -Wait -PassThru
    if ($p.ExitCode -ne 0) { throw "the probe's setup exited with $($p.ExitCode): $($more -join ' ')" }
}
function Uninstall-Probe {
    if (-not (Probe-Installed)) { return }
    # the registration reads: "C:\...\unins000.exe" /LOG
    $u = ((Get-ItemProperty $Key).UninstallString -replace '^\s*"([^"]+)".*$', '$1')
    if (Test-Path -LiteralPath $u) {
        Start-Process -FilePath $u -ArgumentList '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART' -Wait | Out-Null
    } else {
        Remove-Item -LiteralPath $Key -Force   # a registration whose uninstaller is gone
    }
    for ($i = 0; $i -lt 300 -and (Probe-Installed); $i++) { Start-Sleep -Milliseconds 100 }
}
# Uninstalls, and removes what the uninstaller leaves: a folder somebody added is not its to delete.
function Reset-Probe {
    Uninstall-Probe
    if (Test-Path $Dir) { Remove-Item -LiteralPath $Dir -Recurse -Force -ErrorAction SilentlyContinue }
}
function Installed-Packs {
    $l = Join-Path $Dir 'languages'
    if (-not (Test-Path $l)) { return ,@() }
    $set = New-Object 'System.Collections.Generic.SortedSet[string]'
    Get-ChildItem -LiteralPath $l -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'language.ini') } |
        ForEach-Object { [void]$set.Add($_.Name) }
    ,@($set)
}

function Check($name, $expected, $actual) {
    $script:checks++
    $e = ($expected | Sort-Object) -join ' '
    $a = ($actual | Sort-Object) -join ' '
    if ($e -eq $a) {
        Write-Host ("  ok    {0} ({1} packs)" -f $name, @($actual).Count)
    } else {
        $script:failures++
        $missing = @($expected | Where-Object { $actual -notcontains $_ })
        $extra = @($actual | Where-Object { $expected -notcontains $_ })
        Write-Host "  FAIL  $name"
        if ($missing) { Write-Host "        missing: $($missing -join ' ')" }
        if ($extra) { Write-Host "        extra:   $($extra -join ' ')" }
    }
}
function Check-True($name, $cond) {
    $script:checks++
    if ($cond) { Write-Host "  ok    $name" } else { $script:failures++; Write-Host "  FAIL  $name" }
}
# The wizard, walked through MSAA on a private desktop (installer_a11y.exe); its verdict is the exit code.
function Walk([string[]]$more) {
    $out = & $Walker $Probe --dir $Dir @more 2>&1 | Out-String
    $out -split "`r?`n" | Where-Object { $_ -match 'items, \d+ checked|selected type|language packs installed|a dialog|of \d+ items checked|FAIL|PASS' } |
        ForEach-Object { Write-Host "        $($_.Trim())" }
    $LASTEXITCODE
}
function Case($title) { Write-Host ""; Write-Host $title }

try {
    if (Test-Path $Work) { Remove-Item $Work -Recurse -Force }
    New-Item -ItemType Directory $Work | Out-Null
    Reset-Probe

    $n = 0
    function Log { $script:n++; Join-Path $Work ("setup{0}.log" -f $script:n) }
    $nativeTags = @($native | ForEach-Object { $_.Tag })
    $allTags = @($visible | ForEach-Object { $_.Tag })

    Case 'The ready-made types, installed fresh'
    Run-Probe @('/TYPE=openevv') (Log)
    Check 'type "openevv": the ten languages the engine speaks itself, and no module pack' $nativeTags (Installed-Packs)
    Reset-Probe
    Run-Probe @('/TYPE=english') (Log)
    Check 'type "english": US and British English' @('enus', 'engb') (Installed-Packs)
    Reset-Probe
    Run-Probe @('/TYPE=full') (Log)
    Check 'type "full": every language and every module pack' ($allTags + $hiddenTags) (Installed-Packs)
    Reset-Probe

    Case 'Nothing chosen on the command line, nothing installed before: the standard choice'
    Run-Probe @() (Log)
    Check 'the default is the type "openevv"' $nativeTags (Installed-Packs)
    Reset-Probe

    Case 'One language read by eSpeak NG brings its module pack and no other'
    $pick = @('nb')
    Run-Probe @('/COMPONENTS="' + (Component 'nb') + '"') (Log)
    Check 'Norwegian Bokmal' (Expect $pick) (Installed-Packs)
    Check-True 'its module pack is dedx, not one of the six others' ((Installed-Packs) -contains 'dedx' -and (Installed-Packs).Count -eq 2)

    Case 'Upgrade: add languages (a second module pack comes with Welsh, US English stays out)'
    $pick = @('nb', 'cy', 'enus')
    Run-Probe @('/COMPONENTS="' + (($pick | ForEach-Object { Component $_ }) -join ',') + '"') (Log)
    Check 'Norwegian Bokmal, Welsh, US English' (Expect $pick) (Installed-Packs)

    Case 'Upgrade with nothing on the command line: what is installed is offered again, and kept'
    Run-Probe @() (Log)
    Check 'the same three languages, unchanged' (Expect $pick) (Installed-Packs)

    Case 'Upgrade: remove languages (and the module packs no language uses any more)'
    $pick = @('enus')
    Run-Probe @('/COMPONENTS="' + (Component 'enus') + '"') (Log)
    Check 'only US English is left; dedx and engx went with their last languages' (Expect $pick) (Installed-Packs)

    Case 'A pack somebody added by hand beside the installed ones keeps the module pack it needs'
    Run-Probe @('/TYPE=full') (Log)
    $mine = Join-Path $Dir 'languages\zz-my-own'
    New-Item -ItemType Directory $mine | Out-Null
    Set-Content -LiteralPath (Join-Path $mine 'language.ini') -Value "[Language]`r`nTag=zz-my-own`r`nName=Mine`r`nTemplate=esux`r`n"
    Run-Probe @('/COMPONENTS="' + (Component 'enus') + '"') (Log)
    Check 'US English, the hand-made pack, and esux for it (every other language and module pack gone)' @('enus', 'zz-my-own', 'esux') (Installed-Packs)
    Reset-Probe

    Case 'Upgrading an installation of the earlier versions: every language, no record of a choice'
    Run-Probe @('/TYPE=full') (Log)
    Remove-ItemProperty -Path $Key -Name 'Inno Setup: Selected Components' -ErrorAction SilentlyContinue
    Remove-ItemProperty -Path $Key -Name 'Inno Setup: Setup Type' -ErrorAction SilentlyContinue
    Run-Probe @() (Log)
    Check 'all languages are offered, and kept' ($allTags + $hiddenTags) (Installed-Packs)

    Case 'A language removed by hand (OpenEVV Configuration does this) is not put back by the next setup'
    Remove-Item -LiteralPath (Join-Path $Dir 'languages\nb') -Recurse -Force
    Run-Probe @() (Log)
    Check 'everything but Norwegian Bokmal' (($allTags | Where-Object { $_ -ne 'nb' }) + $hiddenTags) (Installed-Packs)

    Case 'A choice on the command line wins over what is installed'
    Run-Probe @('/TYPE=openevv') (Log)
    Check 'only the ten languages the engine speaks itself' $nativeTags (Installed-Packs)

    Case 'The log says what was done'
    $text = Get-Content -LiteralPath (Join-Path $Work ("setup{0}.log" -f $n)) -Raw
    Check-True 'it names the languages that were removed' ($text -match 'language not selected, removed: ')
    Check-True 'it names the module packs that went' ($text -match 'module pack no language uses any more, removed: dedx')
    Check-True 'it counts what is installed' ($text -match '10 languages installed, 80 voices')

    if ($Walker) {
        Case 'The wizard, clicked through: a fresh install offers the standard choice'
        Reset-Probe
        Check-True 'the walk passes: 11 items checked (the ten languages and their group), ten packs installed' ((Walk @('--expect-checked', '11', '--expect-type', 'The ten OpenEVV languages', '--expect-packs', '10')) -eq 0)

        Case 'The wizard, with the buttons: select none and go on is refused, select all installs every language'
        Reset-Probe
        Check-True "the walk passes: none selected and Next gives an error that asks for at least one language and stays; select all checks every language and installs every pack" ((Walk @('--buttons', '--expect-packs', "$($allTags.Count + $hiddenTags.Count)")) -eq 0)

        Case 'The wizard, upgrading a choice of two languages after one was removed by hand'
        Reset-Probe
        Run-Probe @('/COMPONENTS="' + ((@('enus', 'nb') | ForEach-Object { Component $_ }) -join ',') + '"') (Log)
        Remove-Item -LiteralPath (Join-Path $Dir 'languages\nb') -Recurse -Force
        Check-True 'the walk passes: only US English is checked (its group is half checked), and no warning that unchecked languages stay' ((Walk @('--upgrade', '--expect-checked', '1', '--expect-type', 'Custom', '--expect-packs', '1')) -eq 0)

        Case 'The wizard, upgrading an English-only installation'
        Reset-Probe
        Run-Probe @('/TYPE=english') (Log)
        Check-True 'the walk passes: the type list says English only, and the two languages are checked (their group is half checked)' ((Walk @('--upgrade', '--expect-checked', '2', '--expect-type', 'English only', '--expect-packs', '2')) -eq 0)

        Case 'The wizard, upgrading an installation of the earlier versions: every language'
        Reset-Probe
        Run-Probe @('/TYPE=full') (Log)
        Remove-ItemProperty -Path $Key -Name 'Inno Setup: Selected Components' -ErrorAction SilentlyContinue
        Remove-ItemProperty -Path $Key -Name 'Inno Setup: Setup Type' -ErrorAction SilentlyContinue
        $everything = $allTags.Count + 2
        Check-True "the walk passes: $everything items checked (every language and both groups), every pack kept" ((Walk @('--upgrade', '--expect-checked', "$everything", '--expect-type', 'All 155 languages', '--expect-packs', "$($allTags.Count + $hiddenTags.Count)")) -eq 0)
        Reset-Probe
    } else {
        Write-Host ""
        Write-Host "  (the wizard is not walked: pass -Walker PATH\installer_a11y.exe to do that too)"
    }

    Case 'Uninstalling takes every pack with it'
    Uninstall-Probe
    $left = @()
    if (Test-Path (Join-Path $Dir 'languages')) { $left = @(Get-ChildItem -LiteralPath (Join-Path $Dir 'languages') -Recurse -File -ErrorAction SilentlyContinue) }
    Check-True 'no language file is left' ($left.Count -eq 0)
}
catch {
    $failures++
    Write-Host "FAIL: $($_.Exception.Message)"
}
finally {
    try { Uninstall-Probe } catch { }
    if (Test-Path $Work) { Remove-Item $Work -Recurse -Force -ErrorAction SilentlyContinue }
}
Write-Host ""
if ($failures) { Write-Host "FAIL: $failures of $checks checks"; exit 1 }
Write-Host "PASS: $checks checks"
exit 0
