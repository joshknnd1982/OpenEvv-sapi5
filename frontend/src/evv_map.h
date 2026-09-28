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

typedef struct {
	char key[48];                          /* IPA, or "@table:mnemonic" */
	int n;
	char phones[EVV_MAX_PHONES][EVV_PHONE_LEN];
} EvvMapEntry;

typedef struct {
	char tmpl[16];          /* the openevv module the phones are for, e.g. "itit" */
	int french;             /* 1: the stress digit goes before the nucleus, as frfr/frca write it */
	char vowels[64][EVV_PHONE_LEN];
	int n_vowels;
	char glides[32][EVV_PHONE_LEN];   /* may follow an obstruent inside an onset */
	int n_glides;
	char schwa[EVV_PHONE_LEN];        /* put before a syllabic consonant */
	char secondary;                   /* the digit secondary stress is written with: the Italian
	                                     and Spanish modules have none, and refuse a 2 */
	EvvMapEntry *entries;
	int n_entries;
	int cap_entries;
	int max_key_len;
} EvvMap;

/* Reads a phonemes.map file. Returns 0, or -1 with a message in err. */
int evv_map_load(EvvMap *map, const char *path, char *err, size_t errlen);
void evv_map_free(EvvMap *map);

int evv_map_is_vowel(const EvvMap *map, const char *phone);
int evv_map_is_glide(const EvvMap *map, const char *phone);

/* The engine phones for one eSpeak phoneme. `table' and `mnemonic' are tried
   first, then the IPA exactly, then the IPA taken apart from the left, the
   longest key that fits each time and any character no key starts with
   skipped (a diacritic the template has no way to say). Returns how many
   phones were written to out. */
int evv_map_lookup(const EvvMap *map, const char *table, const char *mnemonic, const char *ipa,
                   char out[][EVV_PHONE_LEN], int max_out);

/* ---- one word, phone by phone, and the annotation it becomes ---- */

#define EVV_WORD_MAX 256

typedef struct {
	char phone[EVV_PHONE_LEN];
	int nucleus;      /* 1: this phone is the vowel its syllable is built on */
	int stress;       /* 0, 1 primary, 2 secondary: meaningful on a nucleus */
} EvvPhone;

typedef struct {
	EvvPhone ph[EVV_WORD_MAX];
	int n;
	int has_nucleus;
} EvvWord;

void evv_word_clear(EvvWord *w);

/* Adds what one eSpeak phoneme became. `syllabic' says eSpeak counts it as a
   syllable of its own, `is_vowel' whether it is a vowel there, and `stress'
   is the engine's 0/1/2. A syllabic consonant is given the map's schwa in
   front of it, so that it has a vowel to carry the syllable. */
void evv_word_add(EvvWord *w, const EvvMap *map, char phones[][EVV_PHONE_LEN], int n, int syllabic,
                  int is_vowel, int stress);

/* Appends the word to out as `[...] with syllable marks and stress digits.
   Returns the number of bytes written, or 0 for a word with nothing in it. */
size_t evv_word_annotate(const EvvWord *w, const EvvMap *map, char *out, size_t room);

#ifdef __cplusplus
}
#endif

#endif
