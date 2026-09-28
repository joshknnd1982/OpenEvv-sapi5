/*
 * OpenEvvFrontend: eSpeak NG's reading of a text, written out as
 * pronunciations in an openevv language module's own phoneme alphabet.
 *
 * An OpenEVV language pack made from an eSpeak NG language has no engine of
 * its own. eSpeak NG reads the text -- its rules, its dictionary, its numbers,
 * its stress -- and this program writes each word it read as a `[ ]
 * pronunciation annotation in the phones of the openevv module the pack names
 * as its template, using the pack's phonemes.map. The engine host hands that
 * to the template's engine, which speaks it. The punctuation that ends each
 * clause is kept, so the engine's own intonation follows the sentence.
 *
 * It is a program of its own, and its own licence, because it links eSpeak
 * NG: the SAPI wrapper talks to it over two pipes.
 *
 *   OpenEvvFrontend --data DIR --voice NAME --map FILE --text "..."
 *        prints what a text becomes, with each word's position
 *   OpenEvvFrontend --data DIR --dump-phonemes
 *        every phoneme of every eSpeak NG phoneme table, as JSON
 *   OpenEvvFrontend --data DIR --serve
 *        the pipe protocol below, on standard input and output
 *
 * Copyright (C) 2026 the OpenEVV SAPI5 contributors
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the Free
 * Software Foundation; either version 3 of the License, or (at your option)
 * any later version. See COPYING.
 */
#include "config.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#include <windows.h>
#endif

#include <espeak-ng/espeak_ng.h>
#include <espeak-ng/speak_lib.h>
#include <espeak-ng/encoding.h>

#include "dictionary.h"
#include "phoneme.h"
#include "readclause.h"
#include "speech.h"
#include "synthdata.h"
#include "synthesize.h"
#include "translate.h"
#include "voice.h"

#include "evv_map.h"
#include "frontend_proto.h"

/* ---- output: the annotated text and where each word came from ---------- */

typedef struct {
	char *text;
	size_t len, cap;
	EvvAnchor *anchors;
	size_t n_anchors, cap_anchors;
} Output;

static Output out;

static void out_reset(void)
{
	out.len = 0;
	if (out.text)
		out.text[0] = 0;
	out.n_anchors = 0;
}

static void out_put(const char *s, size_t l)
{
	if (out.len + l + 1 > out.cap) {
		size_t cap = out.cap ? out.cap * 2 : 4096;
		while (cap < out.len + l + 1)
			cap *= 2;
		char *t = (char *)realloc(out.text, cap);
		if (!t)
			return;
		out.text = t;
		out.cap = cap;
	}
	memcpy(out.text + out.len, s, l);
	out.len += l;
	out.text[out.len] = 0;
}

static void out_anchor(uint32_t src, uint32_t src_len)
{
	if (out.n_anchors == out.cap_anchors) {
		size_t cap = out.cap_anchors ? out.cap_anchors * 2 : 256;
		EvvAnchor *a = (EvvAnchor *)realloc(out.anchors, cap * sizeof(EvvAnchor));
		if (!a)
			return;
		out.anchors = a;
		out.cap_anchors = cap;
	}
	EvvAnchor *a = &out.anchors[out.n_anchors++];
	a->out_offset = (uint32_t)out.len;
	a->src_offset = src;
	a->src_length = src_len;
}

/* ---- one clause ----------------------------------------------------------- */

typedef struct {
	EvvWord w;
	int src;      /* the word's first character in the text, from nought */
	int src_len;
} ClauseWord;

#define MAX_CLAUSE_WORDS 400
static ClauseWord clause_words[MAX_CLAUSE_WORDS];
static int n_clause_words;

static EvvMap g_map;
static int g_map_loaded;

/* --stats: how often each phoneme is said, for the tools that choose a
   template and write the maps */
typedef struct {
	char table[32], mnem[32], ipa[64];
	int type, syllabic, count;
} Stat;
static Stat *g_stats;
static int g_n_stats, g_cap_stats, g_counting;

