# packs/: the language packs as data

One folder a language, one `pack.toml` in it. A build step (`engine/packs/`) turns a pack into the
files `languages/<tag>/` holds (`language.ini`, `sounds.map`, `phonemes.map`, `sample.txt`), in the
formats the product reads today, so the product is not changed and needs no TOML reader.

Stage M1 of `docs/tts-extension/DESIGN.md` 11.3: all 163 folders of `languages/` are packs
(146 read by eSpeak NG, `realization = "legacy"`, Belgian Dutch `nl-be` added in 1.3.0; the 10 native languages and the 7 template modules,
`realization = "module"`, which make only their `language.ini`: the DLLs stay where they are).
Every pack builds to files identical to the ones in `languages/`; 18 packs `extends` a parent
and hold only what differs.

## Commands (PowerShell, repository root; Python 3.10 needs `tomli`, the harness venv has it)

    python engine\packs\build_packs.py check                  every pack builds to the file in languages\ (exit 1 if not)
    python engine\packs\build_packs.py build <out> [tag ...]  write the folders languages\<tag>\ would hold
    python engine\packs\build_packs.py explain ru-cl ini.Language.Order     which pack of the chain gave a value
    python engine\packs\build_packs.py list
    python engine\packs\test_packs.py                         the loader's tests (inheritance, stops, round trips)
    python engine\packs\make_child.py <child> <parent>        rewrite a pack as the delta against its parent (proved)
    python engine\packs\import_packs.py <tag>                 a pack from a folder of languages\ (refuses unless identical)
    python engine\packsuild_packs.py build <out> --proposed <tag>   with the proposed overrides realised (to measure them)
    python engine\packsalidate_packs.py [tag ...]            authenticity metadata and anti-caricature rules (Phase 7)

## What a pack holds (`engine/packs/packlib.py` has the full rules)

    [pack]    tag, name, kind (language | dialect | accent), extends, format = 1
    [meta]    sources, licence, note ...        [engine]  reader, template, realization    [files]  eol
    [ini.<Section>]   the keys of language.ini (a key _cN is a comment line, _bN a blank line)
    [sounds] [phonemes]   line = [ { kind = ..., ... }, ... ]: one record a line of sounds.map or phonemes.map
    [sample]  text      remove = [ "ini.Voice3.Params" ]
    [[override]]  a sound's target moved, with provenance and recordings (engine/packs/overrides.py;
                  docs/tts-extension/AUTHENTICITY.md); state "proposed" reaches only a scratch build
    beside pack.toml: measure.toml (what extract_targets.py measures), measured/ (its results),
                  review.toml (what make_packet.py puts in the native review packet)

Inheritance: tables merge key by key, a plain value or list replaces the parent's, `line` is keyed
(an entry with the key of a parent's line replaces it in place; `after = "<key>"` places a new one;
`remove = ["<key>"]` and `reset = true` inside `[sounds]` or `[phonemes]`). A cycle, a missing
parent, an unknown key, a `remove` or `after` naming nothing, two lines of one key, or an `[engine]`
that disagrees with `language.ini` stops the build.

`realization = "legacy"`: the sound lines are the ones the generator wrote
(`engine/make_espeak_packs.py`, `engine/accent/mapwriter.py`), kept as data. Moving them to the
master table's sounds (`realization = "master"`, stages M3 and M4) is a later step; the generator is
retired only after Phase 9 and with the human's agreement (R18).

## Licence

The loader and its tools (`engine/packs/`) are MIT. The `[sounds]` and `[phonemes]` lines of a pack are
the data of the `sounds.map` and `phonemes.map` files, written from eSpeak NG's phoneme tables, and
carry the licence `NOTICE.md` gives those files (GPL-3.0-or-later); `[ini]` is `language.ini`.
