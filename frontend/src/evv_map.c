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

#include <windows.h>

static void copy_name(char *dst, const char *src, size_t room)
{
	strncpy(dst, src, room - 1);
	dst[room - 1] = 0;
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

/* A comment begins at a `#' that starts a word. One inside a word is part of
   the word: eSpeak NG names an aspirated t `t#', and a map that lost
   everything after that `#' would say nothing for the plain t as well. */
static void strip_comment(char *line)
{
	char *p = line;
	int at_start = 1;
	for (; *p; p++) {
		if (*p == '#' && at_start) {
			*p = 0;
			return;
		}
		at_start = (*p == ' ' || *p == '\t');
	}
}

static int add_list(char list[][EVV_PHONE_LEN], int *n, int max, char *rest)
{
	char *w;
	while ((w = next_word(&rest)) != NULL) {
		if (*n >= max)
			return -1;
		copy_name(list[(*n)++], w, EVV_PHONE_LEN);
	}
	return 0;
}

/* What the text is to begin with is put together as the map is read. */
typedef struct {
	char *text;
	size_t len, cap;
} Buffer;

static int buffer_put(Buffer *b, const char *s)
{
	size_t l = strlen(s);
	if (b->len + l + 1 > b->cap) {
		size_t cap = b->cap ? b->cap * 2 : 1024;
		while (cap < b->len + l + 1)
			cap *= 2;
		char *t = (char *)realloc(b->text, cap);
		if (!t)
			return -1;
		b->text = t;
		b->cap = cap;
	}
	memcpy(b->text + b->len, s, l + 1);
	b->len += l;
	return 0;
}

static int buffer_group(Buffer *b, const char *letter, const char *rest)
{
	/* one space between words, none at either end */
	if (buffer_put(b, "{") || buffer_put(b, letter))
		return -1;
	char copy[1024];
	copy_name(copy, rest, sizeof(copy));
	char *p = copy, *w;
	while ((w = next_word(&p)) != NULL) {
		if (strchr(w, '{') || strchr(w, '}'))
			continue;
		if (buffer_put(b, " ") || buffer_put(b, w))
			return -1;
	}
	return buffer_put(b, "}");
}

static int add_defined(EvvDefined **list, int *n, int *cap, const char *id, const char *group)
{
	if (*n == *cap) {
		int c = *cap ? *cap * 2 : 64;
		EvvDefined *t = (EvvDefined *)realloc(*list, (size_t)c * sizeof(EvvDefined));
		if (!t)
			return -1;
		*list = t;
		*cap = c;
	}
	EvvDefined *d = &(*list)[(*n)++];
	memset(d, 0, sizeof(*d));
	copy_name(d->id, id, EVV_ID_LEN);
	d->group = (char *)malloc(strlen(group) + 1);
	if (!d->group)
		return -1;
	strcpy(d->group, group);
	return 0;
}

/* A `sound' or a `tone' line, kept as the group it becomes under the name it
   defines. */
static int define(EvvDefined **list, int *n, int *cap, const char *letter, const char *rest)
{
	Buffer b = {0};
	char copy[1024];
	copy_name(copy, rest, sizeof(copy));
	char *q = copy;
	char *id = next_word(&q);
	if (!id)
		return 0;
	if (buffer_group(&b, letter, rest)) {
		free(b.text);
		return -1;
	}
	int bad = add_defined(list, n, cap, id, b.text);
	free(b.text);
	return bad;
}

static void use(EvvDefined *list, int n, const char *id)
{
	for (int i = 0; i < n; i++)
		if (strcmp(list[i].id, id) == 0) {
			list[i].used = 1;
			return;
		}
}

char *evv_map_begin(EvvMap *map, size_t *len)
{
	Buffer b = {0};
	int bad = 0;
	*len = 0;
	if (!map->accent || !map->header)
		return NULL;
	bad |= buffer_put(&b, map->header);
	for (int i = 0; i < map->n_sounds; i++)
		if (map->sounds[i].used) {
			bad |= buffer_put(&b, map->sounds[i].group);
			map->sounds[i].used = 0;
		}
	for (int i = 0; i < map->n_tone_defs; i++)
		if (map->tone_defs[i].used) {
			bad |= buffer_put(&b, map->tone_defs[i].group);
			map->tone_defs[i].used = 0;
		}
	if (bad) {
		free(b.text);
		return NULL;
	}
	*len = b.len;
	return b.text;
}

static int add_tone_id(EvvMap *map, const char *id)
{
	if (map->n_tone_ids == map->cap_tone_ids) {
		int cap = map->cap_tone_ids ? map->cap_tone_ids * 2 : 16;
		void *t = realloc(map->tone_ids, (size_t)cap * EVV_ID_LEN);
		if (!t)
			return -1;
		map->tone_ids = (char(*)[EVV_ID_LEN])t;
		map->cap_tone_ids = cap;
	}
	copy_name(map->tone_ids[map->n_tone_ids++], id, EVV_ID_LEN);
	return 0;
}

static int add_tone_name(EvvMap *map, const char *from, const char *to)
{
	if (map->n_tones == map->cap_tones) {
		int cap = map->cap_tones ? map->cap_tones * 2 : 16;
		EvvToneName *t = (EvvToneName *)realloc(map->tones, (size_t)cap * sizeof(EvvToneName));
		if (!t)
			return -1;
		map->tones = t;
		map->cap_tones = cap;
	}
	copy_name(map->tones[map->n_tones].from, from, EVV_ID_LEN);
	copy_name(map->tones[map->n_tones].to, to, EVV_ID_LEN);
	map->n_tones++;
	return 0;
}

static void read_phone(EvvMapPhone *ph, char *w)
{
	memset(ph, 0, sizeof(*ph));
	if ((w[0] == '<' || w[0] == '>') && w[1]) {
		ph->made = w[0];
		w++;
	}
	char *eq = strchr(w, '=');
	if (eq && eq != w) {
		*eq = 0;
		copy_name(ph->sound, eq + 1, EVV_ID_LEN);
	}
	copy_name(ph->name, w, EVV_PHONE_LEN);
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
	Buffer accent = {0}, rest_of = {0};
	char line[1024];
	int lineno = 0;
	int failed = 0;
	while (fgets(line, sizeof(line), f)) {
		lineno++;
		char *p = line;
		if (lineno == 1 && (unsigned char)p[0] == 0xef && (unsigned char)p[1] == 0xbb && (unsigned char)p[2] == 0xbf)
			p += 3;
		strip_comment(p);
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
				copy_name(map->schwa, w, EVV_PHONE_LEN);
			continue;
		}
		if (strcmp(key, "words") == 0) {
			char *w = next_word(&rest);
			map->apart = w && strcmp(w, "apart") == 0;
			continue;
		}
		if (strcmp(key, "cluster") == 0) {
			char *x = next_word(&rest);
			char *y = next_word(&rest);
			if (x && y && map->n_clusters < 16) {
				copy_name(map->clusters[map->n_clusters][0], x, EVV_PHONE_LEN);
				copy_name(map->clusters[map->n_clusters][1], y, EVV_PHONE_LEN);
				map->n_clusters++;
			}
			continue;
		}
		if (strcmp(key, "onset") == 0) {
			char *w = next_word(&rest);
			if (w && w[0] >= '1' && w[0] <= '3')
				map->onset = w[0] - '0';
			continue;
		}
		if (strcmp(key, "accent") == 0) {
			/* what kind of language it is: the first thing the engine is told */
			char all[1024];
			snprintf(all, sizeof(all), "v=1 %s", rest);
			accent.len = 0;
			if (accent.text)
				accent.text[0] = 0;
			failed |= buffer_group(&accent, "A", all);
			map->accent = 1;
			continue;
		}
		if (strcmp(key, "sound") == 0) {
			failed |= define(&map->sounds, &map->n_sounds, &map->cap_sounds, "D", rest);
			map->accent = 1;
			continue;
		}
		if (strcmp(key, "tone") == 0) {
			char copy[1024];
			copy_name(copy, rest, sizeof(copy));
			char *q = copy;
			char *id = next_word(&q);
			if (id)
				failed |= add_tone_id(map, id);
			failed |= define(&map->tone_defs, &map->n_tone_defs, &map->cap_tone_defs, "T", rest);
			map->accent = 1;
			continue;
		}
		if (strcmp(key, "whwords") == 0) {
			char *w = next_word(&rest);
			if (w && strcmp(w, "any") == 0)
				map->ask_where = 2;
			else if (w && strcmp(w, "first") == 0)
				map->ask_where = map->ask_where ? map->ask_where : 1;
			else if (w)
				rest = w; /* no place named: the word is a question word */
			while ((w = next_word(&rest)) != NULL) {
				if (map->n_ask == map->cap_ask) {
					int cap = map->cap_ask ? map->cap_ask * 2 : 32;
					void *t = realloc(map->ask, (size_t)cap * EVV_ASK_LEN);
					if (!t) {
						failed = 1;
						break;
					}
					map->ask = (char(*)[EVV_ASK_LEN])t;
					map->cap_ask = cap;
				}
				copy_name(map->ask[map->n_ask++], w, EVV_ASK_LEN);
			}
			if (!map->ask_where)
				map->ask_where = 1;
			continue;
		}
		if (strcmp(key, "weaktones") == 0) {
			char *w;
			while ((w = next_word(&rest)) != NULL && map->n_weak_tones < 16)
				copy_name(map->weak_tones[map->n_weak_tones++], w, EVV_ID_LEN);
			continue;
		}
		if (strcmp(key, "tonename") == 0) {
			char *from = next_word(&rest);
			char *to = next_word(&rest);
			if (from && to)
				failed |= add_tone_name(map, from, to);
			continue;
		}
		if (strcmp(key, "says") == 0) {
			failed |= buffer_group(&rest_of, "X", rest);
			continue;
		}
		if (strcmp(key, "may") == 0) {
			failed |= buffer_group(&rest_of, "S", rest);
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
			read_phone(&e->phones[e->n++], w);
		}
		int kl = (int)strlen(e->key);
		if (kl > map->max_key_len)
			map->max_key_len = kl;
		map->n_entries++;
	}
	fclose(f);
	if (failed) {
		free(accent.text);
		free(rest_of.text);
		snprintf(err, errlen, "out of memory");
		return -1;
	}
	if (map->n_vowels == 0) {
		free(accent.text);
		free(rest_of.text);
		snprintf(err, errlen, "%s names no vowels", path);
		return -1;
	}
	if (map->accent) {
		Buffer h = {0};
		int bad = buffer_put(&h, accent.text ? accent.text : "{A v=1}");
		if (rest_of.text)
			bad |= buffer_put(&h, rest_of.text);
		if (bad) {
			free(h.text);
			free(accent.text);
			free(rest_of.text);
			snprintf(err, errlen, "out of memory");
			return -1;
		}
		map->header = h.text;
		map->header_len = h.len;
	}
	free(accent.text);
	free(rest_of.text);
	return 0;
too_many:
	fclose(f);
	free(accent.text);
	free(rest_of.text);
	snprintf(err, errlen, "%s:%d: list too long", path, lineno);
	return -1;
}