static void count_phoneme(const char *table, const char *mnem, const char *ipa, int type, int syllabic)
{
	for (int i = 0; i < g_n_stats; i++)
		if (strcmp(g_stats[i].table, table) == 0 && strcmp(g_stats[i].mnem, mnem) == 0 &&
		    strcmp(g_stats[i].ipa, ipa) == 0 && g_stats[i].syllabic == syllabic) {
			g_stats[i].count++;
			return;
		}
	if (g_n_stats == g_cap_stats) {
		g_cap_stats = g_cap_stats ? g_cap_stats * 2 : 256;
		g_stats = (Stat *)realloc(g_stats, sizeof(Stat) * g_cap_stats);
	}
	Stat *st = &g_stats[g_n_stats++];
	snprintf(st->table, sizeof(st->table), "%s", table);
	snprintf(st->mnem, sizeof(st->mnem), "%s", mnem);
	snprintf(st->ipa, sizeof(st->ipa), "%s", ipa);
	st->type = type;
	st->syllabic = syllabic;
	st->count = 1;
}

static int engine_stress(int level)
{
	if (level >= STRESS_IS_PRIMARY)
		return 1;
	if (level == STRESS_IS_SECONDARY)
		return 2;
	return 0;
}

static ClauseWord *new_word(int src, int src_len)
{
	if (n_clause_words >= MAX_CLAUSE_WORDS)
		return &clause_words[MAX_CLAUSE_WORDS - 1];
	ClauseWord *cw = &clause_words[n_clause_words++];
	evv_word_clear(&cw->w);
	cw->src = src;
	cw->src_len = src_len;
	return cw;
}

static void append_phones(EvvWord *to, const EvvWord *from, int at_front)
{
	if (to->n + from->n > EVV_WORD_MAX)
		return;
	if (at_front) {
		memmove(&to->ph[from->n], &to->ph[0], sizeof(EvvPhone) * to->n);
		memcpy(&to->ph[0], &from->ph[0], sizeof(EvvPhone) * from->n);
	} else {
		memcpy(&to->ph[to->n], &from->ph[0], sizeof(EvvPhone) * from->n);
	}
	to->n += from->n;
	to->has_nucleus |= from->has_nucleus;
}

static const char *clause_punctuation(int terminator)
{
	switch (terminator & CLAUSE_INTONATION_TYPE) {
	case CLAUSE_INTONATION_QUESTION:
		return "?";
	case CLAUSE_INTONATION_EXCLAMATION:
		return "!";
	case CLAUSE_INTONATION_COMMA:
		return ",";
	case CLAUSE_INTONATION_NONE:
		return "";
	default:
		return (terminator & CLAUSE_TYPE) == CLAUSE_TYPE_CLAUSE ? "," : ".";
	}
}

static void write_clause(int terminator)
{
	/* A word with no vowel of its own -- a lone preposition like Czech `v',
	   or a consonant eSpeak split off -- is said as part of the word after
	   it, or of the one before it at the end of a clause. */
	for (int i = 0; i < n_clause_words; i++) {
		ClauseWord *cw = &clause_words[i];
		if (cw->w.n == 0 || cw->w.has_nucleus)
			continue;
		int j = i + 1;
		while (j < n_clause_words && clause_words[j].w.n == 0)
			j++;
		if (j < n_clause_words) {
			append_phones(&clause_words[j].w, &cw->w, 1);
			if (clause_words[j].src > cw->src) {
				clause_words[j].src_len += clause_words[j].src - cw->src;
				clause_words[j].src = cw->src;
			}
			cw->w.n = 0;
			continue;
		}
		int k = i - 1;
		while (k >= 0 && clause_words[k].w.n == 0)
			k--;
		if (k >= 0) {
			append_phones(&clause_words[k].w, &cw->w, 0);
			cw->w.n = 0;
		} else if (g_map.schwa[0]) {
			/* nothing to lean on: give it a vowel */
			char phones[1][EVV_PHONE_LEN];
			strcpy(phones[0], g_map.schwa);
			EvvWord tmp = cw->w;
			evv_word_clear(&cw->w);
			evv_word_add(&cw->w, &g_map, phones, 1, 1, 1, 1);
			append_phones(&cw->w, &tmp, 0);
		}
	}
	static char buf[EVV_WORD_MAX * 12 + 16];
	int wrote = 0;
	for (int i = 0; i < n_clause_words; i++) {
		ClauseWord *cw = &clause_words[i];
		size_t l = evv_word_annotate(&cw->w, &g_map, buf, sizeof(buf));
		if (l == 0)
			continue;
		if (out.len)
			out_put(" ", 1);
		out_anchor((uint32_t)cw->src, (uint32_t)cw->src_len);
		out_put(buf, l);
		wrote = 1;
	}
	if (wrote) {
		const char *p = clause_punctuation(terminator);
		out_put(p, strlen(p));
	}
	n_clause_words = 0;
}

