# Architecture map (Phase 0)

Written 2026-10-05 on branch `tts-ext/phase-0`, from the code at tag `tts-ext-baseline` (commit `10542ae`). Every statement here was read from the code or run on this machine; `file:line` names where. Nothing in the engine was changed.

## 1. What this project is

Three layers, each a separate thing:

| Layer | Where | What it is | Language | Licence |
|---|---|---|---|---|
| The engine, **openevv** | `openevv/` | IBM Embedded ViaVoice (Eloquence) rebuilt as C: a rule machine ("Delta") that turns text into frames, and a Klatt formant synthesiser that turns frames into samples. One module (DLL) per language. | C, GNU make, mingw-w64 GCC | Code MIT; language data is IBM's and not licensed (see `NOTICE.md`) |
| The reader, **OpenEvvFrontend** | `frontend/` | A program that links eSpeak NG. It reads the text of 145 more languages (spelling rules, dictionary, numbers, stress, tones) and writes each word as phones of an openevv module, with markup saying what each phone was *meant* to be. | C, CMake, MSVC + Ninja | GPL v3 or later |
| The wrapper | `src/`, `installer/`, `engine/` | The SAPI 5 engine DLL, the engine host process, the configuration program, the tools, the Python scripts that write language packs, the installer. | C++17, CMake, MSVC; Python 3 | MIT (some SAPI scaffolding files excepted, `NOTICE.md`) |

## 2. Environment (determined, not assumed: R12)

