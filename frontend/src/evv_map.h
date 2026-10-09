/*
 * OpenEVV front-end: a language pack's phoneme map, and the annotation it
 * writes with it.
 *
 * Copyright (C) 2026 the OpenEVV SAPI5 contributors
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the Free
 * Software Foundation; either version 3 of the License, or (at your option)
 * any later version. See COPYING.
 */
#ifndef EVV_MAP_H
#define EVV_MAP_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define EVV_MAX_PHONES 8   /* engine phones one eSpeak phoneme may become */
#define EVV_PHONE_LEN 8    /* bytes in one engine phone's name, with its nought */
#define EVV_ID_LEN 12      /* and in the name of a sound or a tone */
#define EVV_ASK_LEN 40     /* bytes in a question word, in UTF-8 */

/* One engine phone of a map entry, and what it was meant to be.
 *
 * `sound' names a `sound' line of the map: how the phone is to differ from
 * the module's own. `made' is nought for a phone the annotation carries, and
 * `<' or `>' for a sound the module has no phone for, which the engine makes
 * out of the start of the phone after it or the end of the phone before it;
 * such a sound is written in the markup and never in the annotation.
 */
typedef struct {
	char name[EVV_PHONE_LEN];
	char sound[EVV_ID_LEN];
	char made;
} EvvMapPhone;

typedef struct {
	char key[64];                          /* IPA, or "@table:mnemonic" */
	int n;
	EvvMapPhone phones[EVV_MAX_PHONES];
} EvvMapEntry;

typedef struct {
	char from[EVV_ID_LEN]; /* eSpeak NG's name for a tone */
	char to[EVV_ID_LEN];   /* the map's */
} EvvToneName;

/* A sound or a tone the map defines: the group that says it to the engine,
   and whether the text being written has used it. */
typedef struct {
	char id[EVV_ID_LEN];
	char *group;
	int used;
} EvvDefined;

/* Composition when speaking (DESIGN.md 2.3, C4), read only from a map with
   `version 2`: every chart letter's features, for the nearest-letter
   fallback, and each modifier's transform in the engine's own terms. */
typedef struct {
	char ipa[8];
	char cls;                /* 'c' consonant, 'v' vowel */
	int place, height, backness;
	char f[7][16];           /* consonant: stricture airstream nasal lateral sibilant place2
	                            voicing; vowel: rounding in f[0] */
	int hz[4];               /* a vowel's formants as the map realises it (`f1hz'...), or 0 */
} EvvLetter;

/* keys a mark's line may hold: 12 since extIPA's fricated releases (a stop's
   friction, its level, the voice under it and six noise bands, D72) */
#define EVV_MAX_OPS 12
typedef struct {
	char key[8];
	char op;                 /* '*' a ratio, multiplied; '+' a time, added; '=' a value, set;
	                            '~' towards v Hz by `part' per cent */
	double v;
	double part;
} EvvOp;

typedef struct {
	char mark[16];
	char cls;
	char pre;                /* 1: a `premod' line, for a mark written before its letter */
	int n;
	EvvOp ops[EVV_MAX_OPS];
} EvvMod;

/* A pitch mark typed in IPA (C2, C5), read only from a map with `version 2':
   a tone letter or tone diacritic and its Chao levels (`tonemark ˥ 5'), a
   register step that lasts to the end of the phrase (`register ꜜ -12', in
   tenths of a Chao level), or a slope over the rest of the phrase (`slope ↗
   8', tenths of a Chao level a syllable). */
typedef struct {
	char mark[16];
	char kind;               /* 't' tone, 'r' register, 's' slope */
	int levels[4];
	int n;
	int value;
} EvvToneMark;

enum { W_STRICTURE, W_AIRSTREAM, W_NASAL, W_LATERAL, W_SIBILANT, W_PLACE, W_PLACE2, W_VOICING, W_HEIGHT,
       W_BACKNESS, W_ROUNDING, W_CLASS, W_COUNT };