static void translate_clause_phonemes(int terminator)
{
	int table = voice ? voice->phoneme_tab_ix : 0;
	ClauseWord *cw = NULL;
	char ipa[64], mnem[32];
	char phones[EVV_MAX_PHONES][EVV_PHONE_LEN];

	n_clause_words = 0;
	for (int ix = 1; ix < n_phoneme_list - 2; ix++) {
		PHONEME_LIST *plist = &phoneme_list[ix];
		PHONEME_TAB *ph = plist->ph;
		if (ph == NULL)
			continue;
		if (plist->newword & PHLIST_START_OF_WORD) {
			int src = clause_start_char + (plist->sourceix & 0x7ff);
			cw = new_word(src > 0 ? src - 1 : 0, plist->sourceix >> 11);
		}
		if (ph->code == phonSWITCH) {
			table = plist->tone_ph;
			continue;
		}
		if (ph->code == phonEND_WORD) {
			/* a word the dictionary gives as several: each is a word here */
			if (cw)
				cw = new_word(cw->src, cw->src_len);
			continue;
		}
		if (plist->type == phPAUSE || plist->type == phSTRESS || plist->type == phVIRTUAL ||
		    plist->type == phDELETED || plist->type == phINVALID)
			continue;
		if (cw == NULL)
			cw = new_word(0, 0);
		WritePhMnemonic(ipa, ph, plist, 1, NULL);
		WritePhMnemonic(mnem, ph, plist, 0, NULL);
		if (g_counting) {
			char longer[80];
			snprintf(longer, sizeof(longer), "%s%s", ipa, (plist->synthflags & SFLAG_LENGTHEN) ? "\xcb\x90" : "");
			count_phoneme(phoneme_tab_list[table].name, mnem, longer, plist->type,
			              (plist->synthflags & SFLAG_SYLLABLE) != 0);
			continue;
		}
		int n = 0;
		if (plist->synthflags & SFLAG_LENGTHEN) {
			char longer[80];
			snprintf(longer, sizeof(longer), "%s\xcb\x90", ipa); /* U+02D0, the length mark */
			n = evv_map_lookup(&g_map, NULL, NULL, longer, phones, EVV_MAX_PHONES);
		}
		if (n == 0)
			n = evv_map_lookup(&g_map, phoneme_tab_list[table].name, mnem, ipa, phones, EVV_MAX_PHONES);
		if (n == 0)
			continue;
		evv_word_add(&cw->w, &g_map, phones, n, (plist->synthflags & SFLAG_SYLLABLE) != 0,
		             plist->type == phVOWEL, engine_stress(plist->stresslevel));
	}
	write_clause(terminator);
}

static int translate_text(const char *utf8, uint32_t flags)
{
	out_reset();
	if (!translator || (!g_map_loaded && !g_counting))
		return -1;
	/* spelling: punctuation is named, in the language's own words */
	espeak_SetParameter(espeakPUNCTUATION, (flags & EVV_FE_FLAG_PUNCTUATION) ? espeakPUNCT_ALL : espeakPUNCT_NONE, 0);
	if (p_decoder == NULL)
		p_decoder = create_text_decoder();
	InitText(0);
	if (text_decoder_decode_string_multibyte(p_decoder, utf8, translator->encoding, espeakCHARS_UTF8) != ENS_OK)
		return -1;
	int guard = 0;
	while (!text_decoder_eof(p_decoder) && guard++ < 100000) {
		int tone = 0, terminator = 0;
		char *voice_change = NULL;
		SelectPhonemeTable(voice->phoneme_tab_ix);
		TranslateClauseWithTerminator(translator, &tone, &voice_change, &terminator);
		translate_clause_phonemes(terminator);
	}
	return 0;
}