void evv_map_free(EvvMap *map)
{
	for (int i = 0; i < map->n_sounds; i++)
		free(map->sounds[i].group);
	for (int i = 0; i < map->n_tone_defs; i++)
		free(map->tone_defs[i].group);
	free(map->sounds);
	free(map->tone_defs);
	free(map->ask);
	free(map->entries);
	free(map->header);
	free(map->tones);
	free(map->tone_ids);
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

const char *evv_map_tone(const EvvMap *map, const char *espeak_name)
{
	if (!espeak_name || !*espeak_name)
		return NULL;
	for (int i = 0; i < map->n_tones; i++)
		if (strcmp(map->tones[i].from, espeak_name) == 0)
			return map->tones[i].to;
	for (int i = 0; i < map->n_tone_ids; i++)
		if (strcmp(map->tone_ids[i], espeak_name) == 0)
			return map->tone_ids[i];
	return NULL;
}

static int same_word(const char *a, size_t na, const char *b, size_t nb)
{
	wchar_t wa[64], wb[64];
	int la = MultiByteToWideChar(CP_UTF8, 0, a, (int)na, wa, 64);
	int lb = MultiByteToWideChar(CP_UTF8, 0, b, (int)nb, wb, 64);
	if (la <= 0 || lb <= 0)
		return 0;
	return CompareStringOrdinal(wa, la, wb, lb, TRUE) == CSTR_EQUAL;
}

int evv_map_asks(const EvvMap *map, const char *word, size_t n, int first)
{
	if (n == 0 || n >= EVV_ASK_LEN)
		return 0;
	for (int i = 0; i < map->n_ask; i++) {
		const char *w = map->ask[i];
		if (w[0] == '~') {
			if (first)
				continue;
			w++;
		}
		if (same_word(w, strlen(w), word, n))
			return 1;
	}
	return 0;
}

int evv_map_tone_is_weak(const EvvMap *map, const char *tone)
{
	if (!tone)
		return 0;
	for (int i = 0; i < map->n_weak_tones; i++)
		if (strcmp(map->weak_tones[i], tone) == 0)
			return 1;
	return 0;
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

static int emit(const EvvMapEntry *e, EvvMapPhone *out, int n, int max_out)
{
	for (int i = 0; i < e->n && n < max_out; i++)
		out[n++] = e->phones[i];
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
                   EvvMapPhone *out, int max_out)
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

static EvvPhone *push(EvvWord *w, const char *phone, const char *sound, char made, int nucleus, int stress)
{
	if (w->n >= EVV_WORD_MAX)
		return NULL;
	EvvPhone *p = &w->ph[w->n++];
	memset(p, 0, sizeof(*p));
	copy_name(p->phone, phone, EVV_PHONE_LEN);
	if (sound)
		copy_name(p->sound, sound, EVV_ID_LEN);
	p->made = made;
	p->nucleus = nucleus;
	p->stress = stress;
	if (nucleus)
		w->has_nucleus = 1;
	return p;
}

void evv_word_add(EvvWord *w, const EvvMap *map, const EvvMapPhone *phones, int n, int syllabic,
                  int is_vowel, int stress, const char *tone)
{
	if (!syllabic) {
		for (int i = 0; i < n; i++)
			push(w, phones[i].name, phones[i].sound, phones[i].made, 0, 0);
		return;
	}
	int first_vowel = -1;
	if (is_vowel) {
		for (int i = 0; i < n; i++)
			if (!phones[i].made && evv_map_is_vowel(map, phones[i].name)) {
				first_vowel = i;
				break;
			}
	}
	if (first_vowel < 0) {
		/* a syllabic consonant, or a vowel the template can only say as a
		   consonant: the syllable is carried by the map's schwa */
		if (map->schwa[0]) {
			EvvPhone *p = push(w, map->schwa, NULL, 0, 1, stress);
			if (p && tone)
				copy_name(p->tone, tone, EVV_ID_LEN);
		}
		for (int i = 0; i < n; i++)
			push(w, phones[i].name, phones[i].sound, phones[i].made, 0, 0);
		return;
	}
	for (int i = 0; i < n; i++) {
		EvvPhone *p = push(w, phones[i].name, phones[i].sound, phones[i].made, i == first_vowel,
		                   i == first_vowel ? stress : 0);
		if (p && i == first_vowel && tone)
			copy_name(p->tone, tone, EVV_ID_LEN);
	}
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

/* What one phone was meant to be, as the markup writes it. */
static size_t put_meant(const EvvMap *map, char *out, size_t room, size_t at, const EvvPhone *p)
{
	/* the text now uses the sound and the tone, and is to begin by saying
	   what they are */
	if (p->sound[0])
		use(map->sounds, map->n_sounds, p->sound);
	if (p->nucleus && !p->made && p->tone[0])
		use(map->tone_defs, map->n_tone_defs, p->tone);
	at = put(out, room, at, " ");
	if (p->made) {
		char m[2] = {p->made, 0};
		at = put(out, room, at, m);
	}
	at = put(out, room, at, p->phone);
	if (p->sound[0]) {
		at = put(out, room, at, "=");
		at = put(out, room, at, p->sound);
	}
	if (p->nucleus && !p->made) {
		at = put(out, room, at, "^");
		at = put(out, room, at, p->tone[0] ? p->tone : "-");
	}
	return at;
}

static size_t annotate(const EvvWord *w, const EvvMap *map, char *out, size_t room);

/* A sound the engine makes for itself -- an h, a glottal stop -- is made out
   of the vowel it stands beside: the start of the vowel after it, or the end
   of the vowel before it where none follows. The map says only that the
   sound is made; which of the two it is depends on the word, and is settled
   here. */
size_t evv_word_annotate(const EvvWord *w, const EvvMap *map, char *out, size_t room)
{
	static EvvWord placed;
	int any = 0;
	for (int i = 0; i < w->n; i++)
		if (w->ph[i].made)
			any = 1;
	if (!any)
		return annotate(w, map, out, room);
	placed = *w;
	for (int i = 0; i < placed.n; i++) {
		if (!w->ph[i].made)
			continue;
		int next = i + 1, prev = i - 1;
		while (next < w->n && w->ph[next].made)
			next++;
		while (prev >= 0 && w->ph[prev].made)
			prev--;
		int vowel_after = next < w->n && evv_map_is_vowel(map, w->ph[next].phone);
		int vowel_before = prev >= 0 && evv_map_is_vowel(map, w->ph[prev].phone);
		if (vowel_after)
			placed.ph[i].made = '<';
		else if (vowel_before)
			placed.ph[i].made = '>';
		else if (next < w->n)
			placed.ph[i].made = '<';
		else
			placed.ph[i].made = '>';
	}
	return annotate(&placed, map, out, room);
}

static size_t annotate(const EvvWord *w, const EvvMap *map, char *out, size_t room)
{
	if (w->n == 0 || !w->has_nucleus)
		return 0;
	/* The phones the annotation carries, which is all of them but the
	   sounds the engine makes for itself. `real' says which phone of the
	   word each of them is. */
	int real[EVV_WORD_MAX];
	int nr = 0;
	for (int i = 0; i < w->n; i++)
		if (!w->ph[i].made)
			real[nr++] = i;
	int nuc[EVV_WORD_MAX];
	int nn = 0;
	for (int r = 0; r < nr; r++)
		if (w->ph[real[r]].nucleus)
			nuc[nn++] = r;
	if (nn == 0)
		return 0;
	/* where each syllable starts, counted in the phones the annotation carries */
	int start[EVV_WORD_MAX];
	start[0] = 0;
	for (int k = 1; k < nn; k++) {
		int a = nuc[k - 1] + 1, b = nuc[k] - 1;
		int s;
		if (b < a) {
			s = nuc[k];
		} else if (a == b) {
			s = a;
		} else if (map->apart) {
			/* A language of one-syllable words: a syllable begins with one
			   consonant, or with a consonant and a glide, and whatever
			   stands before that ends the syllable before. */
			s = b;
			if (map->onset != 1 && evv_map_is_glide(map, w->ph[real[b]].phone))
				s = b - 1;
			for (int c = 0; c < map->n_clusters; c++)
				if (strcmp(map->clusters[c][0], w->ph[real[b - 1]].phone) == 0 &&
				    strcmp(map->clusters[c][1], w->ph[real[b]].phone) == 0)
					s = b - 1;
		} else {
			s = b;
			/* an obstruent and a liquid or glide begin a syllable together */
			if (evv_map_is_glide(map, w->ph[real[b]].phone) && !evv_map_is_glide(map, w->ph[real[b - 1]].phone) &&
			    !evv_map_is_vowel(map, w->ph[real[b - 1]].phone))
				s = b - 1;
		}
		/* a vowel that is not a nucleus stays with the syllable before it */
		for (int i = a; i <= b; i++)
			if (evv_map_is_vowel(map, w->ph[real[i]].phone) && s <= i)
				s = i + 1;
		if (s > nuc[k])
			s = nuc[k];
		start[k] = s;
	}
	/* One primary stress to a word. eSpeak NG gives a number's words, or a
	   compound's parts, as one word with a stress on each; a module expects
	   one, and the Italian one loops for ever on `[.1a.1a]. So a second
	   stress begins a word of its own, and where every syllable carries a
	   tone every syllable does. Which syllable begins which annotation is
	   settled first, since the markup in front of an annotation has to say
	   all of it. */
	int piece[EVV_WORD_MAX];
	int primaries = 0, pieces = 0;
	for (int k = 0; k < nn; k++) {
		int st = w->ph[real[nuc[k]]].stress;
		int begins = k == 0;
		if (map->apart && k > 0)
			begins = 1;
		if (st == 1 && primaries++ > 0)
			begins = 1;
		if (begins)
			pieces++;
		piece[k] = pieces - 1;
	}
	size_t at = 0;
	for (int k = 0; k < nn; k++) {
		int end = k + 1 < nn ? start[k + 1] : nr;
		int st = w->ph[real[nuc[k]]].stress;
		int first_of_piece = k == 0 || piece[k] != piece[k - 1];
		char digit[2] = {st == 2 ? map->secondary : (char)('0' + st), 0};
		if (first_of_piece) {
			if (k > 0)
				at = put(out, room, at, "] ");
			if (map->accent) {
				/* what this annotation was meant to be */
				at = put(out, room, at, "{W");
				for (int j = k; j < nn && piece[j] == piece[k]; j++) {
					int jend = j + 1 < nn ? start[j + 1] : nr;
					int jst = w->ph[real[nuc[j]]].stress;
					char d[4] = {' ', '.', jst == 2 ? map->secondary : (char)('0' + jst), 0};
					at = put(out, room, at, d);
					/* the phones of the syllable, and the sounds made
					   beside them: those written before a syllable's first
					   phone belong to it, and those after the word's last
					   phone to the last syllable */
					int from = j == 0 ? 0 : real[start[j]];
					int upto = jend < nr ? real[jend] : w->n;
					if (j > 0) {
						/* made sounds written between the syllable before
						   and this one: `<' ones are this syllable's */
						int back = real[start[j]];
						while (back > 0 && w->ph[back - 1].made == '<')
							back--;
						from = back;
					}
					if (jend < nr) {
						int back = real[jend];
						while (back > from && w->ph[back - 1].made == '<')
							back--;
						upto = back;
					}
					for (int i = from; i < upto; i++)
						at = put_meant(map, out, room, at, &w->ph[i]);
				}
				at = put(out, room, at, "}");
			}
			at = put(out, room, at, "`[");
		}
		at = put(out, room, at, ".");
		if (!map->french)
			at = put(out, room, at, digit);
		for (int i = start[k]; i < end; i++) {
			if (map->french && i == nuc[k])
				at = put(out, room, at, digit);
			at = put_phone(out, room, at, w->ph[real[i]].phone);
		}
	}
	at = put(out, room, at, "]");
	return at;
}