typedef struct {
	char tmpl[16];          /* the openevv module the phones are for, e.g. "itit" */
	int french;             /* 1: the stress digit goes before the nucleus, as frfr/frca write it */
	int extipa;             /* 1: `notation extipa': the lines marked `extipa' are read (extIPA's own
	                           readings of characters the IPA reads otherwise, Q18) */
	char vowels[64][EVV_PHONE_LEN];
	int n_vowels;
	char glides[32][EVV_PHONE_LEN];   /* may follow an obstruent inside an onset */
	int n_glides;
	char schwa[EVV_PHONE_LEN];        /* put before a syllabic consonant */
	char syl_sound[EVV_ID_LEN];       /* and the sound it is said with, if the map names one */
	char reiterate[2][64];            /* extIPA's reiteration (p\p\p): the IPA said at a `\' after a
	                                     consonant [0] and after a vowel [1] (`reiterate c|v IPA') */
	char secondary;                   /* the digit secondary stress is written with: the Italian
	                                     and Spanish modules have none, and refuse a 2 */
	int apart;                        /* 1: every syllable is a word of its own, as a language
	                                     whose syllables each carry a tone wants */
	int onset;                        /* in such a language, how many phones may begin a
	                                     syllable: 1, or 2 where the second is a glide */
	char clusters[16][2][EVV_PHONE_LEN]; /* and the pairs that may, where it is 1 */
	int n_clusters;
	int accent;                       /* 1: the map has an accent, and markup is written */
	char *header;                     /* the markup every text begins with: the
	                                     language, and what the module says in
	                                     place of what it is given */
	size_t header_len;
	EvvDefined *sounds;               /* and what a text adds if it uses it */
	int n_sounds, cap_sounds;
	EvvDefined *tone_defs;
	int n_tone_defs, cap_tone_defs;
	EvvToneName *tones;
	int n_tones, cap_tones;
	char (*tone_ids)[EVV_ID_LEN];     /* the tones the map defines */
	int n_tone_ids, cap_tone_ids;
	char weak_tones[16][EVV_ID_LEN];  /* those of them a light syllable has */
	int n_weak_tones;
	/* The words a question is asked with: who, what, where. A question that
	   has one is not the question that wants yes or no, and in most
	   languages does not end as that one does. `ask_where' says where in the
	   clause such a word counts: 1 among its first three words, 2 anywhere.
	   A word written with `~' before it counts only when it is not the
	   first word of the clause: Hindi's kya, which asks `what' inside a
	   sentence and makes a yes-or-no question of one it begins. */
	char (*ask)[EVV_ASK_LEN];
	int n_ask, cap_ask;
	int ask_where;
	EvvMapEntry *entries;
	int n_entries;
	int cap_entries;
	int max_key_len;
	int version;                      /* 2: compose when speaking (C4); 0: as before */
	int weights[W_COUNT];
	EvvLetter *letters;
	int n_letters, cap_letters;
	EvvMod *mods;
	int n_mods, cap_mods;
	/* the second character of a mark of two characters (extIPA's ◌̥᪽):
	   `after ᪽ ̥ ̬', the first characters it is a mark after; it is said only
	   after one of them, and that one makes no letter of two (D77) */
	struct {
		char mark[8];
		char firsts[32];
	} after[16];
	int n_after;
	int n_composed;
	EvvDefined *composed;             /* each string composed: its sound id (id) and IPA (group) */
	int n_comp, cap_comp;
	EvvToneMark *tonemarks;
	int n_tonemarks, cap_tonemarks;
	int n_ipa_tones;                  /* tones made from typed IPA */
} EvvMap;

/* A pitch mark the map lists (`tonemark', `register', `slope'), or NULL. */
const EvvToneMark *evv_map_tonemark(const EvvMap *map, const char *ch, size_t len);

/* The id of a tone through `levels' (Chao 1 to 5), moved by `from' tenths of
   a level at its start and `to' at its end; made and kept the first time it
   is asked for. NULL if there is no room. */
const char *evv_map_ipa_tone(EvvMap *map, const int *levels, int n, int from, int to);

/* Whether a character (UTF-8, one code point) is a chart letter the map
   lists, and which. */
const EvvLetter *evv_map_letter(const EvvMap *map, const char *ch, size_t len);

/* Whether the map has a `mod' line for a mark (one code point) on a letter of
   class `cls' (c or v), and whether it has a `premod' line for it on any. */
int evv_map_has_mod(const EvvMap *map, const char *mark, size_t len, char cls);
int evv_map_has_premod(const EvvMap *map, const char *mark, size_t len);

/* Reads a phonemes.map file. Returns 0, or -1 with a message in err. */
int evv_map_load(EvvMap *map, const char *path, char *err, size_t errlen);
void evv_map_free(EvvMap *map);