/* ---- set-up ------------------------------------------------------------- */

static int start_espeak(const char *data, char *err, size_t errlen)
{
	espeak_ng_InitializePath(data);
	espeak_ng_ERROR_CONTEXT context = NULL;
	espeak_ng_STATUS st = espeak_ng_Initialize(&context);
	if (st != ENS_OK) {
		char msg[512];
		espeak_ng_GetStatusCodeMessage(st, msg, sizeof(msg));
		snprintf(err, errlen, "eSpeak NG did not start from %s: %s", data, msg);
		espeak_ng_ClearErrorContext(&context);
		return -1;
	}
	st = espeak_ng_InitializeOutput(ENOUTPUT_MODE_SYNCHRONOUS, 0, NULL);
	if (st != ENS_OK) {
		snprintf(err, errlen, "eSpeak NG output did not start");
		return -1;
	}
	return 0;
}

static int set_voice(const char *name, const char *map_path, char *err, size_t errlen)
{
	espeak_ng_STATUS st = espeak_ng_SetVoiceByName(name);
	if (st != ENS_OK) {
		snprintf(err, errlen, "eSpeak NG has no voice %s", name);
		return -1;
	}
	if (g_map_loaded)
		evv_map_free(&g_map);
	g_map_loaded = 0;
	if (map_path == NULL)
		return 0;
	if (evv_map_load(&g_map, map_path, err, errlen) != 0)
		return -1;
	g_map_loaded = 1;
	return 0;
}

/* ---- the phoneme tables, for the tools that write the maps ------------------ */

static void json_string(FILE *f, const char *s)
{
	fputc('"', f);
	for (; *s; s++) {
		unsigned char c = (unsigned char)*s;
		if (c == '"' || c == '\\')
			fprintf(f, "\\%c", c);
		else if (c < 0x20)
			fprintf(f, "\\u%04x", c);
		else
			fputc(c, f);
	}
	fputc('"', f);
}

static void dump_phonemes(FILE *f)
{
	char ipa[64], mnem[32];
	fprintf(f, "[\n");
	int first_table = 1;
	for (int t = 0; t < N_PHONEME_TABS; t++) {
		if (phoneme_tab_list[t].name[0] == 0)
			break;
		SelectPhonemeTable(t);
		fprintf(f, "%s{\"table\": ", first_table ? "" : ",\n");
		first_table = 0;
		json_string(f, phoneme_tab_list[t].name);
		fprintf(f, ", \"index\": %d, \"includes\": %d, \"phonemes\": [", t, phoneme_tab_list[t].includes);
		int first = 1;
		for (int code = 1; code < n_phoneme_tab; code++) {
			PHONEME_TAB *ph = phoneme_tab[code];
			if (ph == NULL || ph->mnemonic == 0)
				continue;
			int own = ph >= phoneme_tab_list[t].phoneme_tab_ptr &&
			          ph < phoneme_tab_list[t].phoneme_tab_ptr + phoneme_tab_list[t].n_phonemes;
			ipa[0] = mnem[0] = 0;
			if (ph->code != phonSWITCH && ph->code != phonEND_WORD) {
				WritePhMnemonic(ipa, ph, NULL, 1, NULL);
				WritePhMnemonic(mnem, ph, NULL, 0, NULL);
			}
			fprintf(f, "%s\n  {\"code\": %d, \"mnemonic\": ", first ? "" : ",", code);
			first = 0;
			json_string(f, mnem);
			fprintf(f, ", \"ipa\": ");
			json_string(f, ipa);
			fprintf(f, ", \"type\": %d, \"flags\": %u, \"place\": %u, \"own\": %d, \"length\": %d}", ph->type,
			        ph->phflags, (ph->phflags & phARTICULATION) >> 16, own, ph->std_length);
		}
		fprintf(f, "]}");
	}
	fprintf(f, "\n]\n");
}

/* ---- the pipe protocol ------------------------------------------------------ */

static int read_all(FILE *f, void *buf, size_t n)
{
	return fread(buf, 1, n, f) == n ? 0 : -1;
}

