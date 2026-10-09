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
#include <math.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <windows.h>

/* eSpeak NG's compat/stdio.h makes snprintf MSVC's _snprintf, which leaves a
   string it cuts unterminated and returns -1. The C99 one (MSVC 2015 and
   later) terminates it and returns the length wanted, which the checks for a
   cut here rely on. Only a cut string is said differently, and no present
   pack has one (the R15 review of Phase 3A). */
#ifdef snprintf
#undef snprintf
#endif

/* ---- diagnostics ---------------------------------------------------------- */

typedef struct {
	int level;
	char kind[24];
	char detail[200];
	int count;
} Diag;

#define MAX_DIAGS 256
static Diag g_diags[MAX_DIAGS];
static int g_n_diags, g_diags_over, g_losses;
int evv_diag_line, evv_diag_quiet;

void evv_diag(int level, const char *kind, const char *fmt, ...)
{
	char detail[200];
	va_list ap;
	if (evv_diag_quiet)
		return;
	va_start(ap, fmt);
	vsnprintf(detail, sizeof(detail), fmt, ap);
	va_end(ap);
	if (evv_diag_line > 0) {
		char at[200];
		snprintf(at, sizeof(at), "map line %d: %s", evv_diag_line, detail);
		memcpy(detail, at, sizeof(detail));
	}
	if (level == EVV_DIAG_LOSS)
		g_losses++;
	for (int i = 0; i < g_n_diags; i++)
		if (g_diags[i].level == level && strcmp(g_diags[i].kind, kind) == 0 &&
		    strcmp(g_diags[i].detail, detail) == 0) {
			g_diags[i].count++;
			return;
		}
	if (g_n_diags == MAX_DIAGS) {
		g_diags_over++;
		return;
	}
	Diag *d = &g_diags[g_n_diags++];
	d->level = level;
	snprintf(d->kind, sizeof(d->kind), "%s", kind);
	memcpy(d->detail, detail, sizeof(d->detail));
	d->count = 1;
}

void evv_diag_clear(void)
{
	g_n_diags = g_diags_over = g_losses = 0;
}

int evv_diag_losses(void)
{
	return g_losses;
}

char *evv_diag_text(size_t *len)
{
	size_t cap = (size_t)g_n_diags * (sizeof(Diag) + 32) + 128;
	char *s = (char *)malloc(cap);
	size_t at = 0;
	*len = 0;
	if (!s)
		return NULL;
	s[0] = 0;
	for (int i = 0; i < g_n_diags; i++) {
		const Diag *d = &g_diags[i];
		at += (size_t)snprintf(s + at, cap - at, "%s\t%s\t%s\t%d\n", d->level == EVV_DIAG_LOSS ? "loss" : "note",
		                       d->kind, d->detail, d->count);
	}
	if (g_diags_over)
		at += (size_t)snprintf(s + at, cap - at, "loss\tdiagnostics-full\tmore kinds than %d\t%d\n", MAX_DIAGS,
		                       g_diags_over);
	*len = at;
	return s;
}

/* What a name is cut to when it is longer than its room, reported. */
static void copy_name(char *dst, const char *src, size_t room)
{
	strncpy(dst, src, room - 1);
	dst[room - 1] = 0;
}

static void copy_checked(char *dst, const char *src, size_t room, const char *what)
{
	if (strlen(src) >= room)
		evv_diag(EVV_DIAG_LOSS, "map-name-cut", "%s `%s' cut to %d bytes", what, src, (int)room - 1);
	copy_name(dst, src, room);
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
		copy_checked(list[(*n)++], w, EVV_PHONE_LEN, "phone");
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
	char copy[4096];
	copy_checked(copy, rest, sizeof(copy), "line");
	char *p = copy, *w;
	while ((w = next_word(&p)) != NULL) {
		if (strchr(w, '{') || strchr(w, '}')) {
			evv_diag(EVV_DIAG_LOSS, "map-ignored", "word `%s' holds a brace and is left out", w);
			continue;
		}
		if (buffer_put(b, " ") || buffer_put(b, w))
			return -1;
	}
	return buffer_put(b, "}");
}

static int add_defined(EvvDefined **list, int *n, int *cap, const char *id, const char *group)
{
	for (int i = 0; i < *n; i++)
		if (strncmp((*list)[i].id, id, EVV_ID_LEN - 1) == 0) {
			evv_diag(EVV_DIAG_LOSS, "map-id-duplicate", "`%s' is defined again; the first definition is used", id);
			break;
		}
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
	copy_checked(d->id, id, EVV_ID_LEN, "id");
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
	char copy[4096];
	copy_name(copy, rest, sizeof(copy));
	char *q = copy;
	char *id = next_word(&q);
	if (!id) {
		evv_diag(EVV_DIAG_LOSS, "map-ignored", "a %s line with no id", letter[0] == 'D' ? "sound" : "tone");
		return 0;
	}
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
	copy_checked(map->tone_ids[map->n_tone_ids++], id, EVV_ID_LEN, "tone id");
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
	copy_checked(map->tones[map->n_tones].from, from, EVV_ID_LEN, "tone name");
	copy_checked(map->tones[map->n_tones].to, to, EVV_ID_LEN, "tone id");
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
		copy_checked(ph->sound, eq + 1, EVV_ID_LEN, "sound id");
	}
	copy_checked(ph->name, w, EVV_PHONE_LEN, "phone");
}

/* A key one letter away from a keyword (`vowel' for `vowels') is read as a
   phoneme, as the format has always done; it is reported. Only words of four
   ASCII letters or more are held to it: no phoneme is written so. */
static int one_edit(const char *a, const char *b)
{
	size_t la = strlen(a), lb = strlen(b);
	if (la == lb) {
		int d = 0;
		for (size_t i = 0; i < la; i++)
			d += a[i] != b[i];
		return d == 1;
	}
	if (la + 1 != lb && lb + 1 != la)
		return 0;
	const char *s = la < lb ? a : b, *l = la < lb ? b : a;
	size_t i = 0, j = 0;
	int skipped = 0;
	while (i < strlen(s) && j < strlen(l)) {
		if (s[i] == l[j]) {
			i++;
			j++;
		} else if (skipped++) {
			return 0;
		} else {
			j++;
		}
	}
	return 1;
}