- OS: Windows 11 Home 10.0.26300, 64-bit. The product is Windows-only (SAPI 5); openevv itself also builds on Linux, not used here.
- Compilers: Visual Studio 2022 Build Tools 17.14 (MSVC, x86 and x64) for the wrapper and the front-end; MSYS2 at `C:\msys64` with `x86_64-w64-mingw32-gcc` and `i686-w64-mingw32-gcc` for the engine modules. CMake at `C:\Program Files\CMake`. Python 3.10 (64-bit). Inno Setup 6 (per-user install). Ninja and bash are not on PATH (Ninja is the one bundled with Visual Studio; bash is MSYS2's).
- Runtime: native Win32, x86 and x64. Static MSVC runtime (`CMakeLists.txt:13`).
- **Public integration interface: SAPI 5.** The COM engine class is `{f3cc6ab4-c4c4-4ec6-aa1f-1a114367ae91}` (`src/sapi/ISpTTSEngineImpl.hpp:19`); voices come from a token enumerator `{90e5cef9-18dd-435e-ae19-bec9b58d3627}` registered under `HKLM\Software\Microsoft\Speech\Voices\TokenEnums\OpenEVV` (`src/sapi/sapi_main.cpp:28-38`), eight voice tokens per visible language pack (`src/sapi/voice_token.cpp:10-27`). A second, lower interface is IBM's ECI API exported by every module DLL (`openevv/include/eci.h`); the wrapper's own host uses it (`src/common/eci_module.cpp:23-73`). The NVDA add-on and the Speech Dispatcher module under `openevv/` are carried in the snapshot and not built or shipped by this repository.

## 3. Build commands (run on 2026-10-05; outputs in PROJECT_STATE.md)

```
cmake -G "Visual Studio 17 2022" -A x64   -S . -B build_x64
cmake --build build_x64 --config Release
cmake -G "Visual Studio 17 2022" -A Win32 -S . -B build_x86
cmake --build build_x86 --config Release
```

These build the wrapper (SAPI DLL, host, configuration program, `evv_say`, the tests) into git-ignored folders and touch nothing tracked. Speaking from the command line then needs only what is already in the repository (`languages/`, `dist/x64/OpenEvvFrontend.exe`, `dist/espeak-ng-data`):

```
.\build_x64\bin\Release\evv_say.exe <tag> <preset 1-8> <text | @utf8file> <out.wav> [32|64]
.\build_x64\bin\Release\evv_say.exe --list
```

The engine modules from source, without touching `languages/` (the build happens in a copy outside the repository, `engine/build_modules.sh:24-27`):

```
$env:MSYSTEM='MSYS'; $env:CHERE_INVOKING='1'
$env:OPENEVV_WORK="$env:LOCALAPPDATA\OpenEvvBuild-ttsext"; $env:TAGS='enus dedx'
& C:\msys64\usr\bin\bash.exe -l "$PWD\engine\build_modules.sh"
```

Run on 2026-10-05 this built `enus` in 250 s and `dedx` in 174 s (both bitnesses and `evv-<tag>.exe`). The DLLs it made are not byte-identical to the ones in `languages/` (different hashes; `openevv-enus-x64.dll` is the same 9,867,960 bytes). Whether they sound identical has not been tested yet: that is Phase 1's first question.

Things that **do** overwrite tracked files, so are not for casual use: `build_all.bat` (deletes and restages `dist\x86`, `dist\x64`, `dist\docs`; the front-end step replaces `dist\espeak-ng-data`), `engine\build_modules.cmd` (its last step, `engine/make_language_packs.py`, overwrites the DLLs and `language.ini` in `languages\<tag>\`; no output-folder option), and `build_all.bat packs` (rewrites all 145 eSpeak NG packs). `build_all.bat` passes its tests even when the front-end was built from the wrong eSpeak NG source (stale CMake cache); after any front-end build check `git diff --ignore-cr-at-eol --stat -- dist/espeak-ng-data`.

## 4. Text to audio

```
SAPI client (screen reader, any SAPI 5 program)
  -> OpenEvvSAPI.dll   ISpTTSEngineImpl::Speak            src/sapi/ISpTTSEngineImpl.cpp:755
       two anonymous pipes (stdin/stdout), messages in src/common/protocol.h
  -> OpenEvvHost.exe   one process per module, pooled      src/common/host_client.cpp, src/host/host_main.cpp
       for a language read by eSpeak NG only:
       -> OpenEvvFrontend.exe --serve (pipes, src/common/frontend_proto.h)
            eSpeak NG translates a clause -> phonemes -> map lookup -> annotated text
  -> module DLL        languages/<tag>/openevv-<tag>-x64.dll (IBM's ECI API)
       eciAddText / eciInsertIndex / eciSynthesize / eciSynchronize     src/host/host_main.cpp:614-733
       inside the module:
         text filter and accent markup stripped   openevv/src/accent/evv_accent.c:913
         Delta rule machine runs the language's rules  (G2P, stress, phonology, duration, intonation, formant targets)
         rules write breakpoints into parameter streams; callInternalSynthesizer -> synthesize   openevv/src/klatt/klatt_run.c:878
         sendArrayParameters makes one frame per 5 ms by straight-line interpolation   openevv/src/eci/bridge/eci_arraygen.c:147-200,258
         accent layer rewrites the frames of each phone (only when markup was present)   evv_accent_run
         KlattSynth turns each frame into samples   openevv/src/klatt/klatt_synth.c
  <- 16-bit mono PCM, 11025 Hz by default, back up the pipes; SAPI gets it in 20 ms pieces
```

- Sample rates offered: 8000, 11025, 16000, 22050, 32000, 44100, 48000 (`src/common/settings.cpp:10-11`). The synthesiser runs at 8000 or 11025 with IBM's own tables; above 11025 it synthesises at 11025 and upsamples (windowed sinc) (`openevv/src/eci/api/eci_env.c:325-342`).
- SAPI events: sentence boundary, word boundary and bookmark, from index marks the wrapper inserts and the engine echoes (`ISpTTSEngineImpl.cpp:614-650`). No viseme or phoneme events.
- **SAPI pronunciation input is ignored.** `SPVA_Pronounce` is spoken as plain text and `pPhoneIds` is never read; there is no SSML handling in the wrapper. The engine has an IPA-to-phoneme converter for six languages (`openevv/src/eci/ssml/eci_ipatospr.c`) reachable only through IBM's SSML filter, which the wrapper never registers. So today **no caller can hand the product an IPA string.** The only ways in for a chosen sound are engine annotations (`` `[.1wa.0tu] ``, when `Annotations=1`) and, at the front-end's command line only, eSpeak NG phoneme names in `[[ ]]` (`--phonemes`).

## 5. Engine type and term mapping (playbook 1.1b)

**Hybrid; every sounding component is parametric.** There is no recorded speech, no unit inventory and no neural model anywhere in the product.

| Component | Type |
|---|---|
| openevv module: Delta rules + Klatt synthesiser | Parametric, rule-based formant synthesis |
| Accent layer inside the module (`openevv/src/accent/`) | Parametric: per-phone transforms on the frames |
| eSpeak NG as used here | Rule-based text analysis only (its own synthesiser is not used for the product's sound; `engine/accent/verify*.py` uses it as a comparison) |

| Playbook term | What it is here |
|---|---|
| Engine-neutral acoustic specification | Does not exist yet as one table. The nearest things: the per-language `engine/profiles/<tag>.json` (what the literature says), and the hard-coded tables in `engine/accent/sounds.py` (`VOWEL` :48, `LOCUS` :118, `VOT_PLAIN`/`VOT_ASPIRATED` :128-133, `SONORANT` :136, `HISS` :182). |
| Native realization | Two forms. (a) A module phoneme: a name in `statement phone`, a `PhonemeN=` settings line, and a rule `<x>_ph_<name>` with a locus rule `<x>_<place>_Fv` holding formant targets. (b) A `sound sN key=value...` line in a pack's `sounds.map`: a module phone plus differences, applied by the accent layer. |
| Engine adapter | `engine/accent/sounds.py` + `prosody.py` + `mapwriter.py` (design a sound as differences from a measured module phone), the front-end's map lookup (`frontend/src/evv_map.c`), and the accent layer (`openevv/src/accent/evv_accent.c`). |
| Create / extend | New `sound` keys and mechanisms in the accent layer; new frame parameters or sources in `openevv/src/klatt`; new phonemes in a module (`openevv/tools/module/phonemes.py add`, at the end of the list only). |
| Frame parameters | The 62-word frame below. |

## 6. The synthesiser (every parameter)

A frame is a fixed array of 62 `int32_t` (`openevv/src/klatt/klatt_run.c:453`, names at `:656-665`; the accent layer asserts the same 62, `evv_accent.c:94`).

| Index | Name | Meaning | Unit |
|---|---|---|---|
| 0 | `ui` | frame length | ms (default 5) |
| 1 | `f0` | fundamental frequency | tenths of Hz |
| 2 | `av` | amplitude of voicing | dB |
| 3 | `oq` | open quotient of the glottal pulse | per cent of the period |
| 4 | `tl` | spectral tilt | index into a table, at most 35 |
| 5 | `fl` | flutter (slow pitch wobble) | scale on three fixed sines |
| 6 | `di` | diplophonia (alternate periods differ) | per cent |
| 7 | `ah` | amplitude of aspiration noise | dB |
| 8 | `af` | amplitude of frication noise | dB |
| 9-26 | `f1 b1 df1 db1 f2 b2 f3 b3 ... f8 b8` | cascade formant frequencies and bandwidths | Hz (clamped 10..5000 and 10..4000) |
| 27-30 | `fnp bnp fnz bnz` | nasal pole and nasal zero | Hz |
| 31-34 | `ftp btp ftz btz` | tracheal pole and zero | Hz |
| 35-42 | `a1f ... a8f` | parallel (frication) branch amplitude at each formant | dB |
| 43 | `ab` | bypass: unfiltered frication | dB |
| 44-51 | `b1f ... b8f` | parallel branch bandwidths | Hz |
| 52-61 | `anv a1v ... a8v atv` | voiced parallel branch | **never read by the synthesiser** |

- `df1`, `db1` and the ten `a*v` words are in the frame and are not referenced in `klatt_synth.c`: there is no voiced parallel branch.
- Eight formant slots exist; **five are used** (`n_formants` is 5, `klatt_run.c:951`; a rule argument can raise it, `:967`). 21 resonators in all (`klatt_synth.c:12-21`).
- Topology: cascade/parallel, as Klatt 1980. Voicing and aspiration go through the nasal and tracheal pole/zero pairs and the cascade; only frication drives the parallel branch and the bypass (`klatt_synth.c:687-770`).
- Sources: a parabolic glottal pulse with tilt filter, flutter and diplophonia (`klatt_synth.c:35-58, 429-542`); one white-noise generator for aspiration and frication, halved in the closed part of each voiced period (`klatt_state.c:113-137`). There is no separate burst source, no second noise source and no source that draws air inward.
- Update model: 200 frames a second (5 ms; the rule's step argument, `klatt_run.c:977-978`); 55 samples a frame at 11025 Hz. Parameters are constant within a frame, except that a changed formant slides its filter coefficients over 3 samples (`klatt_synth.c:234-262`). Between frames the values are straight lines between the breakpoints the rules wrote (`eci_arraygen.c:147-200`).
- Taps for measurement: `EVV_KLATT_TAP=file` writes every frame the synthesiser receives (after the accent layer) as 62 tab-separated integers under a header line (`openevv/src/port/evv_klatttap.c:26-94`); `EVV_ACCENT_TRACE=file` writes one line per phone with what it was meant to be (`evv_accent.c:346-357, 2366-2382`); `EVV_ARRAY_TAP=file` writes the breakpoints before interpolation (`eci_arraygen.c:49-60`).

## 7. How phonemes and languages are defined

### A module of its own (the ten native languages)

`openevv/lang/<tag>/`. A phoneme is in three places (`openevv/tools/module/phonemes.py:4-13`, `openevv/docs/language.md:123-129`):

1. its **name and code**: the ordered `name` values of `statement phone` in `<tag>.statements`, each with an 8-byte record (class, voicing, sonority, manner, place, ...);
2. its **numbers**: a `PhonemeN=` line in `<tag>.settings`;
3. its **sound**: a rule `<x>_ph_<name>` that sets the sources and calls one locus rule `<x>_<place>_Fv` where the formant targets are.

| | Where (file name pattern under `lang/<tag>/rules/`, first letter = language) | Form |
|---|---|---|
| Spelling to phonemes (G2P) | `?t_phone` (and `letters`, a text form, for enus/eses/itit); dictionaries `<tag>.dict`, `<tag>.sets` | rules as text (`.dr` lower notation, `.up` upper form), compiled to bytecode or C at build time |
| Syllables, stress | `?t_syll`, `?t_strss` | rules |
| Phonology (allophones) | `?t_phnol` and others | rules |
| Duration | `?s_cdur`, `?s_ndur`, `?s_tdur`, shared `us_dur` | rules |
| Intonation / F0 | `?t_inton`, `?s_inton`, shared `us_inton`, `ut_inton` | rules |
| Formant targets | `?s_val` (locus rules) | rules, with the numbers as immediates |

`<tag>.segments`, `.phonemes`, `.durations`, `.formants` and `lang/measured/` are read-outs measured from the engine for study; nothing in `openevv/src` reads them. Japanese (`jajp`) has no text forms at all: its rules exist only as lifted bytecode, with a romanizer in `openevv/rom/jajp`.

### A language read by eSpeak NG (145 packs)

`languages/<tag>/` holds `language.ini` (`Template=` names the module that speaks, `[Frontend] Voice=` the eSpeak NG voice), `phonemes.map` (the 1.1 map: nearest phones only), `sounds.map` (the map in use) and `sample.txt`. In `sounds.map` (format: `docs/SOUNDS.md`; parser: `frontend/src/evv_map.c:231-454`):

- `@table:name  phone=sN ...` maps an eSpeak NG phoneme, by its table and name, to module phones, each optionally naming a sound;
- a line that starts with IPA maps any phoneme with that IPA from any table; every pack carries such lines for most letters of the IPA chart;
- `sound sN key=value ...` says how the sound differs from the module's phone (formants and bandwidths F1-F4 in per cent, timing in ms, noise in dB; the keys are listed in section 9);
- `accent ...`, `tone ...`, `whwords ...` give melody, tones and question words.

G2P, stress, tone assignment and tone sandhi are eSpeak NG's (compiled data in `dist/espeak-ng-data`, built from `joshknnd1982/espeak-ng` at tag `openevv-1.2.0`). Duration and the frames come from the template module's rules; the accent layer then reshapes them and, with `f0=own`, replaces the module's pitch with its own contour.

### How the existing languages were added, and what they share

**N = 155 languages** in 162 pack folders (`docs/tts-extension/inventory/languages.json`):

- **10 native**: enus, engb, dede, eses, esus, frfr, frca, itit, jajp (nine lifted from IBM's objects) and plpl (Polish, made by copying Italian's text forms and replacing rules; experimental).
- **7 hidden template modules**: dedx, engx, enux, esex, esux, frfx, itix. Each is an IBM module with its own language's phonology rules replaced by rules that do nothing, made at build time by `openevv/tools/module/clone.py` from `openevv/accents/<tag>/` (frfx replaces nothing yet).
- **145 eSpeak NG packs**, by template: dedx 87, esex 21, itix 16, engx 9, esux 7, frfx 3, enux 2. Written by `engine/make_espeak_packs.py`: dump eSpeak NG's phoneme tables, count phonemes in sample text, choose the template by mapping cost (`engine/espeak_phonemes.py:633`; `engine/espeak_templates.txt` overrides 91 tags by hand), design each sound as differences from the template's measured phone (`engine/accent/sounds.py`, against `engine/accent/chassis/<module>.json`), take melody and tones from `engine/profiles/<tag>.json` and hand tables in `engine/accent/prosody.py`, and write the maps.

Shared by all: every line of `openevv/src`, the synthesiser, the accent layer, the wrapper, the pack-writing code and its tables. Per language: a native module's rules and data; or for an eSpeak NG pack its profile JSON, its two maps, its entries in the hand tables of `prosody.py` and `questions.py`, and eSpeak NG's own data for it.

### Voices

Eight presets per pack, each eight numbers: gender, head size, pitch baseline, pitch fluctuation, roughness, breathiness, speed, volume (`openevv/include/eci.h:173-183`; `language.ini` `Params=`). An eSpeak NG pack copies its template's presets. Head size scales the formants inside the rules, not in C (`apply_head_size_val`, `openevv/lang/enus/rules/ut_anno.dr:1183`; the arithmetic was not traced in this phase). Because the scaling has already happened when the accent layer sees a frame, **every formant value in `sounds.map` is a ratio against the module's phone, never hertz** (`evv_accent.c:61-64`).

## 8. Existing tests and measuring tools

| What | How to run (Windows) | Proves |
|---|---|---|
| `sapi_test.exe` (x64, x86) and `sapi_test_cet.exe` | `build_x64\bin\Release\sapi_test.exe --out <dir> [--only <name>] [--all-voices]`; categories: latency, languages, bookmarks, words, silence, pauses, community, prosody, spell, abort, rates, settings, recovery | The SAPI engine through a mock SAPI site |
| `engine/check_espeak_packs.py` | `python engine\check_espeak_packs.py dist\x64\OpenEvvFrontend.exe dist\espeak-ng-data [tag...]` | Every pack: each word accepted as a pronunciation, each phone found in what the map meant |
| `a11y_check`, `installer_a11y`, `installer/test_language_choice.ps1`, `OpenEvvConfig --selftest` | via `build_all.bat` | The configuration program and installer |
| openevv `test/matrix.sh` | bash + make; **979 recorded cases** over the ten native languages are in `openevv/test/samples/*.sha256` | The engine's own gate: sample hashes per case. Written for Linux (`nix develop`); says it drops Wine under MSYS; **not yet run here** |
| openevv `test/words.sh`, `hash.sh`, `crashers.sh` | bash | Twenty thousand words; one-sentence smoke test; strings that must not crash |
| `engine/accent/verify_pack.py`, `verify.py`, `measure.py`, `proof_hindi.py`, `proof_mandarin.py` | Python + numpy; need `probe-<tag>.exe` (see below) and `espeak-ng.exe` | Formants (LPC), VOT, noise, pitch of a pack's sounds beside eSpeak NG's own synthesiser |
| `engine/accent/chassis.py`, `probe.py`, `say.py` | Python + numpy; drive `probe-<tag>.exe` and read `EVV_KLATT_TAP` | Measure every phone of a module from its frames |

There is **no golden audio regression for the 145 eSpeak NG packs** and none at the SAPI level; `matrix.sh` covers only the ten native modules. `engine/accent/probe.py:56` names `engine\build_probes.cmd`, which is not in the repository, so the measuring scripts cannot run from a clean checkout as they stand. No tool uses Praat or scipy.

## 9. What the accent layer can do today

Per-sound keys (`evv_accent.c:616-643`; meanings in `docs/SOUNDS.md`): `f1-f4`, `g1-g4` (+`glide`), `b1-b4`, `dur`, `hold`, `reach`, `vot`, `asp`, `lead`, `bar`, `voi`, `brth`, `f0`, `ej`, `impl`, `burst`, `noburst`, `pre`, `nas`, `fric`, `a2-a6`, `ab`, `av`, `ah`, `af`, `tap`, `tapms`, `oq`, `tl`, `creak`, `whisper`, and for a sound the layer makes itself out of the neighbouring vowel (`<`): `ms`, `hush`. Melody keys and tone lines: `docs/SOUNDS.md`. Pitch with `f0=own` is a target line per syllable followed by a critically damped second-order filter, plus declination and phrase endings, clamped to 40..600 Hz (`evv_accent.c:1305-1510`). A tone is at most 8 points (`MAX_POINTS`), on Chao's five levels in tenths.

Fixed limits: 384 sound definitions, 64 tones, phone names of at most 7 characters, at most 4 phones per map entry (`evv_accent.c:105-111`); the front-end's vowel and glide lists hold 64 and 32 (`evv_map.c:269-274`).

## 10. Gaps I already notice

"Confirmed by code" means the code shows the mechanism is missing or is a stand-in. "Suspected" means it needs the Phase 1 harness to say. Nothing here has been measured yet.

| Gap | Status | Evidence |
|---|---|---|
| No way to hand the product IPA (or any phoneme string) through SAPI | confirmed by code | `pPhoneIds` never read; no SSML; section 4 |
| Clicks (ʘ ǀ ǃ ǂ ǁ) have no mechanism of their own | confirmed by code | every pack maps them to `t`/`p` with `burst=8 ej=25` (an ejective-like stop); the synthesiser has no ingressive or separate burst source; `burst` only scales frication the module already makes (`evv_accent.c:2098-2108`) |
| Epiglottals ʜ ʢ ʡ are in no map | confirmed by data | 0 of 145 packs have a line for them |
| An unmapped phoneme is dropped silently | confirmed by code | `frontend_main.c:482-483` (`if (n == 0) continue;`); a `-` line likewise; no warning anywhere |
| Bilabial trill ʙ, labiodental flap ⱱ are plain substitutions | confirmed by data | mapped to `v`/`R`/`r`/`b` with no sound definition |
| Trills and taps are amplitude and F1 dips, not closures | confirmed by code | `evv_accent.c:2270-2290`; whether that is acoustically enough is suspected-insufficient until measured |
| Ejectives: silence after the burst only | confirmed by code (`ej` key); adequacy suspected | no change to burst spectrum or to the following vowel's onset |
| Implosives: voicing swells towards release only | confirmed by code (`impl` key); adequacy suspected | no falling-then-rising F0, no lowered larynx formant cue |
| Breathy and creaky voice exist (`brth`, `creak`, `oq`, `tl`, `di`) | present; adequacy suspected | breathy is tied to a stop release (`brth` in ms) or a tone; no key for a steadily breathy vowel other than `oq`/`tl`/`ah` by hand |
| Nasalization: one knob | confirmed by code | `nas` moves the nasal zero towards pole+170 Hz and widens B1; the nasal pole frequency/bandwidth and zero cannot be set (`fnp`, `bnp`, `bnz` have no key) |
| Pharyngealization, velarization, palatalization, labialization as transforms | absent as transforms | they can only be written by hand as `f1-f4` ratios on each sound; nothing composes a diacritic onto an arbitrary base |
| Only F1-F4 and B1-B4 can be moved; F5-F8, the tracheal pair, parallel bandwidths and `a1f` cannot | confirmed by code | `evv_accent.c:96-97` |
| Formants only as ratios against a module phone | confirmed by code | a target with no near module phone (a click, an epiglottal) has nothing to be a ratio of |
| Tone contours: 8 points, 5 levels in tenths, own-F0 only | present | contour and level tones of the chart look expressible; downstep, upstep, global rise and fall have no named control (the phrase-end and declination keys are per language, not per mark) |
| Pitch accents of Swedish, Norwegian, Serbo-Croatian, Slovenian, Lithuanian, Latvian; Thai tones | absent | `docs/SOUNDS.md` "What is not there yet": eSpeak NG does not supply them |
| Length marks (ː ˑ ̆) as general transforms | partly | long is tried as IPA+`ː` in the map (`frontend_main.c:475-479`) and by `dur`; half-long and extra-short have no general handling |
| Syllabic, non-syllabic, no audible release, nasal and lateral release, linguolabial, apical/laminal, advanced/retracted tongue root, more/less rounded, raised/lowered, centralized | unknown to absent | `noburst` exists; the rest have no key and no composing rule; how eSpeak NG's phoneme tables present them is unknown until Phase 1 |
| Stress beyond the template's habits | partly | stress digits 0/1/2 reach the module; Italian and Spanish modules have no secondary stress (`frontend/README.md`); the layer's own `accent`/`accent2`/`stressed`/`weak` keys carry it when `f0=own` |
| Syllable break, linking, minor and major group marks | unknown | punctuation drives phrase endings; no handling of the IPA marks themselves was found |
| No golden regression for the 145 packs; measuring scripts not runnable from a clean checkout | confirmed | section 8 |
| Japanese module cannot be edited as text | confirmed | `lang/jajp` has bytecode only |

## 11. Rewrite candidates (nothing rewritten; Phase 2 decides)

| Candidate | Why it blocks "every IPA symbol" or "data-only languages" | Coupling | Dependents |
|---|---|---|---|
| **No engine-neutral table of sounds.** The knowledge is split between `sounds.py` tables, 145 profiles, 14 chassis files and the generated maps. | A symbol's target is designed afresh per template as ratios; there is no one place that says what ʈ is, with provenance. | `engine/accent/sounds.py` (1,100 lines), `mapwriter.py`, `make_espeak_packs.py` | all 145 packs' `sounds.map` |
| **Ratio-only realization against a module phone.** | Sounds with no near neighbour in the template (clicks, epiglottals, trills) cannot be specified; the same sound needs seven different definitions, one per template. | accent layer `def` structure; `sounds.map` format; front-end `{D}` markup | every sound line in every pack |
| **Seven template modules, chosen per language.** | The same IPA symbol sounds different (and is differently wrong) in dedx, esex, itix...; a new language inherits a template's phone set (34 to 53 phones) and its timing and coarticulation rules. | module rules; `espeak_templates.txt`; chassis measurements | 145 packs |
| **Fixed 62-word frame with five formants in use and one noise source.** | No burst/transient source (clicks, strong ejectives), no voiced parallel branch (the `a*v` words are dead), limited nasal control. | `openevv/src/klatt/*`, the accent layer's parameter enum, the taps, IBM-derived resonator tables | every module; the 979-case gate (hash-exact) |
| **Phoneme inventory of a module is an ordered list baked into rules and dictionaries.** | New phonemes can only be appended; rules that test neighbours never see them (`openevv/docs/notes/polish.md`). Adding dozens of phonemes per module this way is the expensive route. | `<tag>.statements`, `.settings`, rule files, dictionaries | each native module |
| **The front-end drops what it cannot map and reports nothing.** | "Never silent" (R7, R19) cannot be checked without at least a diagnostic. | `frontend/src/frontend_main.c`, `evv_map.c` | all 145 packs |
| **G2P is bound to eSpeak NG's compiled data** (GPL), and for the ten native languages to IBM's rules. | A new language needs an eSpeak NG voice (C tables + compiled dictionary) before it can be a pack: not a data-only change inside this repository. Dialects and accents that eSpeak NG lacks have no home. | `frontend/`, `dist/espeak-ng-data`, the separate espeak-ng fork | all 145 packs |
| **No phoneme-level input through the public interface.** | The checklist's "render each symbol" needs a direct IPA or phoneme path; today only the front-end's command line has one. | `src/sapi/ISpTTSEngineImpl.cpp`, `src/host/host_main.cpp`, `frontend --serve` protocol | SAPI clients (additive: would not change existing behaviour) |
| **Prosody by keyword-matching profile prose plus hand tables** (`prosody.py:63-225`). | Melody and tone for a new language need code edits to hand tables, not data. | `engine/accent/prosody.py`, `questions.py` | all packs with `accent`/`tone` lines |
| **Timing model is the template module's rules, then scaled.** | Bursts, closures and contour timing are whatever the module's stop rules produce; the layer scales (0.2 to 4.0) and inserts lead frames but cannot lay out a new sequence of events (for example closure, click burst, silence, release). | accent layer stretch logic; module duration rules | all packs |

## 12. Licence and origin note (R4; flagged, not blocking)

- The engine code is a rebuild of IBM's Embedded ViaVoice from its 1999 Windows objects: transcribed and reverse-engineered. Its authors license their own code under MIT; **the language data (`openevv/lang/`, every module in `languages/`, `klatt_tables.c`, `eci_xmltok_tables.c`) is IBM's and is not licensed to anyone here** (`NOTICE.md`, `openevv/NOTICE`). Who holds the rights today is unsettled (Cerence v. Microsoft and Nuance, D. Del. 1:25-cv-00553).
- eSpeak NG, the front-end, `dist/espeak-ng-data`, and the `sounds.map`/`phonemes.map` files written from eSpeak NG's phoneme tables are GPL v3 or later.
- Consequence for this project: new work should go where the licence is clean (the accent layer, the wrapper, new tables of our own: MIT) and should not copy data from GPL or ShareAlike sources into MIT files. The IPA chart itself is CC BY-SA: cite it, do not paste it.

## 13. Corrections and additions from Phase 2 (2026-10-05)

The text above is left as Phase 0 wrote it. Phase 2 read the code again for the design and found these; the evidence is in `DESIGN.md` ("The facts this design rests on") and `DECISIONS.md` D30. Some were established by a research helper reading the code and were not re-run by the main session; `DESIGN.md` marks those "(helper)".

- **Section 6.** `df1` is ignored by the synthesiser but is written by the rules (0 in everything measured). The words nothing writes or reads are `db1` and the ten `a*v` words. The synthesiser has no burst, step or impulse source. One noise generator serves two independent streams (aspiration, frication). Formants cannot be asked above 5000 Hz. With the default resampler speech is synthesised at 11025 Hz and upsampled, so nothing above 5512 Hz is produced at any output rate; the user setting `Resampler=none` synthesises at the output rate instead. A frame's length word is honoured per frame, and frames shorter than 5 ms already occur. Six filter slots are spare while five formants are in use.
- **Section 7, voices.** Head size multiplies F1 to F5 by (125 minus half the head size) per cent and changes nothing else (measured). Gender switches defaults and applies factors that differ by frequency range. All eight voice settings are applied in the modules' rules, none in C.
- **Section 7, native modules.** A phone name of more than one letter is written in single quotes in an annotation (`'E:'`, `'a~'`). The `PhonemeN=` settings line is not on the synthesis path. A module can report the phonemes of a text (`eciGeneratePhonemes`).
- **Section 9.** A map entry may hold 8 phones; 4 is the limit of a `says` rule. The sound key `f0` has no effect when the layer makes the pitch, which is in all 145 packs. The tone key `av` is parsed and never applied. A stop's release keys act on the frames of whatever follows, a pause included, and the voice-onset key and the breathy-release key force voicing there even when what follows is voiceless or a pause: a defect in the shipped packs (`DESIGN.md`, "A defect found on the way"). A sound definition is a flat record: one definition a phone, no event list, no composition.
- **Section 10.** The length mark and the palatalisation mark are mapped to nothing in all 145 packs, so a long consonant is said short; the generator ignores about a dozen chart marks without a message. Nine native modules *and the 32-bit US English module* predate the accent layer.
- **Section 11.** The front-end's error output is discarded by the host: there is no channel for a warning today. `engine/accent/prosody.py` and `questions.py` hold tables keyed by language tag (tones for 12 tags, question words for 115), so a new tone language needs a code edit.
