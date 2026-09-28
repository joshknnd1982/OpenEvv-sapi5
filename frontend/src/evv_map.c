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
#include "evv_map.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void copy_phone(char *dst, const char *src)
{
	strncpy(dst, src, EVV_PHONE_LEN - 1);
	dst[EVV_PHONE_LEN - 1] = 0;
}

static char *next_word(char **p)
{
	char *s = *p;
	while (*s == ' ' || *s == '\t')
		s++;
	if (*s == 0)
		return NULL;
	char *w = s;
	while (*s && *s != ' ' && *s != '\t')
		s++;
	if (*s)
		*s++ = 0;
	*p = s;
	return w;
}

static int add_list(char list[][EVV_PHONE_LEN], int *n, int max, char *rest)
{
	char *w;
	while ((w = next_word(&rest)) != NULL) {
		if (*n >= max)
			return -1;
		copy_phone(list[(*n)++], w);
	}
	return 0;
}

int evv_map_load(EvvMap *map, const char *path, char *err, size_t errlen)
{
	memset(map, 0, sizeof(*map));
	map->secondary = '2';
	FILE *f = fopen(path, "rb");
	if (!f) {
		snprintf(err, errlen, "cannot open %s", path);
		return -1;
	}
	char line[1024];
	int lineno = 0;
	while (fgets(line, sizeof(line), f)) {
		lineno++;
		char *p = line;
		if (lineno == 1 && (unsigned char)p[0] == 0xef && (unsigned char)p[1] == 0xbb && (unsigned char)p[2] == 0xbf)
			p += 3;
		char *hash = strchr(p, '#');
		if (hash)
			*hash = 0;
		size_t len = strlen(p);
		while (len && (p[len - 1] == '\n' || p[len - 1] == '\r' || p[len - 1] == ' ' || p[len - 1] == '\t'))
			p[--len] = 0;
		char *rest = p;
		char *key = next_word(&rest);
		if (!key)
			continue;
		if (strcmp(key, "template") == 0) {
			char *w = next_word(&rest);
			if (w)
				snprintf(map->tmpl, sizeof(map->tmpl), "%s", w);
			continue;
		}
		if (strcmp(key, "style") == 0) {
			char *w = next_word(&rest);
			map->french = w && strcmp(w, "french") == 0;
			continue;
		}
		if (strcmp(key, "vowels") == 0) {
			if (add_list(map->vowels, &map->n_vowels, 64, rest) < 0)
				goto too_many;
			continue;
		}
		if (strcmp(key, "glides") == 0) {
			if (add_list(map->glides, &map->n_glides, 32, rest) < 0)
				goto too_many;
			continue;
		}
		if (strcmp(key, "secondary") == 0) {
			char *w = next_word(&rest);
			if (w && w[0] >= '0' && w[0] <= '2')
				map->secondary = w[0];
			continue;
		}
		if (strcmp(key, "schwa") == 0) {
			char *w = next_word(&rest);
			if (w)
				copy_phone(map->schwa, w);
			continue;
		}
		if (map->n_entries == map->cap_entries) {
			map->cap_entries = map->cap_entries ? map->cap_entries * 2 : 256;
			EvvMapEntry *e = (EvvMapEntry *)realloc(map->entries, sizeof(EvvMapEntry) * map->cap_entries);
			if (!e) {
				fclose(f);
				snprintf(err, errlen, "out of memory");
				return -1;
			}
			map->entries = e;
		}
		EvvMapEntry *e = &map->entries[map->n_entries];
		memset(e, 0, sizeof(*e));
		if (strlen(key) >= sizeof(e->key)) {
			snprintf(err, errlen, "%s:%d: key too long", path, lineno);
			fclose(f);
			return -1;
		}
		strcpy(e->key, key);
		char *w;
		while ((w = next_word(&rest)) != NULL) {
			if (strcmp(w, "-") == 0)
				continue; /* says nothing */
			if (e->n >= EVV_MAX_PHONES) {
				snprintf(err, errlen, "%s:%d: too many phones", path, lineno);
				fclose(f);
				return -1;
			}
			copy_phone(e->phones[e->n++], w);
		}
		int kl = (int)strlen(e->key);
		if (kl > map->max_key_len)
			map->max_key_len = kl;
		map->n_entries++;
	}
	fclose(f);
	if (map->n_vowels == 0) {
		snprintf(err, errlen, "%s names no vowels", path);
		return -1;
	}
	return 0;
too_many:
	fclose(f);
	snprintf(err, errlen, "%s:%d: list too long", path, lineno);
	return -1;
}