static const char *keyword_like(const char *key)
{
	static const char *words[] = {"template", "style", "vowels", "glides", "secondary", "schwa", "words", "cluster",
	                              "onset", "accent", "sound", "tone", "whwords", "weaktones", "tonename", "says",
	                              "version", "weights", "letter", "tonemark", "register", "slope", "syllabic", "after"};
	size_t n = strlen(key);
	if (n < 4)
		return NULL;
	for (size_t i = 0; i < n; i++)
		if (key[i] < 'a' || key[i] > 'z')
			return NULL;
	for (size_t w = 0; w < sizeof(words) / sizeof(words[0]); w++)
		if (strlen(words[w]) >= 4 && one_edit(key, words[w]))
			return words[w];
	return NULL;
}

/* `letter IPA c|v name=value ...' */
static int read_letter(EvvMap *map, char *rest)
{
	static const char *cons[7] = {"stricture", "airstream", "nasal", "lateral", "sibilant", "place2", "voicing"};
	char *ipa = next_word(&rest), *cls = next_word(&rest), *w;
	if (!ipa || !cls) {
		evv_diag(EVV_DIAG_LOSS, "map-ignored", "a letter line needs a letter and a class");
		return 0;
	}
	if (map->n_letters == map->cap_letters) {
		int cap = map->cap_letters ? map->cap_letters * 2 : 128;
		EvvLetter *t = (EvvLetter *)realloc(map->letters, (size_t)cap * sizeof(EvvLetter));
		if (!t)
			return -1;
		map->letters = t;
		map->cap_letters = cap;
	}
	EvvLetter *l = &map->letters[map->n_letters++];
	memset(l, 0, sizeof(*l));
	copy_checked(l->ipa, ipa, sizeof(l->ipa), "letter");
	l->cls = cls[0];
	while ((w = next_word(&rest)) != NULL) {
		char *eq = strchr(w, '=');
		if (!eq)
			continue;
		*eq++ = 0;
		if (strcmp(w, "place") == 0)
			l->place = atoi(eq);
		else if (strcmp(w, "height") == 0)
			l->height = atoi(eq);
		else if (strcmp(w, "backness") == 0)
			l->backness = atoi(eq);
		else if (strcmp(w, "rounding") == 0)
			copy_checked(l->f[0], eq, sizeof(l->f[0]), "feature");
		else if (w[0] == 'f' && w[1] >= '1' && w[1] <= '4' && strcmp(w + 2, "hz") == 0)
			l->hz[w[1] - '1'] = atoi(eq); /* the letter as realised, for a mark that moves towards a target */
		else {
			int k;
			for (k = 0; k < 7 && strcmp(cons[k], w) != 0; k++)
				;
			if (k < 7)
				copy_checked(l->f[k], eq, sizeof(l->f[k]), "feature");
			else
				evv_diag(EVV_DIAG_LOSS, "map-ignored", "letter %s: no feature %s", ipa, w);
		}
	}
	return 0;
}

/* `tonemark MARK LEVELS', `register MARK TENTHS', `slope MARK TENTHS'
   (version 2; DESIGN.md 4.3, C2 and C5) */
static int read_tonemark(EvvMap *map, char kind, char *rest)
{
	char *mark = next_word(&rest), *v = next_word(&rest);
	if (!mark || !v) {
		evv_diag(EVV_DIAG_LOSS, "map-ignored", "a %s line needs a mark and a value",
		         kind == 't' ? "tonemark" : kind == 'r' ? "register" : "slope");
		return 0;
	}
	if (map->n_tonemarks == map->cap_tonemarks) {
		int cap = map->cap_tonemarks ? map->cap_tonemarks * 2 : 32;
		EvvToneMark *t = (EvvToneMark *)realloc(map->tonemarks, (size_t)cap * sizeof(EvvToneMark));
		if (!t)
			return -1;
		map->tonemarks = t;
		map->cap_tonemarks = cap;
	}
	EvvToneMark *m = &map->tonemarks[map->n_tonemarks++];
	memset(m, 0, sizeof(*m));
	copy_checked(m->mark, mark, sizeof(m->mark), "mark");
	m->kind = kind;
	if (kind == 't') {
		for (const char *d = v; *d; d++) {
			if (*d < '1' || *d > '5' || m->n >= 4) {
				evv_diag(EVV_DIAG_LOSS, "map-ignored", "tonemark %s: levels `%s' are not 1 to 5, at most four", mark, v);
				map->n_tonemarks--;
				return 0;
			}
			m->levels[m->n++] = *d - '0';
		}
	} else {
		m->value = atoi(v);
	}
	return 0;
}

const EvvToneMark *evv_map_tonemark(const EvvMap *map, const char *ch, size_t len)
{
	for (int i = 0; i < map->n_tonemarks; i++)
		if (strlen(map->tonemarks[i].mark) == len && memcmp(map->tonemarks[i].mark, ch, len) == 0)
			return &map->tonemarks[i];
	return NULL;
}

/* A tone made for typed IPA: its points spread evenly over the nucleus, in
   tenths of a Chao level, moved by the register and the slope. A contour's
   last level is planned at four fifths of the nucleus, not its end: the
   voice follows the plan through the accent layer's filter, which trails a
   movement by 44 ms where the plan is brought forward by 20, and on a short
   nucleus the last level was never reached (D66). Kept as a tone definition
   like a map's own, and found again by what it says. */