static void write_msg(FILE *f, uint32_t type, const void *a, uint32_t alen, const void *b, uint32_t blen)
{
	EvvMsgHeader h;
	h.magic = EVV_FE_MAGIC;
	h.type = type;
	h.size = alen + blen;
	fwrite(&h, sizeof(h), 1, f);
	if (alen)
		fwrite(a, 1, alen, f);
	if (blen)
		fwrite(b, 1, blen, f);
	fflush(f);
}

static void reply_status(FILE *f, int ok, const char *error)
{
	EvvStatus s;
	memset(&s, 0, sizeof(s));
	s.ok = ok;
	if (error)
		snprintf(s.error, sizeof(s.error), "%s", error);
	write_msg(f, EVV_FE_STATUS, &s, sizeof(s), NULL, 0);
}

static int serve(void)
{
#ifdef _WIN32
	_setmode(_fileno(stdin), _O_BINARY);
	_setmode(_fileno(stdout), _O_BINARY);
#endif
	char *payload = NULL;
	size_t cap = 0;
	for (;;) {
		EvvMsgHeader h;
		if (read_all(stdin, &h, sizeof(h)) != 0 || h.magic != EVV_FE_MAGIC || h.size > EVV_FE_MAX_PAYLOAD)
			break;
		if (h.size + 1 > cap) {
			cap = h.size + 1;
			char *p = (char *)realloc(payload, cap);
			if (!p)
				break;
			payload = p;
		}
		if (h.size && read_all(stdin, payload, h.size) != 0)
			break;
		payload[h.size] = 0;
		if (h.type == EVV_FE_QUIT)
			break;
		if (h.type == EVV_FE_VOICE) {
			/* "voice\0map path\0" */
			const char *name = payload;
			const char *map = payload + strlen(payload) + 1;
			char err[200] = "";
			if (map >= payload + h.size + 1 || set_voice(name, map, err, sizeof(err)) != 0)
				reply_status(stdout, 0, err[0] ? err : "bad voice request");
			else
				reply_status(stdout, 1, NULL);
			continue;
		}
		if (h.type == EVV_FE_TRANSLATE) {
			if (h.size < sizeof(uint32_t)) {
				reply_status(stdout, 0, "bad translate request");
				continue;
			}
			const char *text = payload + sizeof(uint32_t);
			uint32_t flags;
			memcpy(&flags, payload, sizeof flags);
			if (translate_text(text, flags) != 0) {
				reply_status(stdout, 0, "no voice has been set");
				continue;
			}
			EvvResultHead r;
			r.n_anchors = (uint32_t)out.n_anchors;
			r.text_len = (uint32_t)out.len;
			uint32_t alen = (uint32_t)(out.n_anchors * sizeof(EvvAnchor));
			/* head, anchors, text */
			EvvMsgHeader hh;
			hh.magic = EVV_FE_MAGIC;
			hh.type = EVV_FE_RESULT;
			hh.size = (uint32_t)sizeof(r) + alen + r.text_len;
			fwrite(&hh, sizeof(hh), 1, stdout);
			fwrite(&r, sizeof(r), 1, stdout);
			if (alen)
				fwrite(out.anchors, 1, alen, stdout);
			if (r.text_len)
				fwrite(out.text, 1, r.text_len, stdout);
			fflush(stdout);
			continue;
		}
		reply_status(stdout, 0, "unknown request");
	}
	free(payload);
	return 0;
}

/* ---- the command line ---------------------------------------------------------- */

static const char *arg_value(int argc, char **argv, const char *name)
{
	for (int i = 1; i + 1 < argc; i++)
		if (strcmp(argv[i], name) == 0)
			return argv[i + 1];
	return NULL;
}

static int has_arg(int argc, char **argv, const char *name)
{
	for (int i = 1; i < argc; i++)
		if (strcmp(argv[i], name) == 0)
			return 1;
	return 0;
}

#ifdef _WIN32
/* The command line in UTF-8, since the ANSI one cannot carry most languages. */
static char **utf8_argv(int *argc_out)
{
	int argc = 0;
	LPWSTR *w = CommandLineToArgvW(GetCommandLineW(), &argc);
	char **argv = (char **)calloc((size_t)argc + 1, sizeof(char *));
	for (int i = 0; i < argc; i++) {
		int n = WideCharToMultiByte(CP_UTF8, 0, w[i], -1, NULL, 0, NULL, NULL);
		argv[i] = (char *)malloc((size_t)n);
		WideCharToMultiByte(CP_UTF8, 0, w[i], -1, argv[i], n, NULL, NULL);
	}
	LocalFree(w);
	*argc_out = argc;
	return argv;
}
#endif