int evv_map_is_vowel(const EvvMap *map, const char *phone);
int evv_map_is_glide(const EvvMap *map, const char *phone);

/* The map's name for one of eSpeak NG's tones, or NULL if it defines none. */
const char *evv_map_tone(const EvvMap *map, const char *espeak_name);

/* Whether a tone is one a light syllable has: Mandarin's neutral tone. */
int evv_map_tone_is_weak(const EvvMap *map, const char *tone);

/* Whether a word, `n' bytes of UTF-8, is one a question is asked with.
   `first' says the word begins its clause. */
int evv_map_asks(const EvvMap *map, const char *word, size_t n, int first);

/* The engine phones for one eSpeak phoneme. `table' and `mnemonic' are tried
   first, then the IPA exactly, then the IPA taken apart from the left, the
   longest key that fits each time and any character no key starts with
   skipped (a diacritic the template has no way to say). Returns how many
   phones were written to out. */
int evv_map_lookup(const EvvMap *map, const char *table, const char *mnemonic, const char *ipa,
                   EvvMapPhone *out, int max_out);

/* The same, and *matched says whether any entry was found at all: an entry
   the map gives as `-' matches and writes no phone. */
int evv_map_lookup_ex(const EvvMap *map, const char *table, const char *mnemonic, const char *ipa,
                      EvvMapPhone *out, int max_out, int *matched);

/* ---- diagnostics: nothing is lost without a word (DESIGN.md C1) ----
 *
 * Whatever is dropped, cut short, skipped or said as something else on the
 * way from eSpeak NG's phonemes to the annotation is written down here, once
 * for each kind and detail with a count. A `loss' is something the map did
 * not ask for; a `note' is something it did (an entry given as `-', a schwa
 * put before a syllabic consonant). The command line prints them on stderr
 * and --strict fails on a loss; --serve sends them after the result. They
 * change what is reported, never what is said. */

#define EVV_DIAG_NOTE 0
#define EVV_DIAG_LOSS 1

void evv_diag(int level, const char *kind, const char *fmt, ...);
void evv_diag_clear(void);
int evv_diag_losses(void);
/* "level\tkind\tdetail\tcount\n" for each, in the order first met; the
   caller frees it. */
char *evv_diag_text(size_t *len);
/* The map's line being read, for what a load reports; 0 when not loading. */
extern int evv_diag_line;
/* Not 0: nothing is reported, for a lookup that is only a trial. */
extern int evv_diag_quiet;

/* ---- one word, phone by phone, and the annotation it becomes ---- */

#define EVV_WORD_MAX 256

typedef struct {
	char phone[EVV_PHONE_LEN];
	char sound[EVV_ID_LEN];
	char tone[EVV_ID_LEN];
	char made;
	int nucleus;      /* 1: this phone is the vowel its syllable is built on */
	int stress;       /* 0, 1 primary, 2 secondary: meaningful on a nucleus */
	int brk;          /* 1: a syllable begins here, as IPA typed it (`.') */
	int glue;         /* 1: one segment with the phone before it (two
	                     phones joined by a tie bar, `k͡p'): never split */
} EvvPhone;

typedef struct {
	EvvPhone ph[EVV_WORD_MAX];
	int n;
	int has_nucleus;
} EvvWord;

void evv_word_clear(EvvWord *w);

/* Adds what one eSpeak phoneme became. `syllabic' says eSpeak counts it as a
   syllable of its own, `is_vowel' whether it is a vowel there, `stress' is
   the engine's 0/1/2 and `tone' the map's name for the syllable's tone, or
   NULL. A syllabic consonant is given the map's schwa in front of it, so
   that it has a vowel to carry the syllable. */
void evv_word_add(EvvWord *w, const EvvMap *map, const EvvMapPhone *phones, int n, int syllabic,
                  int is_vowel, int stress, const char *tone);

/* Appends the word to out as `[...] with syllable marks and stress digits,
   each annotation with the markup that says what it was meant to be in
   front of it when the map has an accent. Returns the number of bytes
   written, or 0 for a word with nothing in it. */
size_t evv_word_annotate(const EvvWord *w, const EvvMap *map, char *out, size_t room);

/* The markup a text is to begin with: the map's header and the sounds and
   tones used since this was last called. Returns a string for the caller to
   free, its length in *len. */
char *evv_map_begin(EvvMap *map, size_t *len);

#ifdef __cplusplus
}
#endif

#endif