void evv_map_free(EvvMap *map)
{
	free(map->entries);
	memset(map, 0, sizeof(*map));
}

static int in_list(char list[][EVV_PHONE_LEN], int n, const char *phone)
{
	for (int i = 0; i < n; i++)
		if (strcmp(list[i], phone) == 0)
			return 1;
	return 0;
}

int evv_map_is_vowel(const EvvMap *map, const char *phone)
{
	return in_list((char(*)[EVV_PHONE_LEN])map->vowels, map->n_vowels, phone);
}

int evv_map_is_glide(const EvvMap *map, const char *phone)
{
	return in_list((char(*)[EVV_PHONE_LEN])map->glides, map->n_glides, phone);
}

static const EvvMapEntry *find(const EvvMap *map, const char *key, size_t len)
{
	for (int i = 0; i < map->n_entries; i++) {
		const EvvMapEntry *e = &map->entries[i];
		if (strlen(e->key) == len && memcmp(e->key, key, len) == 0)
			return e;
	}
	return NULL;
}

static int emit(const EvvMapEntry *e, char out[][EVV_PHONE_LEN], int n, int max_out)
{
	for (int i = 0; i < e->n && n < max_out; i++)
		copy_phone(out[n++], e->phones[i]);
	return n;
}

static int utf8_len(unsigned char c)
{
	if (c < 0x80) return 1;
	if ((c & 0xe0) == 0xc0) return 2;
	if ((c & 0xf0) == 0xe0) return 3;
	if ((c & 0xf8) == 0xf0) return 4;
	return 1;
}

int evv_map_lookup(const EvvMap *map, const char *table, const char *mnemonic, const char *ipa,
                   char out[][EVV_PHONE_LEN], int max_out)
{
	const EvvMapEntry *e;
	if (table && mnemonic && *mnemonic) {
		char key[64];
		snprintf(key, sizeof(key), "@%s:%s", table, mnemonic);
		if ((e = find(map, key, strlen(key))) != NULL)
			return emit(e, out, 0, max_out);
	}
	if (!ipa || !*ipa)
		return 0;
	if ((e = find(map, ipa, strlen(ipa))) != NULL)
		return emit(e, out, 0, max_out);
	/* taken apart from the left, longest key first */
	int n = 0;
	const char *p = ipa;
	while (*p && n < max_out) {
		size_t left = strlen(p);
		size_t try_len = left < (size_t)map->max_key_len ? left : (size_t)map->max_key_len;
		const EvvMapEntry *best = NULL;
		for (size_t l = try_len; l > 0; l--) {
			if ((e = find(map, p, l)) != NULL) {
				best = e;
				break;
			}
		}
		if (best) {
			n = emit(best, out, n, max_out);
			p += strlen(best->key);
		} else {
			p += utf8_len((unsigned char)*p);
		}
	}
	return n;
}

void evv_word_clear(EvvWord *w)
{
	w->n = 0;
	w->has_nucleus = 0;
}

static void push(EvvWord *w, const char *phone, int nucleus, int stress)
{
	if (w->n >= EVV_WORD_MAX)
		return;
	EvvPhone *p = &w->ph[w->n++];
	copy_phone(p->phone, phone);
	p->nucleus = nucleus;
	p->stress = stress;
	if (nucleus)
		w->has_nucleus = 1;
}