static char *read_file(const char *path)
{
	FILE *f = fopen(path, "rb");
	if (!f)
		return NULL;
	fseek(f, 0, SEEK_END);
	long n = ftell(f);
	fseek(f, 0, SEEK_SET);
	char *s = (char *)malloc((size_t)n + 1);
	if (s && fread(s, 1, (size_t)n, f) != (size_t)n) {
		free(s);
		s = NULL;
	}
	if (s)
		s[n] = 0;
	fclose(f);
	return s;
}

int main(int argc, char **argv)
{
#ifdef _WIN32
	argv = utf8_argv(&argc);
	/* never a crash dialog in front of a screen reader */
	SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX);
#endif
	const char *data = arg_value(argc, argv, "--data");
	if (!data) {
		fprintf(stderr, "usage: OpenEvvFrontend --data DIR (--serve | --dump-phonemes | --voice NAME --map FILE "
		                "(--text TEXT | --file FILE))\n");
		return 2;
	}
	char err[512];
	if (start_espeak(data, err, sizeof(err)) != 0) {
		if (has_arg(argc, argv, "--serve")) {
			/* say why to whoever is listening, then go */
			reply_status(stdout, 0, err);
		}
		fprintf(stderr, "%s\n", err);
		return 1;
	}
	if (has_arg(argc, argv, "--serve"))
		return serve();
	if (has_arg(argc, argv, "--dump-phonemes")) {
		dump_phonemes(stdout);
		return 0;
	}
	const char *name = arg_value(argc, argv, "--voice");
	const char *map = arg_value(argc, argv, "--map");
	if (has_arg(argc, argv, "--stats")) {
		/* --voice NAME --stats FILE...: every line of each file read, and
		   each phoneme counted, as JSON */
		if (!name || set_voice(name, NULL, err, sizeof(err)) != 0) {
			fprintf(stderr, "%s\n", name ? err : "--stats needs --voice");
			return 1;
		}
		g_counting = 1;
		for (int i = 1; i < argc; i++) {
			if (strcmp(argv[i], "--stats") != 0)
				continue;
			for (int j = i + 1; j < argc && strncmp(argv[j], "--", 2) != 0; j++) {
				char *all = read_file(argv[j]);
				if (all)
					translate_text(all, 0);
				free(all);
			}
		}
		printf("[\n");
		for (int i = 0; i < g_n_stats; i++) {
			printf("%s{\"table\": ", i ? ",\n" : "");
			json_string(stdout, g_stats[i].table);
			printf(", \"mnemonic\": ");
			json_string(stdout, g_stats[i].mnem);
			printf(", \"ipa\": ");
			json_string(stdout, g_stats[i].ipa);
			printf(", \"type\": %d, \"syllabic\": %d, \"count\": %d}", g_stats[i].type, g_stats[i].syllabic,
			       g_stats[i].count);
		}
		printf("\n]\n");
		return 0;
	}
	const char *text = arg_value(argc, argv, "--text");
	const char *file = arg_value(argc, argv, "--file");
	char *owned = NULL;
	if (file)
		text = owned = read_file(file);
	if (!name || !map || !text) {
		fprintf(stderr, "--voice, --map and --text or --file are all needed\n");
		return 2;
	}
	if (set_voice(name, map, err, sizeof(err)) != 0) {
		fprintf(stderr, "%s\n", err);
		return 1;
	}
	translate_text(text, has_arg(argc, argv, "--punctuation") ? EVV_FE_FLAG_PUNCTUATION : 0);
	if (has_arg(argc, argv, "--anchors")) {
		for (size_t i = 0; i < out.n_anchors; i++)
			printf("%u\t%u+%u\n", out.anchors[i].out_offset, out.anchors[i].src_offset, out.anchors[i].src_length);
	}
	printf("%s\n", out.text ? out.text : "");
	free(owned);
	return 0;
}