const char *evv_map_ipa_tone(EvvMap *map, const int *levels, int n, int from, int to)
{
	char body[160];
	size_t at = 0;
	int pts = n == 1 ? 2 : n;
	at += (size_t)snprintf(body + at, sizeof(body) - at, "p=");
	for (int i = 0; i < pts && at < sizeof(body); i++) {
		int lv = levels[n == 1 ? 0 : i];
		int along = i * 100 / (pts - 1);
		/* the register and the slope move the point by where it stands in
		   the syllable, not by when it is planned */
		int off = from + (to - from) * along / 100;
		int pos = n > 1 && i == pts - 1 ? 80 : along;
		int v = lv * 10 + off;
		if (v < 0 || v > 60) {
			evv_diag(EVV_DIAG_LOSS, "tone-clamped", "level %d moved by %d tenths is off the voice; held at its edge",
			         lv, off);
			v = v < 0 ? 0 : 60;
		}
		at += (size_t)snprintf(body + at, sizeof(body) - at, "%s%d:%d", i ? "," : "", pos, v);
	}
	char want[200];
	snprintf(want, sizeof(want), " %s}", body);
	for (int i = 0; i < map->n_tone_defs; i++) {
		/* `{T id p=...}': what follows the id */
		const char *g = map->tone_defs[i].group;
		const char *sp = strchr(g, ' ');
		sp = sp ? strchr(sp + 1, ' ') : NULL;
		if (strncmp(map->tone_defs[i].id, "ipa", 3) == 0 && sp && strcmp(sp, want) == 0)
			return map->tone_defs[i].id;
	}
	char line[200];
	char id[EVV_ID_LEN];
	snprintf(id, sizeof(id), "ipa%d", ++map->n_ipa_tones);
	snprintf(line, sizeof(line), "%s %s", id, body);
	if (define(&map->tone_defs, &map->n_tone_defs, &map->cap_tone_defs, "T", line) != 0)
		return NULL;
	evv_diag(EVV_DIAG_NOTE, "tone-made", "%s %s", id, body);
	return map->tone_defs[map->n_tone_defs - 1].id;
}

/* `mod MARK c|v key*value key+value ...'; `premod' the same, for a mark
   written before its letter (extIPA's pre-aspiration ʰp, pre-voicing ˬz) */