void evv_word_add(EvvWord *w, const EvvMap *map, char phones[][EVV_PHONE_LEN], int n, int syllabic,
                  int is_vowel, int stress)
{
	if (!syllabic) {
		for (int i = 0; i < n; i++)
			push(w, phones[i], 0, 0);
		return;
	}
	int first_vowel = -1;
	if (is_vowel) {
		for (int i = 0; i < n; i++)
			if (evv_map_is_vowel(map, phones[i])) {
				first_vowel = i;
				break;
			}
	}
	if (first_vowel < 0) {
		/* a syllabic consonant, or a vowel the template can only say as a
		   consonant: the syllable is carried by the map's schwa */
		if (map->schwa[0])
			push(w, map->schwa, 1, stress);
		for (int i = 0; i < n; i++)
			push(w, phones[i], 0, 0);
		return;
	}
	for (int i = 0; i < n; i++)
		push(w, phones[i], i == first_vowel, i == first_vowel ? stress : 0);
}

static size_t put(char *out, size_t room, size_t at, const char *s)
{
	size_t l = strlen(s);
	if (at + l + 1 > room)
		return at;
	memcpy(out + at, s, l);
	out[at + l] = 0;
	return at + l;
}

static size_t put_phone(char *out, size_t room, size_t at, const char *phone)
{
	if (strlen(phone) > 1) {
		at = put(out, room, at, "'");
		at = put(out, room, at, phone);
		return put(out, room, at, "'");
	}
	return put(out, room, at, phone);
}

size_t evv_word_annotate(const EvvWord *w, const EvvMap *map, char *out, size_t room)
{
	if (w->n == 0 || !w->has_nucleus)
		return 0;
	int nuc[EVV_WORD_MAX];
	int nn = 0;
	for (int i = 0; i < w->n; i++)
		if (w->ph[i].nucleus)
			nuc[nn++] = i;
	/* where each syllable starts */
	int start[EVV_WORD_MAX];
	start[0] = 0;
	for (int k = 1; k < nn; k++) {
		int a = nuc[k - 1] + 1, b = nuc[k] - 1;
		int s;
		if (b < a) {
			s = nuc[k];
		} else if (a == b) {
			s = a;
		} else {
			s = b;
			/* an obstruent and a liquid or glide begin a syllable together */
			if (evv_map_is_glide(map, w->ph[b].phone) && !evv_map_is_glide(map, w->ph[b - 1].phone) &&
			    !evv_map_is_vowel(map, w->ph[b - 1].phone))
				s = b - 1;
		}
		/* a vowel that is not a nucleus stays with the syllable before it */
		for (int i = a; i <= b; i++)
			if (evv_map_is_vowel(map, w->ph[i].phone) && s <= i)
				s = i + 1;
		if (s > nuc[k])
			s = nuc[k];
		start[k] = s;
	}
	size_t at = 0;
	at = put(out, room, at, "`[");
	int primaries = 0;
	for (int k = 0; k < nn; k++) {
		int end = k + 1 < nn ? start[k + 1] : w->n;
		int st = w->ph[nuc[k]].stress;
		char digit[2] = {st == 2 ? map->secondary : (char)('0' + st), 0};
		/* One primary stress to a word. eSpeak NG gives a number's words, or
		   a compound's parts, as one word with a stress on each; a module
		   expects one, and the Italian one loops for ever on `[.1a.1a]. So a
		   second stress begins a word of its own. */
		if (st == 1 && primaries++ > 0)
			at = put(out, room, at, "] `[");
		at = put(out, room, at, ".");
		if (!map->french)
			at = put(out, room, at, digit);
		for (int i = start[k]; i < end; i++) {
			if (map->french && i == nuc[k])
				at = put(out, room, at, digit);
			at = put_phone(out, room, at, w->ph[i].phone);
		}
	}
	at = put(out, room, at, "]");
	return at;
}
