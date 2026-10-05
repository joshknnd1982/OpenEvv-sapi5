# Brief for the IPA chart research helpers (Phase 0, step 6b)

One helper per chart section. Each writes one JSON file in this folder. This brief is the whole task; the merged checklist is built from the seven files by `inventory/build_ipa_checklist.py`.

## Goal

Record every symbol the *current official* IPA chart prints in your section: what it is, its exact Unicode codepoints, its official name, how it is articulated and what it is expected to look like acoustically, with sources. Research only. Do not design phonemes, do not touch engine code, and do not judge what the engine can do (that column is filled in afterwards from the code).

## Rules that bind

- **Look up, don't recall.** Use WebSearch/WebFetch. The chart to follow is the International Phonetic Association's current chart (the 2015 chart as revised; find the latest revision, its date, its URL and its licence line, and record them). If the official page is an image or PDF you cannot read as text, say so and use a faithful text transcription of it (the IPA's own "IPA number chart"/Unicode chart pages, the Unicode Standard's IPA Extensions/Phonetic Extensions/Spacing Modifier/Combining Diacritical Marks code charts, Wikipedia's "International Phonetic Alphabet chart" or "International Phonetic Alphabet"), and say which you actually read.
- **Never cite a source you did not open in this session.** Each source in `references` has `"read": true` only if you fetched it and found the fact there. A fact you know but could not find in a fetched source goes in with `"provenance": "recalled-unverified"`; one found in a fetched source has `"provenance": "literature"` and names the reference ids. Do not invent numbers. A range of hertz or milliseconds needs a fetched source; without one describe the correlate in words and tag it `recalled-unverified`.
- **Licences.** Record each source's licence. Write the facts in your own words; do not paste long passages (CC BY-SA text must not be copied into this MIT project). Short official names and codepoints are facts and fine.
- **Exact codepoints.** Give every symbol as its exact Unicode scalar values, `U+XXXX`, and the Unicode character name, checked against a Unicode source (unicode.org code charts, or a page that quotes them). Watch the classic traps: ɡ is U+0261 not U+0067; ː is U+02D0 not a colon; ˈ U+02C8 and ˌ U+02CC are not apostrophe/comma; ʼ ejective is U+02BC; ǀ ǁ ǂ ǃ are U+01C0..U+01C3; the tie bars are U+0361 and U+035C; ‿ linking is U+203F; | and ‖ minor/major group are U+007C and U+2016; tone letters are U+02E5..U+02E9; ꜛ ꜜ are U+A71B/U+A71C; ↗ ↘ are U+2197/U+2198.
- **Count exactly.** One entry per distinct symbol the chart prints in your section. Shaded or empty cells are not entries. Where the chart prints two representations of the same thing (a tone diacritic and a tone letter; ring below and ring above for voiceless; the two tie bars), each printed representation is its own entry, linked with `equivalent_to`. A diacritic is entered as the combining or modifier character alone (the chart's carrier letter goes in `chart_example`). Example combinations the chart prints only as examples (such as `t̪ d̪` beside "Dental") are not entries. State your section's count and how you arrived at it, and note anything whose membership in the section is arguable.

## Sections

`pulmonic` Consonants (pulmonic) table · `non_pulmonic` Consonants (non-pulmonic): clicks, voiced implosives, ejectives · `other_symbols` Other symbols, including the affricate/double-articulation tie bars · `vowels` Vowels trapezium · `diacritics` Diacritics table · `suprasegmentals` Suprasegmentals (stress, length, group/linking/syllable-break marks) · `tones` Tones and word accents (level and contour, diacritic and letter forms, downstep, upstep, global rise and fall)

## Output: `<section>.json`, UTF-8, this shape

```json
{
  "section": "pulmonic",
  "chart": {"title": "", "revision": "", "url": "", "licence": "", "how_read": "what you actually opened and read"},
  "count": 0,
  "count_explanation": "",
  "symbols": [
    {
      "symbol": "p",
      "codepoints": ["U+0070"],
      "unicode_name": "LATIN SMALL LETTER P",
      "ipa_name": "official IPA name of the symbol if you found one, else null",
      "ipa_number": 101,
      "chart_example": null,
      "alt_codepoints": [],
      "equivalent_to": null,
      "articulatory": "voiceless bilabial plosive",
      "features": {"voicing": "voiceless", "place": "bilabial", "manner": "plosive", "airstream": "pulmonic egressive"},
      "acoustic_correlates": [
        {"text": "silent closure, then a weak, diffuse burst with energy low in the spectrum; formant transitions of neighbouring vowels point down to a low F2 locus", "provenance": "literature", "refs": ["johnson2012"]}
      ],
      "notes": ""
    }
  ],
  "references": [
    {"id": "johnson2012", "title": "", "author": "", "year": "", "url": "", "accessed": "2026-10-05", "licence": "", "read": true, "used_for": ""}
  ],
  "problems": ["anything you could not verify, any disagreement between sources"]
}
```

For vowels use features `height`, `backness`, `rounding`. For diacritics, suprasegmentals and tones use `features` to say what the mark changes (for example `{"modifies": "phonation", "value": "breathy"}`) and make `acoustic_correlates` say what should measurably change on the base sound (for example: lower spectral tilt, raised H1-H2, added aspiration noise). Acoustic correlates may be shared per class (all bilabial plosives, all front rounded vowels) but each symbol must carry its own entries, with whatever is specific to it.

Aim for at least one fetched descriptive phonetics source for the acoustic correlates besides the chart itself (for example a university phonetics course page, an open-access paper or handbook chapter, UCLA/Ladefoged course material, Wikipedia articles as a last resort). Three or four good sources per section are enough; this is a checklist, not a literature review.

## When done

Reply with: the file path, the exact count, the chart revision you found, and the list in `problems`. Nothing else.