static int read_mod(EvvMap *map, char *rest, int pre)
{
	char *mark = next_word(&rest), *cls = next_word(&rest), *w;
	if (!mark || !cls) {
		evv_diag(EVV_DIAG_LOSS, "map-ignored", "a mod line needs a mark and a class");
		return 0;
	}
	if (map->n_mods == map->cap_mods) {
		int cap = map->cap_mods ? map->cap_mods * 2 : 32;
		EvvMod *t = (EvvMod *)realloc(map->mods, (size_t)cap * sizeof(EvvMod));
		if (!t)
			return -1;
		map->mods = t;
		map->cap_mods = cap;
	}
	EvvMod *m = &map->mods[map->n_mods++];
	memset(m, 0, sizeof(*m));
	copy_checked(m->mark, mark, sizeof(m->mark), "mark");
	m->cls = cls[0];
	m->pre = (char)pre;
	while ((w = next_word(&rest)) != NULL) {
		char *op = strpbrk(w, "*+=~");
		if (!op || op == w || m->n >= EVV_MAX_OPS) {
			evv_diag(EVV_DIAG_LOSS, "map-ignored", "mod %s: `%s' is not key*value, key+value or key=value, or one too "
			         "many", mark, w);
			continue;
		}
		EvvOp *o = &m->ops[m->n++];
		o->op = *op;
		*op = 0;
		copy_checked(o->key, w, sizeof(o->key), "key");
		o->v = atof(op + 1);
		if (o->op == '~') {
			/* `f2~1450:50': half of the way towards 1450 Hz */
			char *c = strchr(op + 1, ':');
			o->part = c ? atof(c + 1) : 50.0;
		}
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
	Buffer accent = {0}, rest_of = {0};
	char line[4096];
	int lineno = 0;
	int failed = 0;
	int accents = 0;
	int cut = 0; /* the line before did not end: this is its rest */
	while (fgets(line, sizeof(line), f)) {
		lineno++;
		evv_diag_line = lineno;
		size_t got = strlen(line);
		int ends = got > 0 && line[got - 1] == '\n';
		if (!ends && !feof(f))
			evv_diag(EVV_DIAG_LOSS, "map-line-long", "longer than %d bytes; the rest is read as a line of its own",
			         (int)sizeof(line) - 1);
		if (cut)
			lineno--; /* the same line of the file, continued */
		cut = !ends && !feof(f);
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
		if (strcmp(key, "notation") == 0) {
			/* which reading a character has where the IPA and extIPA differ (Q18):
			   the IPA's unless the map says extipa, before the lines that need it */
			char *w = next_word(&rest);
			map->extipa = w && strcmp(w, "extipa") == 0;
			if (!w || (strcmp(w, "extipa") != 0 && strcmp(w, "ipa") != 0))
				evv_diag(EVV_DIAG_LOSS, "map-ignored", "notation `%s' is neither ipa nor extipa; ipa is used",
				         w ? w : "");
			continue;
		}
		if (strcmp(key, "extipa") == 0) {
			/* a line of extIPA's own reading (ingressive ↓): read only under `notation extipa' */
			if (!map->extipa || !(key = next_word(&rest)))
				continue;
		}
		if (strcmp(key, "template") == 0) {
			char *w = next_word(&rest);
			if (w)
				copy_checked(map->tmpl, w, sizeof(map->tmpl), "template");
			continue;
		}
		if (strcmp(key, "style") == 0) {
			char *w = next_word(&rest);
			map->french = w && strcmp(w, "french") == 0;
			if (!w || (strcmp(w, "french") != 0 && strcmp(w, "standard") != 0))
				evv_diag(EVV_DIAG_LOSS, "map-ignored", "style `%s' is neither french nor standard; standard is used",
				         w ? w : "");
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
			else
				evv_diag(EVV_DIAG_LOSS, "map-ignored", "secondary `%s' is not 0, 1 or 2", w ? w : "");
			continue;
		}
		if (strcmp(key, "schwa") == 0) {
			char *w = next_word(&rest);
			if (w)
				copy_checked(map->schwa, w, EVV_PHONE_LEN, "phone");
			continue;
		}
		if (strcmp(key, "reiterate") == 0) {
			/* extIPA's reiteration (Tier B): what is said at a `\' typed in IPA, after
			   a consonant or after a vowel, before the sound is said again */
			char *c = next_word(&rest);
			char *w = next_word(&rest);
			if (!c || !w || (strcmp(c, "c") != 0 && strcmp(c, "v") != 0))
				evv_diag(EVV_DIAG_LOSS, "map-ignored", "a reiterate line needs c or v and the IPA said");
			else
				copy_checked(map->reiterate[c[0] == 'v'], w, sizeof(map->reiterate[0]), "reiteration");
			continue;
		}
		if (strcmp(key, "syllabic") == 0) {
			/* version 2 (C7): the sound the schwa is said with when it only carries
			   the syllable of a consonant marked syllabic */
			char *w = next_word(&rest);
			if (w)
				copy_checked(map->syl_sound, w, EVV_ID_LEN, "sound id");
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
			if (!x || !y)
				evv_diag(EVV_DIAG_LOSS, "map-ignored", "a cluster line needs two phones");
			else if (map->n_clusters >= 16)
				evv_diag(EVV_DIAG_LOSS, "map-list-full", "cluster %s %s: no room past 16", x, y);
			else {
				copy_checked(map->clusters[map->n_clusters][0], x, EVV_PHONE_LEN, "phone");
				copy_checked(map->clusters[map->n_clusters][1], y, EVV_PHONE_LEN, "phone");
				map->n_clusters++;
			}
			continue;
		}
		if (strcmp(key, "onset") == 0) {
			char *w = next_word(&rest);
			if (w && w[0] >= '1' && w[0] <= '3')
				map->onset = w[0] - '0';
			else
				evv_diag(EVV_DIAG_LOSS, "map-ignored", "onset `%s' is not 1, 2 or 3", w ? w : "");
			continue;
		}
		if (strcmp(key, "accent") == 0) {
			/* what kind of language it is: the first thing the engine is told */
			char all[4096];
			if (accents++)
				evv_diag(EVV_DIAG_LOSS, "map-ignored", "a second accent line; it replaces the first");
			if (snprintf(all, sizeof(all), "v=1 %s", rest) >= (int)sizeof(all))
				evv_diag(EVV_DIAG_LOSS, "map-line-long", "the accent line is cut to %d bytes", (int)sizeof(all) - 1);
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
			char copy[4096];
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
				copy_checked(map->ask[map->n_ask++], w, EVV_ASK_LEN, "question word");
			}
			if (!map->ask_where)
				map->ask_where = 1;
			continue;
		}
		if (strcmp(key, "weaktones") == 0) {
			char *w;
			while ((w = next_word(&rest)) != NULL) {
				if (map->n_weak_tones >= 16) {
					evv_diag(EVV_DIAG_LOSS, "map-list-full", "weak tone %s: no room past 16", w);
					continue;
				}
				copy_checked(map->weak_tones[map->n_weak_tones++], w, EVV_ID_LEN, "tone id");
			}
			continue;
		}
		if (strcmp(key, "tonename") == 0) {
			char *from = next_word(&rest);
			char *to = next_word(&rest);
			if (from && to)
				failed |= add_tone_name(map, from, to);
			else
				evv_diag(EVV_DIAG_LOSS, "map-ignored", "a tonename line needs two names");
			continue;
		}
		if (strcmp(key, "version") == 0) {
			char *w = next_word(&rest);
			map->version = w ? atoi(w) : 0;
			continue;
		}
		if (strcmp(key, "weights") == 0) {
			static const char *names[W_COUNT] = {"stricture", "airstream", "nasal", "lateral", "sibilant",
			                                     "place_step", "place2", "voicing", "height_step",
			                                     "backness_step", "rounding", "class"};
			char *w;
			while ((w = next_word(&rest)) != NULL) {
				char *eq = strchr(w, '=');
				int k;
				if (!eq)
					continue;
				*eq = 0;
				for (k = 0; k < W_COUNT && strcmp(names[k], w) != 0; k++)
					;
				if (k < W_COUNT)
					map->weights[k] = atoi(eq + 1);
				else
					evv_diag(EVV_DIAG_LOSS, "map-ignored", "weights: no weight %s", w);
			}
			continue;
		}
		if (strcmp(key, "letter") == 0) {
			failed |= read_letter(map, rest);
			continue;
		}
		if (strcmp(key, "mod") == 0 || strcmp(key, "premod") == 0) {
			failed |= read_mod(map, rest, key[0] == 'p');
			continue;
		}
		if (strcmp(key, "after") == 0) {
			/* `after ᪽ ̥ ̬': the second character of a mark of two (D77) */
			char *mark = next_word(&rest), *w;
			if (!mark || map->n_after >= (int)(sizeof(map->after) / sizeof(map->after[0]))) {
				evv_diag(EVV_DIAG_LOSS, "map-ignored", "an after line needs a mark (and at most 16 are read)");
				continue;
			}
			copy_checked(map->after[map->n_after].mark, mark, sizeof(map->after[0].mark), "mark");
			map->after[map->n_after].firsts[0] = 0;
			while ((w = next_word(&rest)) != NULL)
				if (strlen(map->after[map->n_after].firsts) + strlen(w) < sizeof(map->after[0].firsts))
					strcat(map->after[map->n_after].firsts, w);
			map->n_after++;
			continue;
		}
		if (strcmp(key, "tonemark") == 0 || strcmp(key, "register") == 0 || strcmp(key, "slope") == 0) {
			failed |= read_tonemark(map, key[0] == 't' ? 't' : key[0] == 'r' ? 'r' : 's', rest);
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
		const char *like = keyword_like(key);
		if (like)
			evv_diag(EVV_DIAG_LOSS, "map-keyword-like", "`%s' is read as a phoneme; is it the keyword %s misspelt?",
			         key, like);
		for (int i = 0; i < map->n_entries; i++)
			if (strcmp(map->entries[i].key, key) == 0) {
				evv_diag(EVV_DIAG_LOSS, "map-key-duplicate", "`%s' is mapped again; the first line is used", key);
				break;
			}
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
	evv_diag_line = 0;
	/* names used that no line defines */
	for (int i = 0; i < map->n_entries; i++)
		for (int j = 0; j < map->entries[i].n; j++) {
			const char *id = map->entries[i].phones[j].sound;
			int found = !id[0];
			for (int k = 0; k < map->n_sounds && !found; k++)
				found = strcmp(map->sounds[k].id, id) == 0;
			if (!found)
				evv_diag(EVV_DIAG_LOSS, "map-sound-undefined",
				         "`%s' names sound %s, which no sound line defines; the module's own phone is said",
				         map->entries[i].key, id);
		}
	for (int i = 0; i < map->n_tones; i++) {
		int found = 0;
		for (int k = 0; k < map->n_tone_ids && !found; k++)
			found = strcmp(map->tone_ids[k], map->tones[i].to) == 0;
		if (!found)
			evv_diag(EVV_DIAG_LOSS, "map-tone-undefined", "tonename %s names tone %s, which no tone line defines",
			         map->tones[i].from, map->tones[i].to);
	}
	for (int i = 0; i < map->n_weak_tones; i++) {
		int found = 0;
		for (int k = 0; k < map->n_tone_ids && !found; k++)
			found = strcmp(map->tone_ids[k], map->weak_tones[i]) == 0;
		if (!found)
			evv_diag(EVV_DIAG_LOSS, "map-tone-undefined", "weaktones names tone %s, which no tone line defines",
			         map->weak_tones[i]);
	}
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
	free(map->letters);
	free(map->mods);
	free(map->tonemarks);
	for (int i = 0; i < map->n_comp; i++)
		free(map->composed[i].group);
	free(map->composed);
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

static int emit(const EvvMapEntry *e, EvvMapPhone *out, int n, int max_out, const char *whole)
{
	if (e->n == 0)
		evv_diag(EVV_DIAG_NOTE, "said-as-nothing", "`%s' in /%s/: the map gives it as -", e->key, whole);
	else if (n + e->n > max_out)
		evv_diag(EVV_DIAG_LOSS, "phones-cut", "/%s/ needs more than %d phones; the rest is dropped", whole, max_out);
	for (int i = 0; i < e->n && n < max_out; i++)
		out[n++] = e->phones[i];
	return n;
}

/* A character as U+XXXX, for a report. */
static unsigned long code_point(const unsigned char *p, int len)
{
	if (len == 1)
		return p[0];
	unsigned long c = p[0] & (0xff >> (len + 1));
	for (int i = 1; i < len; i++)
		c = (c << 6) | (p[i] & 0x3f);
	return c;
}

static int utf8_len(unsigned char c)
{
	if (c < 0x80) return 1;
	if ((c & 0xe0) == 0xc0) return 2;
	if ((c & 0xf0) == 0xe0) return 3;
	if ((c & 0xf8) == 0xf0) return 4;
	return 1;
}

const EvvLetter *evv_map_letter(const EvvMap *map, const char *ch, size_t len)
{
	for (int i = 0; i < map->n_letters; i++)
		if (strlen(map->letters[i].ipa) == len && memcmp(map->letters[i].ipa, ch, len) == 0)
			return &map->letters[i];
	return NULL;
}

static const EvvMod *find_mod_of(const EvvMap *map, const char *mark, size_t len, char cls, int pre)
{
	for (int i = 0; i < map->n_mods; i++)
		if (map->mods[i].pre == pre && (cls == 0 || map->mods[i].cls == cls) && strlen(map->mods[i].mark) == len &&
		    memcmp(map->mods[i].mark, mark, len) == 0)
			return &map->mods[i];
	return NULL;
}

/* The first characters a second character of a mark of two is said after
   (`after' lines), or NULL for a mark of its own (D77). */
static const char *after_of(const EvvMap *map, const char *mark, size_t len)
{
	for (int i = 0; i < map->n_after; i++)
		if (strlen(map->after[i].mark) == len && memcmp(map->after[i].mark, mark, len) == 0)
			return map->after[i].firsts;
	return NULL;
}

/* Whether the code point at `p' (of `len' bytes) is one of `firsts'. */
static int among(const char *firsts, const char *p, size_t len)
{
	for (const char *f = firsts; *f; f += utf8_len((unsigned char)*f))
		if ((size_t)utf8_len((unsigned char)*f) == len && memcmp(f, p, len) == 0)
			return 1;
	return 0;
}

static const EvvMod *find_mod(const EvvMap *map, const char *mark, size_t len, char cls)
{
	return find_mod_of(map, mark, len, cls, 0);
}

int evv_map_has_mod(const EvvMap *map, const char *mark, size_t len, char cls)
{
	return find_mod_of(map, mark, len, cls, 0) != NULL;
}

int evv_map_has_premod(const EvvMap *map, const char *mark, size_t len)
{
	return find_mod_of(map, mark, len, 0, 1) != NULL;
}

/* The nearest-letter cost of ipa/features.toml (engine/ipa/adapter.py's
   `distance', in the same weights). */
static int letter_distance(const EvvMap *map, const EvvLetter *a, const EvvLetter *b)
{
	const int *w = map->weights;
	if (a->cls != b->cls)
		return w[W_CLASS];
	if (a->cls == 'v')
		return w[W_HEIGHT] * abs(a->height - b->height) + w[W_BACKNESS] * abs(a->backness - b->backness) +
		       w[W_ROUNDING] * (strcmp(a->f[0], b->f[0]) != 0);
	static const int k[7] = {W_STRICTURE, W_AIRSTREAM, W_NASAL, W_LATERAL, W_SIBILANT, W_PLACE2, W_VOICING};
	int d = w[W_PLACE] * abs(a->place - b->place);
	for (int i = 0; i < 7; i++)
		d += w[k[i]] * (strcmp(a->f[i], b->f[i]) != 0);
	return d;
}

/* The keys of a sound the map defines, from its group "{D id k=v ...}". */
static int sound_keys(const EvvMap *map, const char *id, char keys[][8], double *vals, int max)
{
	int n = 0;
	for (int i = 0; i < map->n_sounds; i++) {
		if (strcmp(map->sounds[i].id, id) != 0)
			continue;
		char copy[4096];
		copy_name(copy, map->sounds[i].group + 2, sizeof(copy)); /* past "{D" */
		char *p = copy, *w;
		size_t l = strlen(copy);
		if (l && copy[l - 1] == '}')
			copy[l - 1] = 0;
		next_word(&p); /* the id */
		while ((w = next_word(&p)) != NULL) {
			char *eq = strchr(w, '=');
			if (!eq)
				continue;
			*eq = 0;
			if (n >= max) {
				evv_diag(EVV_DIAG_LOSS, "compose-full", "sound %s: key %s past the %d a composition holds; left out",
				         id, w, max);
				continue;
			}
			copy_checked(keys[n], w, 8, "key");
			vals[n++] = atof(eq + 1);
		}
		break;
	}
	return n;
}

/* A letter with marks, said as the letter's line with each mark's `mod' line
   merged into its sound: ratios multiplied, times added (DESIGN.md 2.3). A
   letter the map has no line for is said as the nearest letter it has; a
   mark with no line for the letter's class is left off. Both are losses and
   reported. The result is kept as an entry of its own, so the same string is
   composed once. Returns the phones written, or -1 when `ipa' is not one
   letter and its marks (the old way then takes it apart). */
static int compose(EvvMap *map, const char *ipa, EvvMapPhone *out, int max_out)
{
	/* marks written before the letter, each with a `premod' line, then the letter */
	const char *lp = ipa;
	while (*lp && !evv_map_letter(map, lp, (size_t)utf8_len((unsigned char)*lp)) &&
	       evv_map_has_premod(map, lp, (size_t)utf8_len((unsigned char)*lp)))
		lp += utf8_len((unsigned char)*lp);
	if (!*lp)
		return -1;
	int bl = utf8_len((unsigned char)lp[0]);
	const EvvLetter *letter = evv_map_letter(map, lp, (size_t)bl);
	if (!letter)
		return -1;
	char two[16];
	const char *joined = NULL;
	int jl = 0;
	/* a letter of two letters, the second right after the first (extIPA's
	   cluck ǃ¡: a click and the tongue's slap): the pair is the letter where
	   the map has a line for it, and its marks are composed on that line */
	{
		const char *q = lp + bl;
		int ql = *q ? utf8_len((unsigned char)*q) : 0;
		if (ql && bl + ql < (int)sizeof(two) && evv_map_letter(map, q, (size_t)ql)) {
			memcpy(two, lp, (size_t)bl);
			memcpy(two + bl, q, (size_t)ql);
			if (evv_map_letter(map, two, (size_t)(bl + ql)) && find(map, two, (size_t)(bl + ql))) {
				letter = evv_map_letter(map, two, (size_t)(bl + ql));
				joined = q;
				jl = ql;
			}
		}
	}
	for (const char *p = joined ? joined + jl : lp + bl; *p; p += utf8_len((unsigned char)*p))
		if (evv_map_letter(map, p, (size_t)utf8_len((unsigned char)*p)))
			return -1; /* two letters: an affricate or a sequence */
	/* a letter of two characters, a letter and a mark the letter's own line
	   reads otherwise (extIPA's bunched r, the apical r: D74), wherever the
	   mark stands among the others (canonical order puts a mark below before
	   one above, so ɹ̩̈ comes as ɹ, ̩, ̈): the pair is the letter, and that
	   mark is not composed again */
	for (const char *q = lp + bl; *q && !joined; q += utf8_len((unsigned char)*q)) {
		int ql = utf8_len((unsigned char)*q);
		if (bl + ql >= (int)sizeof(two))
			continue;
		/* a mark that begins a mark of two makes no letter (𝼀̬᪽ is 𝼀 with
		   ◌̬᪽, not 𝼀̬ with ᪽: D77) */
		const char *nq = q + ql;
		const char *fs = *nq ? after_of(map, nq, (size_t)utf8_len((unsigned char)*nq)) : NULL;
		if (fs && among(fs, q, (size_t)ql))
			continue;
		memcpy(two, lp, (size_t)bl);
		memcpy(two + bl, q, (size_t)ql);
		if (evv_map_letter(map, two, (size_t)(bl + ql)) && find(map, two, (size_t)(bl + ql))) {
			letter = evv_map_letter(map, two, (size_t)(bl + ql));
			joined = q;
			jl = ql;
			break;
		}
	}
	const EvvMapEntry *base = joined ? find(map, two, (size_t)(bl + jl)) : find(map, lp, (size_t)bl);
	if (!base) {
		int best = -1, best_d = 0;
		for (int i = 0; i < map->n_letters; i++) {
			if (!find(map, map->letters[i].ipa, strlen(map->letters[i].ipa)))
				continue;
			int d = letter_distance(map, letter, &map->letters[i]);
			if (best < 0 || d < best_d) {
				best = i;
				best_d = d;
			}
		}
		if (best < 0)
			return -1;
		evv_diag(EVV_DIAG_LOSS, "nearest-letter", "/%.*s/ has no line: said as /%s/, %d away by features", bl, lp,
		         map->letters[best].ipa, best_d);
		base = find(map, map->letters[best].ipa, strlen(map->letters[best].ipa));
	}
	char keys[32][8];
	double vals[32];
	int nk = 0, carrier = 0;
	for (int i = 0; i < base->n; i++)
		if (base->phones[i].sound[0]) {
			nk = sound_keys(map, base->phones[i].sound, keys, vals, 32);
			carrier = i;
			break;
		}
	int applied = 0;
	const char *prev = NULL; /* the code point before p */
	for (const char *p = ipa; *p; prev = p, p += utf8_len((unsigned char)*p)) {
		if (p == lp) {
			p += bl - utf8_len((unsigned char)*p); /* the letter itself */
			continue;
		}
		if (p == joined)
			continue; /* the mark that is part of it */
		int ml = utf8_len((unsigned char)*p);
		const char *fs = after_of(map, p, (size_t)ml);
		if (fs && !(prev && among(fs, prev, (size_t)utf8_len((unsigned char)*prev)))) {
			evv_diag(EVV_DIAG_LOSS, "mark-left-off", "U+%04lX %.*s on /%s/: the second half of a mark of two, "
			         "without its first; left off", code_point((const unsigned char *)p, ml), ml, p, ipa);
			continue;
		}
		const EvvMod *m = find_mod_of(map, p, (size_t)ml, letter->cls, p < lp);
		if (!m) {
			evv_diag(EVV_DIAG_LOSS, "mark-left-off", "U+%04lX %.*s on /%s/: no %smod line for a %s; left off",
			         code_point((const unsigned char *)p, ml), ml, p, ipa, p < lp ? "pre" : "",
			         letter->cls == 'v' ? "vowel" : "consonant");
			continue;
		}
		for (int o = 0; o < m->n; o++) {
			int k;
			for (k = 0; k < nk && strcmp(keys[k], m->ops[o].key) != 0; k++)
				;
			/* a level the layer adds to the module's own (voice, breath, noise): a
			   sound without one has 0 dB of it, so a mark adds to nought */
			int level = strcmp(m->ops[o].key, "av") == 0 || strcmp(m->ops[o].key, "ah") == 0 ||
			            strcmp(m->ops[o].key, "af") == 0;
			if (k == nk && m->ops[o].op == '+' && !level) {
				evv_diag(EVV_DIAG_LOSS, "mark-left-off", "%s on /%s/: %s+%g has no %s to add to", m->mark, ipa,
				         m->ops[o].key, m->ops[o].v, m->ops[o].key);
				continue;
			}
			if (k == nk || m->ops[o].op == '=') {
				if (k < nk) { /* a value set: the base's own gives way */
					vals[k] = m->ops[o].v;
					continue;
				}
				if (nk >= 32) {
					evv_diag(EVV_DIAG_LOSS, "compose-full", "%s on /%s/: no room for key %s; left off", m->mark, ipa,
					         m->ops[o].key);
					continue;
				}
				copy_name(keys[nk], m->ops[o].key, 8);
				vals[nk++] = m->ops[o].op == '=' ? m->ops[o].v : level ? 0 : 100;
				if (m->ops[o].op == '=')
					continue;
			}
			if (m->ops[o].op == '~') {
				/* towards a target: the letter's own frequency (its `fNhz') moved by
				   the part asked, as a ratio of what the base already has */
				int f = m->ops[o].key[0] == 'f' ? m->ops[o].key[1] - '1' : -1;
				double hz = f >= 0 && f < 4 ? letter->hz[f] : 0;
				if (hz <= 0) {
					evv_diag(EVV_DIAG_LOSS, "mark-left-off", "%s on /%s/: %s~ and the letter has no %shz to move from",
					         m->mark, ipa, m->ops[o].key, m->ops[o].key);
					continue;
				}
				vals[k] = vals[k] * (hz + (m->ops[o].v - hz) * m->ops[o].part / 100.0) / hz;
				continue;
			}
			vals[k] = m->ops[o].op == '*' ? vals[k] * m->ops[o].v / 100.0 : vals[k] + m->ops[o].v;
		}
		applied++;
	}
	/* the composed sound, under an id of its own: the same string keeps its id,
	   and is composed (and its fallbacks reported) every time it is met */
	EvvMapEntry e = *base;
	char id[EVV_ID_LEN] = "";
	for (int c = 0; c < map->n_comp; c++)
		if (strcmp(map->composed[c].group, ipa) == 0)
			copy_name(id, map->composed[c].id, EVV_ID_LEN);
	if (!id[0]) {
		char group[512];
		int taken;
		do { /* not a name the map's own sound lines use */
			snprintf(id, sizeof(id), "c%d", ++map->n_composed);
			taken = 0;
			for (int k = 0; k < map->n_sounds && !taken; k++)
				taken = strcmp(map->sounds[k].id, id) == 0;
		} while (taken);
		size_t at = (size_t)snprintf(group, sizeof(group), "{D %s", id);
		for (int k = 0; k < nk && at < sizeof(group); k++)
			at += (size_t)snprintf(group + at, sizeof(group) - at, " %s=%ld", keys[k], lround(vals[k]));
		if (at + 2 > sizeof(group)) {
			evv_diag(EVV_DIAG_LOSS, "compose-full", "/%s/: its definition is longer than %d bytes", ipa,
			         (int)sizeof(group) - 2);
			return -1;
		}
		snprintf(group + at, sizeof(group) - at, "}");
		if (add_defined(&map->sounds, &map->n_sounds, &map->cap_sounds, id, group) != 0 ||
		    add_defined(&map->composed, &map->n_comp, &map->cap_comp, id, ipa) != 0)
			return -1;
		evv_diag(EVV_DIAG_NOTE, "composed", "/%s/ = /%s/ and %d mark(s), as %s", ipa, e.key, applied, group);
	}
	if (e.n > 0)
		copy_name(e.phones[carrier].sound, id, EVV_ID_LEN);
	copy_name(e.key, ipa, sizeof(e.key));
	return emit(&e, out, 0, max_out, ipa);
}

int evv_map_lookup(const EvvMap *map, const char *table, const char *mnemonic, const char *ipa,
                   EvvMapPhone *out, int max_out)
{
	int matched;
	return evv_map_lookup_ex(map, table, mnemonic, ipa, out, max_out, &matched);
}

int evv_map_lookup_ex(const EvvMap *map, const char *table, const char *mnemonic, const char *ipa,
                      EvvMapPhone *out, int max_out, int *matched)
{
	const EvvMapEntry *e;
	*matched = 1;
	if (table && mnemonic && *mnemonic) {
		char key[64];
		if (snprintf(key, sizeof(key), "@%s:%s", table, mnemonic) >= (int)sizeof(key))
			evv_diag(EVV_DIAG_LOSS, "key-cut", "@%s:%s is longer than %d bytes and cannot match", table, mnemonic,
			         (int)sizeof(key) - 1);
		if ((e = find(map, key, strlen(key))) != NULL)
			return emit(e, out, 0, max_out, key);
	}
	*matched = 0;
	if (!ipa || !*ipa)
		return 0;
	if ((e = find(map, ipa, strlen(ipa))) != NULL) {
		*matched = 1;
		return emit(e, out, 0, max_out, ipa);
	}
	if (map->version >= 2) {
		/* a letter and its marks, composed when speaking (C4) */
		int n = compose((EvvMap *)map, ipa, out, max_out);
		if (n >= 0) {
			*matched = 1;
			return n;
		}
		/* two letters joined by a tie bar (U+0361, U+035C) or by extIPA's
		   sliding mark (U+0362) with no line for the pair: each side looked
		   up, or composed with its own marks, and said one after the other
		   (Q22: the old lookup below left off every mark on either side).
		   The sliding mark is a mark of both sides as well: its `mod' line
		   is what makes the two take the time of one segment. */
		const char *tie = NULL;
		int slide = 0;
		for (const char *q = ipa; *q; q += utf8_len((unsigned char)*q))
			if ((unsigned char)q[0] == 0xcd && ((unsigned char)q[1] == 0xa1 || (unsigned char)q[1] == 0x9c ||
			                                    (unsigned char)q[1] == 0xa2)) {
				tie = q;
				slide = (unsigned char)q[1] == 0xa2;
				break;
			}
		if (tie && tie > ipa && tie[2] && (size_t)(tie - ipa) + 3 < 64 && strlen(tie + 2) + 3 < 64) {
			char a[64], b[64];
			size_t la = (size_t)(tie - ipa);
			memcpy(a, ipa, la);
			a[la] = 0;
			snprintf(b, sizeof(b), "%s", tie + 2);
			if (slide) {
				/* the mark goes after each side's own marks, as typed after a letter */
				memcpy(a + la, tie, 2);
				a[la + 2] = 0;
				size_t lb = strlen(b);
				memcpy(b + lb, tie, 2);
				b[lb + 2] = 0;
			}
			/* only when each side begins with a letter, and the pair itself (its two
			   letters and the tie, without their marks) has no line: a marked
			   affricate the template has (t͡sʰ) is said as before, by its line */
			int l1 = utf8_len((unsigned char)ipa[0]), l2 = utf8_len((unsigned char)tie[2]);
			char bare[16];
			int has_bare = 0;
			if ((size_t)(l1 + 2 + l2) < sizeof(bare)) {
				memcpy(bare, ipa, (size_t)l1);
				memcpy(bare + l1, tie, 2);
				memcpy(bare + l1 + 2, tie + 2, (size_t)l2);
				has_bare = find(map, bare, (size_t)(l1 + 2 + l2)) != NULL;
			}
			if (has_bare || !evv_map_letter(map, ipa, (size_t)l1) || !evv_map_letter(map, tie + 2, (size_t)l2))
				goto apart;
			int ma = 0, mb = 0;
			int na = evv_map_lookup_ex(map, NULL, NULL, a, out, max_out, &ma);
			int nb = ma ? evv_map_lookup_ex(map, NULL, NULL, b, out + na, max_out - na, &mb) : 0;
			if (ma && mb) {
				*matched = 1;
				if (!slide)
					evv_diag(EVV_DIAG_LOSS, "tie-as-sequence", "/%s/ has no line: its two sides said one "
					         "after the other, each with its own marks", ipa);
				return na + nb;
			}
		}
	}
apart:;
	/* taken apart from the left, longest key first; a character no key
	   starts with is skipped, and reported if the rest is said */
	int n = 0;
	const char *p = ipa;
	const char *skipped[EVV_MAX_PHONES * 4];
	int n_skipped = 0;
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
			*matched = 1;
			n = emit(best, out, n, max_out, ipa);
			p += strlen(best->key);
		} else {
			if (n_skipped < (int)(sizeof(skipped) / sizeof(skipped[0])))
				skipped[n_skipped++] = p;
			p += utf8_len((unsigned char)*p);
		}
	}
	/* nothing matched: the caller reports the phoneme dropped */
	for (int i = 0; i < n_skipped && *matched; i++) {
		int l = utf8_len((unsigned char)*skipped[i]);
		evv_diag(EVV_DIAG_LOSS, "ipa-char-skipped", "U+%04lX %.*s in /%s/%s%s%s",
		         code_point((const unsigned char *)skipped[i], l), l, skipped[i], ipa, table ? " (" : "",
		         table ? table : "", table ? ")" : "");
	}
	if (*p)
		evv_diag(EVV_DIAG_LOSS, "phones-cut", "/%s/ needs more than %d phones; `%s' is dropped", ipa, max_out, p);
	return n;
}

void evv_word_clear(EvvWord *w)
{
	w->n = 0;
	w->has_nucleus = 0;
}

static EvvPhone *push(EvvWord *w, const char *phone, const char *sound, char made, int nucleus, int stress)
{
	if (w->n >= EVV_WORD_MAX) {
		evv_diag(EVV_DIAG_LOSS, "word-too-long", "more than %d phones in a word; phone %s dropped", EVV_WORD_MAX, phone);
		return NULL;
	}
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
			evv_diag(EVV_DIAG_NOTE, "schwa-inserted", "%s before syllabic %s", map->schwa, n ? phones[0].name : "");
			EvvPhone *p = push(w, map->schwa, map->syl_sound[0] ? map->syl_sound : NULL, 0, 1, stress);
			if (p && tone)
				copy_name(p->tone, tone, EVV_ID_LEN);
		} else {
			evv_diag(EVV_DIAG_LOSS, "syllable-no-nucleus", "syllabic %s and the map has no schwa: the syllable%s is lost",
			         n ? phones[0].name : "", tone ? " and its tone" : "");
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
	if (at + l + 1 > room) {
		evv_diag(EVV_DIAG_LOSS, "annotation-cut", "a word's annotation is longer than %d bytes", (int)room - 1);
		return at;
	}
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
		/* one segment said as two phones (a double articulation) begins
		   its syllable whole */
		while (s > a && s <= b && w->ph[real[s]].glue)
			s--;
		/* a vowel that is not a nucleus stays with the syllable before it */
		for (int i = a; i <= b; i++)
			if (evv_map_is_vowel(map, w->ph[real[i]].phone) && s <= i)
				s = i + 1;
		/* a syllable break typed in IPA (`.') says where the syllable begins */
		for (int i = a; i <= nuc[k]; i++)
			if (w->ph[real[i]].brk) {
				s = i;
				break;
			}
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
