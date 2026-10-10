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
 *        prints what a text becomes, with each word's position;
 *        --spell has it spelled, every character by its name;
 *        --phonemes lets it name eSpeak NG's phonemes in [[double brackets]]
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
#include "intonation.h"
#include "phoneme.h"
#include "readclause.h"
#include "speech.h"
#include "synthdata.h"
#include "synthesize.h"
#include "translate.h"
#include "voice.h"

#include "evv_map.h"
#include "frontend_proto.h"

/* eSpeak NG's compat/stdio.h makes snprintf MSVC's _snprintf, which leaves a
   string it cuts unterminated and returns -1. The C99 one (MSVC 2015 and
   later) terminates it and returns the length wanted, which the checks for a
   cut here rely on. Only a cut string is said differently, and no present
   pack has one (the R15 review of Phase 3A). */
#ifdef snprintf
#undef snprintf
#endif

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
		if (!t) {
			evv_diag(EVV_DIAG_LOSS, "out-of-memory", "%u bytes of the annotation dropped", (unsigned)l);
			return;
		}
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
		if (!a) {
			evv_diag(EVV_DIAG_LOSS, "out-of-memory", "a word's position dropped");
			return;
		}
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
	int pause_ms; /* a pause typed before it in IPA (extIPA's (.), D83) */
} ClauseWord;

#define MAX_CLAUSE_WORDS 400
static ClauseWord clause_words[MAX_CLAUSE_WORDS];
static int n_clause_words;

static EvvMap g_map;
static int g_map_loaded;
static int g_load_reported = 1; /* 0: what reading the map reported is still to be sent */
static int g_src_shift;     /* characters put in front of the text, which no position counts */
static const char *g_input; /* the text being read, as it was given */

/* The stretches of the text that are to be spelled, in characters from the
   start of the text as it was given. */
typedef struct {
	int from, to;
} Stretch;
#define MAX_SPELLED 64
static Stretch g_spelled[MAX_SPELLED];
static int g_n_spelled;

/* eSpeak NG is told to say characters by a command in the text: the
   character with the number one, a number and Y. 18 to 20 are the ways of
   spelling; Y with no number, or nought, ends it. `shift' is how many
   characters were put in front of the text that was given. */
static void find_spelled(const char *text, int shift)
{
	int at = 0, open = -1;
	g_n_spelled = 0;
	for (const unsigned char *p = (const unsigned char *)text; *p;) {
		if (*p == 1) {
			const unsigned char *q = p + 1;
			int value = 0, digits = 0;
			while (*q >= '0' && *q <= '9') {
				value = value * 10 + (*q - '0');
				q++;
				digits++;
			}
			if (*q == 'Y') {
				int after = at + 1 + digits + 1 - shift;
				if ((value & 0xf0) == 0x10) {
					if (open < 0)
						open = after < 0 ? 0 : after;
				} else if (open >= 0 && g_n_spelled < MAX_SPELLED) {
					g_spelled[g_n_spelled].from = open;
					g_spelled[g_n_spelled].to = at - shift;
					g_n_spelled++;
					open = -1;
				} else if (open >= 0) {
					evv_diag(EVV_DIAG_LOSS, "spelled-full", "more than %d stretches to spell; the rest are read as words",
					         MAX_SPELLED);
					open = -1;
				}
			}
		}
		p++;
		while ((*p & 0xc0) == 0x80)
			p++;
		at++;
	}
	if (open >= 0 && g_n_spelled < MAX_SPELLED) {
		g_spelled[g_n_spelled].from = open;
		g_spelled[g_n_spelled].to = at - shift + 1;
		g_n_spelled++;
	} else if (open >= 0) {
		evv_diag(EVV_DIAG_LOSS, "spelled-full", "more than %d stretches to spell; the rest are read as words",
		         MAX_SPELLED);
	}
}

static int is_spelled(int character)
{
	for (int i = 0; i < g_n_spelled; i++)
		if (character >= g_spelled[i].from && character < g_spelled[i].to)
			return 1;
	return 0;
}

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
	if (n_clause_words >= MAX_CLAUSE_WORDS) {
		evv_diag(EVV_DIAG_LOSS, "clause-words-full", "more than %d words in a clause; the rest join the last",
		         MAX_CLAUSE_WORDS);
		return &clause_words[MAX_CLAUSE_WORDS - 1];
	}
	ClauseWord *cw = &clause_words[n_clause_words++];
	evv_word_clear(&cw->w);
	cw->src = src;
	cw->src_len = src_len;
	cw->pause_ms = 0;
	return cw;
}

/* How a clause ends, as the markup says it: a statement, a question, an
   exclamation, or a sentence that goes on. */
static char phrase_ending(int terminator)
{
	switch (terminator & CLAUSE_INTONATION_TYPE) {
	case CLAUSE_INTONATION_QUESTION:
		return 'q';
	case CLAUSE_INTONATION_EXCLAMATION:
		return 'e';
	case CLAUSE_INTONATION_COMMA:
		return 'c';
	case CLAUSE_INTONATION_NONE:
		return 'c';
	default:
		return (terminator & CLAUSE_TYPE) == CLAUSE_TYPE_CLAUSE ? 'c' : 's';
	}
}

static void append_phones(EvvWord *to, const EvvWord *from, int at_front)
{
	if (to->n + from->n > EVV_WORD_MAX) {
		evv_diag(EVV_DIAG_LOSS, "word-too-long", "a word with no vowel of %d phones does not fit beside its neighbour; "
		         "it is dropped", from->n);
		return;
	}
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

/* Where in a text in UTF-8 the character with a number begins. */
static const char *at_character(const char *s, int n)
{
	while (*s && n > 0) {
		s++;
		while ((*s & 0xc0) == 0x80)
			s++;
		n--;
	}
	return s;
}

static int is_letter_byte(unsigned char c)
{
	return c >= 0x80 || (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z');
}

/* Whether the clause is asked with a question word: one of the words the
   map lists, where the map says such a word counts. */
static int asked_with_a_word(void)
{
	if (!g_map.n_ask || !g_input)
		return 0;
	int seen = 0;
	int last_src = -1;
	for (int i = 0; i < n_clause_words; i++) {
		const ClauseWord *cw = &clause_words[i];
		if (cw->src == last_src || cw->src_len <= 0)
			continue;
		last_src = cw->src;
		const char *a = at_character(g_input, cw->src);
		const char *b = at_character(a, cw->src_len);
		/* the word without what stands round it */
		while (a < b && !is_letter_byte((unsigned char)*a))
			a++;
		while (b > a && !is_letter_byte((unsigned char)b[-1]))
			b--;
		if (b <= a)
			continue;
		seen++;
		if (g_map.ask_where == 1 && seen > 3)
			return 0;
		if (evv_map_asks(&g_map, a, (size_t)(b - a), seen == 1))
			return 1;
	}
	return 0;
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
		} else if (!g_map.schwa[0]) {
			evv_diag(EVV_DIAG_LOSS, "word-no-nucleus", "a word of %d phones beginning %s has no vowel, nothing to "
			         "lean on and the map no schwa; it is dropped", cw->w.n, cw->w.ph[0].phone);
		} else {
			/* nothing to lean on: give it a vowel */
			evv_diag(EVV_DIAG_NOTE, "schwa-inserted", "%s for a word with no vowel beginning %s", g_map.schwa,
			         cw->w.ph[0].phone);
			EvvMapPhone phones[1];
			memset(phones, 0, sizeof(phones));
			snprintf(phones[0].name, sizeof(phones[0].name), "%s", g_map.schwa);
			EvvWord tmp = cw->w;
			evv_word_clear(&cw->w);
			evv_word_add(&cw->w, &g_map, phones, 1, 1, 1, 1, NULL);
			append_phones(&cw->w, &tmp, 0);
		}
	}
	static char buf[EVV_WORD_MAX * 48 + 64];
	int wrote = 0;
	/* What is being spelled is said as people spell: a letter, a breath, the
	   next letter. eSpeak NG makes that pause in its own sound; here it is a
	   comma, which is what the engine pauses at. The words of one letter's
	   name ("a", "con", "acento") stay together: they are read from one
	   place in the text, or the later of them from the space after it. */
	int last_src = -1;
	for (int i = 0; i < n_clause_words; i++) {
		ClauseWord *cw = &clause_words[i];
		size_t l = evv_word_annotate(&cw->w, &g_map, buf, sizeof(buf));
		if (l == 0)
			continue;
		int same_letter = cw->src == last_src;
		if (!same_letter && g_input != NULL) {
			char c = *at_character(g_input, cw->src);
			same_letter = c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == 0;
		}
		if (wrote && !same_letter && is_spelled(cw->src)) {
			if (g_map.accent)
				out_put("{P c}", 5);
			out_put(",", 1);
		}
		if (out.len > 0)
			out_put(" ", 1);
		if (cw->pause_ms > 0) {
			/* a pause typed in IPA: the engine's own pause annotation, so long */
			char pz[24];
			int pl = snprintf(pz, sizeof(pz), "`p%d ", cw->pause_ms);
			out_put(pz, (size_t)pl);
		}
		out_anchor((uint32_t)cw->src, (uint32_t)cw->src_len);
		out_put(buf, l);
		wrote = 1;
		last_src = cw->src;
	}
	if (wrote) {
		if (g_map.accent) {
			/* how the phrase ends, for whoever is making its melody */
			char ending = phrase_ending(terminator);
			if (ending == 'q' && asked_with_a_word())
				ending = 'w';
			char group[8] = {'{', 'P', ' ', ending, '}', 0};
			out_put(group, 5);
		}
		const char *p = clause_punctuation(terminator);
		out_put(p, strlen(p));
	}
	n_clause_words = 0;
}

static void translate_clause_phonemes(int terminator, int clause_tone)
{
	int table = voice ? voice->phoneme_tab_ix : 0;
	ClauseWord *cw = NULL;
	char ipa[64], mnem[32], tone_name[32];
	EvvMapPhone phones[EVV_MAX_PHONES];

	/* A language with tones changes them by what stands beside them: the
	   third tone of Mandarin before another third tone, the neutral tone
	   after each of the four. eSpeak NG does that where it works out the
	   pitch, which is after the translation this program stops at, so it is
	   asked to here. Nothing else it sets there is read. */
	if (translator && translator->langopts.tone_language == 1 && n_phoneme_list > 2)
		CalcPitches(translator, clause_tone);

	n_clause_words = 0;
	for (int ix = 1; ix < n_phoneme_list - 2; ix++) {
		PHONEME_LIST *plist = &phoneme_list[ix];
		PHONEME_TAB *ph = plist->ph;
		if (ph == NULL)
			continue;
		if (plist->newword & PHLIST_START_OF_WORD) {
			int src = clause_start_char + (plist->sourceix & 0x7ff) - 1 - g_src_shift;
			int len = plist->sourceix >> 11;
			if (src < 0) {
				/* the word began among the characters put in front of the text */
				len = len + src > 0 ? len + src : 0;
				src = 0;
			}
			cw = new_word(src, len);
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
		int n = 0, matched = 0;
		if (plist->synthflags & SFLAG_LENGTHEN) {
			char longer[80];
			snprintf(longer, sizeof(longer), "%s\xcb\x90", ipa); /* U+02D0, the length mark */
			/* a trial: reported only if it is what is said */
			evv_diag_quiet = 1;
			n = evv_map_lookup(&g_map, NULL, NULL, longer, phones, EVV_MAX_PHONES);
			evv_diag_quiet = 0;
			if (n != 0)
				n = evv_map_lookup(&g_map, NULL, NULL, longer, phones, EVV_MAX_PHONES);
			else
				evv_diag(EVV_DIAG_LOSS, "length-dropped", "%s:%s /%s/ said without its length",
				         phoneme_tab_list[table].name, mnem, longer);
		}
		if (n == 0) {
			n = evv_map_lookup_ex(&g_map, phoneme_tab_list[table].name, mnem, ipa, phones, EVV_MAX_PHONES, &matched);
			if (!matched)
				evv_diag(EVV_DIAG_LOSS, "phoneme-dropped", "%s:%s /%s/ has no line in the map",
				         phoneme_tab_list[table].name, mnem, ipa);
		}
		if (n == 0)
			continue;
		/* the tone the syllable carries, under the name the map gives it */
		const char *tone = NULL;
		if (plist->type == phVOWEL && plist->tone_ph != 0 && g_map.n_tone_ids > 0) {
			PHONEME_TAB *tph = TonePhoneme(plist);
			if (tph != NULL) {
				tone_name[0] = 0;
				WritePhMnemonic(tone_name, tph, plist, 0, NULL);
				tone = evv_map_tone(&g_map, tone_name);
				if (tone == NULL)
					evv_diag(EVV_DIAG_LOSS, "tone-unknown", "tone %s, which the map does not name, said as no tone",
					         tone_name);
			} else {
				evv_diag(EVV_DIAG_LOSS, "tone-unknown", "tone number %d, which eSpeak NG gives no phoneme, said as "
				         "no tone", plist->tone_ph);
			}
		} else if (plist->type == phVOWEL && plist->tone_ph != 0 && translator &&
		           translator->langopts.tone_language == 1) {
			evv_diag(EVV_DIAG_LOSS, "tone-unsupported", "a tone, and the map defines none: said as no tone");
		}
		int stress = engine_stress(plist->stresslevel);
		/* Where every syllable is a word and has a tone, a syllable's weight
		   is its tone's: full, or light as the neutral tone is. */
		if (tone != NULL && g_map.apart)
			stress = evv_map_tone_is_weak(&g_map, tone) ? 0 : 1;
		evv_word_add(&cw->w, &g_map, phones, n, (plist->synthflags & SFLAG_SYLLABLE) != 0,
		             plist->type == phVOWEL, stress, tone);
	}
	write_clause(terminator);
}

/* Text to be spelled: every character by its name in the language, which is
   what somebody moving through a line a character at a time has to hear.
   eSpeak NG is told by the command it keeps for that, written in front of
   the text: the character with the number one, the number of the way of
   saying (18: characters), and Y. The same command without a number ends
   it. The host writes them itself around what is to be spelled; this is for
   a whole text. */
#define SPELL_ON "\001" "18Y"
#define SPELL_ON_LEN 4

static void put_header(void);

static int translate_text(const char *utf8, uint32_t flags)
{
	out_reset();
	/* what the map reported when it was read goes with the first result after */
	if (!g_load_reported)
		g_load_reported = 1;
	else
		evv_diag_clear();
	g_src_shift = 0;
	g_input = utf8;
	if (!translator || (!g_map_loaded && !g_counting))
		return -1;
	/* spelling: punctuation is named, in the language's own words */
	espeak_SetParameter(espeakPUNCTUATION, (flags & EVV_FE_FLAG_PUNCTUATION) ? espeakPUNCT_ALL : espeakPUNCT_NONE, 0);
	if (p_decoder == NULL)
		p_decoder = create_text_decoder();
	char *spelled = NULL;
	if (flags & EVV_FE_FLAG_SPELL) {
		size_t n = strlen(utf8);
		spelled = (char *)malloc(n + SPELL_ON_LEN + 1);
		if (spelled) {
			memcpy(spelled, SPELL_ON, SPELL_ON_LEN);
			memcpy(spelled + SPELL_ON_LEN, utf8, n + 1);
			utf8 = spelled;
			g_src_shift = SPELL_ON_LEN;
		}
	}
	find_spelled(utf8, g_src_shift);
	InitText(0);
	if (text_decoder_decode_string_multibyte(p_decoder, utf8, translator->encoding, espeakCHARS_UTF8) != ENS_OK) {
		free(spelled);
		return -2;
	}
	int guard = 0;
	while (!text_decoder_eof(p_decoder)) {
		if (guard++ >= 100000) {
			evv_diag(EVV_DIAG_LOSS, "text-cut", "more than 100000 clauses; the rest is not read");
			break;
		}
		int tone = 0, terminator = 0;
		char *voice_change = NULL;
		SelectPhonemeTable(voice->phoneme_tab_ix);
		TranslateClauseWithTerminator(translator, &tone, &voice_change, &terminator);
		translate_clause_phonemes(terminator, tone);
	}
	free(spelled);
	put_header();
	return 0;
}

/* What the phones were meant to be begins the text: the language, and
   those of its sounds and tones that these words have in them. It is
   written last, when it is known which they are, and put first. */
static void put_header(void)
{
	if (g_map_loaded && g_map.accent && !g_counting && out.len > 0) {
		size_t hl = 0;
		char *h = evv_map_begin(&g_map, &hl);
		if (h && hl) {
			size_t body = out.len;
			out_put(h, hl); /* makes the room */
			if (out.len == body + hl) {
				memmove(out.text + hl, out.text, body);
				memcpy(out.text, h, hl);
				out.text[out.len] = 0;
				for (size_t i = 0; i < out.n_anchors; i++)
					out.anchors[i].out_offset += (uint32_t)hl;
			}
		}
		free(h);
	}
}

/* IPA in (C4, the serving front-end's half of the IPA reader of C2): words
   by spaces, ˈ and ˌ for the stress of the syllable they stand before, `.'
   between syllables, and each segment a chart letter with the marks after it,
   looked up whole and otherwise composed (evv_map.c). Anything that is not a
   letter the map lists and stands where a letter should is reported. A mark
   with no `mod' line is left off and reported, never dropped without a word.
   Pitch typed in IPA (C2, C5), from a map with `tonemark', `register' and
   `slope' lines: tone letters and tone diacritics give the syllable they
   belong to a tone of its own, made on the spot; a register step (downstep,
   upstep) moves every tone after it to the end of the phrase; a global rise
   or fall gives each syllable after it to the end of the phrase a tone a step
   higher or lower than the one before. `|' ends a minor group and `‖' a major
   one (a phrase each); `‿' links, and is otherwise nothing. A `.' inside a
   word says where the next syllable begins. A tie bar (U+0361 above, U+035C
   below) makes the letters on each side one segment, looked up whole (an
   affricate the template has, `t͡s'); a tied pair the map has no line for is
   said one side after the other, each with its own marks, and reported so.
   extIPA's sliding mark (U+0362) joins two letters the same way, and is a
   mark of each (its `mod' line gives the two the time of one segment). */
static int utf8_char_len(unsigned char c)
{
	return c < 0x80 ? 1 : (c & 0xe0) == 0xc0 ? 2 : (c & 0xf0) == 0xe0 ? 3 : (c & 0xf8) == 0xf0 ? 4 : 1;
}

#ifdef _WIN32
#pragma comment(lib, "Normaliz.lib")
#endif

/* IPA as the reader of C2 takes it (engine/ipa/reader.py, ipa/aliases.toml):
   Unicode's canonical decomposition, then c and a cedilla put back together
   as the one chart letter it would break, and Latin g read as the chart's
   script g. Canonically equal input therefore reads the same. The caller
   frees the result. */
static char *ipa_normalize(const char *utf8)
{
	char *out = NULL;
#ifdef _WIN32
	int wn = MultiByteToWideChar(CP_UTF8, 0, utf8, -1, NULL, 0);
	wchar_t *w = (wchar_t *)malloc(sizeof(wchar_t) * (size_t)wn);
	if (w && MultiByteToWideChar(CP_UTF8, 0, utf8, -1, w, wn) > 0) {
		/* the combining marks of Unicode 14 (extIPA's partial voicing ◌᫃ ◌᫄
		   among them) are unknown to Windows' tables, which leave them where
		   they stand: each is put in order as a Hebrew accent of its class
		   (U+0591 220, U+0592 230; UnicodeData.txt), never met in IPA, and
		   given back after. The reader has the same list (reader.py LATE_CCC). */
		static const wchar_t late[] = { 0x1ac1, 0x1ac2, 0x1ac3, 0x1ac4, 0x1ac5, 0x1ac6, 0x1ac7,
		                                0x1ac8, 0x1ac9, 0x1aca, 0x1acb, 0x1acc, 0x1acd, 0x1ace };
		static const unsigned char late_ccc[] = { 230, 230, 220, 220, 230, 230, 230,
		                                          230, 230, 220, 230, 230, 230, 230 };
		const int n_late = (int)(sizeof(late) / sizeof(late[0]));
		int stood_in = !wcschr(w, 0x0591) && !wcschr(w, 0x0592);
		wchar_t *orig = stood_in ? _wcsdup(w) : NULL; /* the marks themselves, in the order written */
		int n_in = 0;
		if (orig)
			for (int i = 0; w[i]; i++)
				for (int k = 0; k < n_late; k++)
					if (w[i] == late[k]) {
						w[i] = late_ccc[k] == 220 ? 0x0591 : 0x0592;
						n_in++;
					}
		int dn = NormalizeString(NormalizationD, w, -1, NULL, 0);
		wchar_t *d = dn > 0 ? (wchar_t *)malloc(sizeof(wchar_t) * (size_t)dn) : NULL;
		if (d && (dn = NormalizeString(NormalizationD, w, -1, d, dn)) > 0) {
			if (n_in) {
				/* back to the marks: canonical ordering is stable, so the
				   stand-ins of one class keep the order their marks were in
				   (a pointer into the marks as written for each class) */
				int j[2] = { 0, 0 };
				for (int i = 0; d[i]; i++)
					if (d[i] == 0x0591 || d[i] == 0x0592) {
						int below = d[i] == 0x0591;
						for (; orig[j[below]]; j[below]++) {
							int k = 0;
							while (k < n_late && orig[j[below]] != late[k])
								k++;
							if (k < n_late && (late_ccc[k] == 220) == below) {
								d[i] = orig[j[below]++];
								break;
							}
						}
					}
			}
			/* the affricate ligatures the IPA withdrew are their two
			   letters joined by a tie bar (ipa/aliases.toml): one code
			   point becomes three, so the result has a buffer of its own */
			static const wchar_t lig[][4] = {
				{ 0x02a6, L't', 0x0361, L's' }, { 0x02a7, L't', 0x0361, 0x0283 },
				{ 0x02a3, L'd', 0x0361, L'z' }, { 0x02a4, L'd', 0x0361, 0x0292 },
				{ 0x02a8, L't', 0x0361, 0x0255 }, { 0x02a5, L'd', 0x0361, 0x0291 },
			};
			wchar_t *e = (wchar_t *)malloc(sizeof(wchar_t) * (size_t)(3 * dn + 1));
			int k = 0;
			if (e != NULL) {
				for (int i = 0; d[i]; i++) {
					int n = 0;
					while (n < (int)(sizeof(lig) / sizeof(lig[0])) && d[i] != lig[n][0])
						n++;
					if (n < (int)(sizeof(lig) / sizeof(lig[0]))) {
						e[k++] = lig[n][1];
						e[k++] = lig[n][2];
						e[k++] = lig[n][3];
					} else
						e[k++] = d[i];
				}
				e[k] = 0;
				free(d);
				d = e;
				k = 0;
			}
			for (int i = 0; d[i]; i++) {
				/* the cedilla may come after other marks of c: canonical order puts a mark of a
				   lower class (an overlay, class 1) before it, and ç must still be ç */
				int ced = 0;
				if (d[i] == L'c')
					for (int j = i + 1; d[j] >= 0x0300 && d[j] <= 0x036f; j++)
						if (d[j] == 0x0327) {
							ced = j;
							break;
						}
				if (ced) {
					d[k++] = 0x00e7;
					for (int j = i + 1; j < ced; j++)
						d[k++] = d[j];
					i = ced;
				} else
					d[k++] = d[i] == L'g' ? 0x0261 : d[i];
			}
			d[k] = 0;
			int un = WideCharToMultiByte(CP_UTF8, 0, d, -1, NULL, 0, NULL, NULL);
			out = (char *)malloc((size_t)un);
			if (out)
				WideCharToMultiByte(CP_UTF8, 0, d, -1, out, un, NULL, NULL);
		} else {
			evv_diag(EVV_DIAG_LOSS, "ipa-not-normalized", "the text could not be put in canonical form; read as given");
		}
		free(d);
		free(orig);
	}
	free(w);
#endif
	if (!out) {
		size_t n = strlen(utf8) + 1;
		out = (char *)malloc(n);
		if (out)
			memcpy(out, utf8, n);
	}
	return out;
}

/* A combining mark: U+0300 to 036F, U+1DC0 to 1DFF. */
static int is_combining(const unsigned char *p, int l)
{
	if (l == 2 && (p[0] == 0xcc || (p[0] == 0xcd && p[1] <= 0xaf)))
		return 1;
	return l == 3 && p[0] == 0xe1 && p[1] == 0xb7;
}

/* The tone typed for a syllable, put on its nucleus: the levels typed, or,
   under a slope with none typed, the middle of the voice; moved by the
   register and by how far the slope has gone. */
static void put_tone(EvvPhone *nuc, int *levels, int *n, int reg, int slope, int *slope_at)
{
	if (nuc == NULL || (*n == 0 && slope == 0)) {
		if (nuc != NULL)
			*n = 0;
		return;
	}
	int mid[1] = {3};
	const int *lv = *n ? levels : mid;
	int k = *n ? *n : 1;
	const char *id = evv_map_ipa_tone(&g_map, lv, k, reg + *slope_at, reg + *slope_at + slope);
	if (id)
		snprintf(nuc->tone, sizeof(nuc->tone), "%s", id);
	else
		evv_diag(EVV_DIAG_LOSS, "tone-dropped", "no room for another tone; a syllable is said without its own");
	*slope_at += slope;
	*n = 0;
}

/* extIPA's reiteration (p\p\p, Tier B): each `\' becomes the IPA the map's
   `reiterate' line gives for the class of the letter before it, and a
   syllable break, so that the sound after it is said again from its start.
   A `\' with no letter before it, or no line for its class, is left off and
   reported. A stress mark typed before a sound that is reiterated before its
   vowel (ˈp\p\pa) goes to the repetition said last, the one with the vowel.
   Returns the text to read, or NULL when there is nothing to expand; then
   `origin' gives, for each character of it, the character of the text given
   that it stands for (what a position reported to the caller counts). The
   caller frees both. */
static int is_space_or_group(char c)
{
	return c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '|';
}

static char *expand_reiteration(const char *utf8, int **origin)
{
	*origin = NULL;
	if (!strchr(utf8, '\\') || (!g_map.reiterate[0][0] && !g_map.reiterate[1][0]))
		return NULL;
	size_t n = strlen(utf8), k = 0;
	size_t room = n * (sizeof(g_map.reiterate[0]) + 3) + 1;
	char *out = (char *)malloc(room);
	int *org = (int *)malloc(sizeof(int) * room);
	if (!out || !org) {
		free(out);
		free(org);
		return NULL;
	}
	int cls = 0, kc = 0, oc = 0;      /* characters written, characters read */
	const char *held = NULL, *held_to = NULL;
	for (const char *p = utf8; *p;) {
		int l = utf8_char_len((unsigned char)*p);
		if (l == 2 && (unsigned char)p[0] == 0xcb && ((unsigned char)p[1] == 0x88 || (unsigned char)p[1] == 0x8c)) {
			/* the last `\' before this word's next vowel, if there is one */
			const char *last = NULL;
			for (const char *q = p + 2; *q && !is_space_or_group(*q); q += utf8_char_len((unsigned char)*q)) {
				const EvvLetter *v = evv_map_letter(&g_map, q, (size_t)utf8_char_len((unsigned char)*q));
				if (*q == '\\')
					last = q;
				else if (v && v->cls == 'v')
					break;
			}
			if (last) {
				held = p;
				held_to = last;
				p += l;
				oc++;
				continue;
			}
		}
		if (*p == '\\') {
			const char *say = cls ? g_map.reiterate[cls == 'v'] : "";
			if (say[0]) {
				for (const char *s = say; *s; s += utf8_char_len((unsigned char)*s))
					org[kc++] = oc;
				memcpy(out + k, say, strlen(say));
				k += strlen(say);
				out[k++] = '.';
				org[kc++] = oc;
			} else
				evv_diag(EVV_DIAG_LOSS, "reiteration-left-off", "a `\\' with %s; left off",
				         cls ? "no reiterate line for its letter's class" : "no letter before it");
			if (p == held_to) {
				memcpy(out + k, held, 2);
				k += 2;
				org[kc++] = (int)(oc); /* stands for the `\' after which it is said */
				held = held_to = NULL;
			}
			p++;
			oc++;
			continue;
		}
		const EvvLetter *lt = evv_map_letter(&g_map, p, (size_t)l);
		if (lt)
			cls = lt->cls;
		else if (is_space_or_group(*p))
			cls = 0;
		memcpy(out + k, p, (size_t)l);
		k += (size_t)l;
		org[kc++] = oc++;
		p += l;
	}
	out[k] = 0;
	org[kc] = oc;
	*origin = org;
	return out;
}

/* ---- a stretch under a label (extIPA's and VoQS's braces, D83) ----

   `{L ... L}': every letter between the braces is composed with the marks the
   map's `label' lines give L, as if they were written after it (a mark of its
   own written on a letter comes before them). A label is read as the map's
   labels one after another, the longest first (V̰! is V, ̰ and !). A label is
   a base (V, F, L̞, f, allegro) or a mark that goes on the base before it (̰,
   !, ʲ); a degree, 1 2 or 3 (VoQS: slight, moderate, extreme; none written:
   2), goes on the symbol written after it, the base and its marks, and no
   further ({1V!L̞ ...} is a slight V! and L̞). The same labels written again,
   in any order, just before the closing brace are passed over. Labels of one
   group (the map's `g=': extIPA's loudness, its tempo) do not add up: the
   innermost stretch's is said ({f ... {p ... p} ... f} is piano inside). A
   ramp's mark goes from its first step on the stretch's first letter to its
   last on the last (crescendo). `(' and `⸨' open a stretch under the labels
   `()' and `⸨⸩' (extIPA's silent articulation and extraneous noise), unless
   `(' begins a pause: one the map lists ((.) (..) (…)), or a time in seconds
   ((1.3 sec), (1.3), 60 at most), said as the engine's own pause before the
   next word. Stretches may hold stretches, four deep. A map with no `label'
   or `pause' lines reads braces and parentheses as it did before (D83). */

#define SPAN_LABELS 8

typedef struct {
	char close[4];               /* what closes it */
	int label[SPAN_LABELS];      /* its labels (the map's), and each one's degree */
	int degree[SPAN_LABELS];
	int n;
	int letters;                 /* a ramp: the letters in the stretch, and how many are said */
	int at;
} Span;

static Span g_spans[4];
static int g_n_spans;
static int g_pause_ms; /* a pause typed and not yet given to a word */

static int is_space(char c)
{
	return c == ' ' || c == '\t' || c == '\n' || c == '\r';
}

static int is_tie(const char *p)
{
	return (unsigned char)p[0] == 0xcd && ((unsigned char)p[1] == 0xa1 || (unsigned char)p[1] == 0x9c ||
	                                       (unsigned char)p[1] == 0xa2);
}

/* The labels written as the `len' bytes at tok, each with its degree, into
   label[] and degree[]; their number, or -1 where any of it is no label the
   map lists (and `bad' then points at it). */
static int read_labels(const char *tok, size_t len, int *label, int *degree, int max, const char **bad)
{
	size_t i = 0;
	int n = 0, pending = 0, cur = 2;
	if (len == 0)
		return -1;
	while (i < len) {
		if (tok[i] >= '1' && tok[i] <= '3' && i + 1 < len) {
			pending = tok[i] - '0'; /* the degree of the symbol after it */
			i++;
			continue;
		}
		int best = -1;
		size_t best_l = 0;
		for (size_t l = len - i; l > 0 && best < 0; l--) {
			best = evv_map_label(&g_map, tok + i, l);
			best_l = l;
		}
		if (best < 0) {
			if (bad)
				*bad = tok + i;
			return -1;
		}
		if (g_map.labels[best].kind != 'm' || pending)
			cur = pending ? pending : 2; /* a base begins a symbol (a mark keeps its base's degree) */
		pending = 0;
		if (n < max) {
			label[n] = best;
			degree[n++] = cur;
		}
		i += best_l;
	}
	return n;
}

/* Whether the `len' bytes at tok are the labels of span s, at their degrees, in any order. */
static int same_labels(const char *tok, size_t len, const Span *s)
{
	int label[SPAN_LABELS], degree[SPAN_LABELS];
	int n = read_labels(tok, len, label, degree, SPAN_LABELS, NULL);
	if (n != s->n)
		return 0;
	int used[SPAN_LABELS] = {0};
	for (int k = 0; k < n; k++) {
		int found = 0;
		for (int j = 0; j < n && !found; j++)
			if (!used[j] && s->label[j] == label[k] && s->degree[j] == degree[k])
				used[j] = found = 1;
		if (!found)
			return 0;
	}
	return 1;
}

/* A timed pause, `(1.3 sec)' or `(1.3)', `in' the text between the
   parentheses: its length in ms, or -1. Digits, a point and digits, a space
   and `sec' or `s' may follow; 60 seconds at most. */
static int timed_pause(const char *in, size_t len)
{
	size_t i = 0;
	double v = 0, scale = 0;
	while (i < len && in[i] >= '0' && in[i] <= '9')
		v = v * 10 + (in[i++] - '0');
	if (i == 0)
		return -1;
	if (i < len && in[i] == '.') {
		i++;
		if (i >= len || in[i] < '0' || in[i] > '9')
			return -1;
		for (scale = 0.1; i < len && in[i] >= '0' && in[i] <= '9'; scale /= 10)
			v += (in[i++] - '0') * scale;
	}
	if (i < len && in[i] == ' ')
		i++;
	if (!(i == len || (len - i == 3 && strncmp(in + i, "sec", 3) == 0) || (len - i == 1 && in[i] == 's')))
		return -1;
	if (v > 60)
		return -1;
	return (int)(v * 1000 + 0.5);
}

/* The length of the pause that begins at p, `(' to `)', or -1 (and its end in *end). */
static int pause_at(const char *p, const char **end)
{
	const char *e = strchr(p, ')');
	int ms = -1;
	if (e && e - p < 24) {
		ms = evv_map_pause(&g_map, p, (size_t)(e - p + 1));
		if (ms < 0)
			ms = timed_pause(p + 1, (size_t)(e - p - 1));
	}
	*end = e;
	return ms;
}

/* The letters from p up to span s's end, counted for a ramp as the reading
   goes: not the labels written again before a closing brace (nor an inner
   stretch's), nor the letter after a tie bar, nor what a pause holds. */
static int count_letters(const char *p, const Span *s)
{
	int n = 0, depth = 0;
	size_t cl = strlen(s->close);
	const char *prev = NULL;
	while (*p) {
		int l = utf8_char_len((unsigned char)*p);
		if (strncmp(p, s->close, cl) == 0) {
			if (depth-- == 0)
				break;
		} else if (*p == s->close[0] - (s->close[0] == '}' ? 2 : 1) && cl == 1) {
			depth++; /* `{' or `(' of the same kind */
		} else if (cl == 3 && strncmp(p, "\xe2\xb8\xa8", 3) == 0) {
			depth++;
		}
		if (*p == '(') {
			const char *e;
			if (pause_at(p, &e) >= 0) {
				prev = NULL;
				p = e + 1;
				continue;
			}
		}
		if (!is_space(*p) && *p != '{' && (prev == NULL || is_space(*prev) || *prev == '{')) {
			/* a word's start: labels written again before a closing brace are no letters */
			const char *te = p, *q;
			while (*te && !is_space(*te) && *te != '}')
				te += utf8_char_len((unsigned char)*te);
			for (q = te; is_space(*q); q++)
				;
			if (*q == '}' && read_labels(p, (size_t)(te - p), NULL, NULL, 0, NULL) >= 0) {
				prev = NULL;
				p = q;
				continue;
			}
		}
		if (prev && *prev == '{' && !is_space(*p)) {
			/* an inner stretch's opening labels */
			while (*p && !is_space(*p) && *p != '}')
				p += utf8_char_len((unsigned char)*p);
			prev = NULL;
			continue;
		}
		if (evv_map_letter(&g_map, p, (size_t)l) && !(prev && is_tie(prev)))
			n++;
		prev = p;
		p += l;
	}
	return n;
}

/* Opens a stretch under the labels `tok' (len bytes), closed by `close'. */
static void open_span(const char *tok, size_t len, const char *close, const char *rest)
{
	if (g_n_spans >= 4) {
		evv_diag(EVV_DIAG_LOSS, "label-too-deep", "a fifth stretch inside four: its label `%.*s' is left off", (int)len,
		         tok);
		return;
	}
	Span *s = &g_spans[g_n_spans++];
	memset(s, 0, sizeof(*s));
	snprintf(s->close, sizeof(s->close), "%s", close);
	const char *bad = NULL;
	int n = read_labels(tok, len, s->label, s->degree, SPAN_LABELS, &bad);
	if (n < 0) {
		evv_diag(EVV_DIAG_LOSS, "label-unknown", "`%.*s' in the label `%.*s' is no label the map lists; the label "
		         "is left off", (int)(len - (size_t)(bad - tok)), bad, (int)len, tok);
		n = 0;
	}
	s->n = n;
	int ramps = 0;
	for (int k = 0; k < n; k++)
		ramps += g_map.labels[s->label[k]].kind == 'r';
	if (ramps > 1)
		evv_diag(EVV_DIAG_LOSS, "label-left-off", "a second ramp in the label `%.*s' is left off", (int)len, tok);
	if (ramps)
		s->letters = count_letters(rest, s);
}

static void close_span(const char *close)
{
	if (g_n_spans == 0 || strcmp(g_spans[g_n_spans - 1].close, close) != 0) {
		evv_diag(EVV_DIAG_LOSS, "label-unopened", "`%s' closes no stretch opened before it; passed over", close);
		return;
	}
	g_n_spans--;
}

/* Whether a label of span k is replaced by one of its group in a stretch inside it. */
static int replaced(int k, int label)
{
	const char *g = g_map.labels[label].group;
	if (!g[0])
		return 0;
	for (int j = k + 1; j < g_n_spans; j++)
		for (int i = 0; i < g_spans[j].n; i++)
			if (strcmp(g_map.labels[g_spans[j].label[i]].group, g) == 0)
				return 1;
	return 0;
}

/* The marks the stretches open now give the next letter (and counts it). */
static void span_marks(char *out, size_t room)
{
	out[0] = 0;
	for (int k = 0; k < g_n_spans; k++) {
		Span *s = &g_spans[k];
		int ramped = 0;
		for (int i = 0; i < s->n; i++) {
			const EvvMap *m = &g_map;
			int lb = s->label[i];
			const char *mk = NULL;
			if (m->labels[lb].kind == 'r') {
				if (ramped++)
					continue;
				int steps = m->labels[lb].n;
				int step = s->letters > 1 ? (int)((double)s->at * (steps - 1) / (s->letters - 1) + 0.5) : steps - 1;
				mk = m->labels[lb].marks[step > steps - 1 ? steps - 1 : step];
			} else if (m->labels[lb].kind == 'd' || m->labels[lb].kind == 'm') {
				mk = m->labels[lb].marks[s->degree[i] - 1];
			}
			if (mk && !replaced(k, lb) && strlen(out) + strlen(mk) < room)
				strcat(out, mk);
		}
		s->at++;
	}
}

static int translate_ipa(const char *given)
{
	EvvMapPhone phones[EVV_MAX_PHONES];
	char *utf8 = NULL;
	out_reset();
	if (!g_load_reported)
		g_load_reported = 1;
	else
		evv_diag_clear();
	g_src_shift = 0;
	if (!g_map_loaded)
		return -1;
	utf8 = ipa_normalize(given);
	if (!utf8)
		return -1;
	/* positions are counted in the text as normalised; what is read may have
	   reiterations written out (then `origin' leads back) */
	int *origin = NULL;
	char *expanded = expand_reiteration(utf8, &origin);
	g_input = utf8;
	n_clause_words = 0;
	ClauseWord *cw = NULL;
	int stress = 0, chars = 0;
	int brk_next = 0;               /* a `.' typed: the next segment begins a syllable */
	int levels[8], n_levels = 0;    /* the tone typed for the syllable being read */
	int next_levels[8], n_next = 0; /* a tone mark on a consonant, for the nucleus after it */
	int reg = 0, slope = 0, slope_at = 0;
	EvvPhone *nuc = NULL;           /* the nucleus that typed tone goes to */
	g_n_spans = 0;
	g_pause_ms = 0;
	int spans_on = g_map.n_labels > 0 || g_map.n_pauses > 0;
	const char *text0 = expanded ? expanded : utf8;
	for (const char *p = text0; *p;) {
		int l = utf8_char_len((unsigned char)*p);
		if (*p == ' ' || *p == '\t' || *p == '\n' || *p == '\r') {
			cw = NULL;
			brk_next = 0;
			p++;
			chars++;
			continue;
		}
		/* braces, a stretch's labels, and pauses (D83): only with a map that has labels or pauses */
		if (spans_on && g_n_spans && g_spans[g_n_spans - 1].close[0] == '}' && (p == text0 || is_space(p[-1]))) {
			/* its labels written again just before the closing brace (in any order) */
			const Span *s = &g_spans[g_n_spans - 1];
			const char *te = p;
			while (*te && !is_space(*te) && *te != '}')
				te += utf8_char_len((unsigned char)*te);
			const char *q = te;
			while (is_space(*q))
				q++;
			if (te > p && *q == '}' && same_labels(p, (size_t)(te - p), s)) {
				for (; p < q; p += utf8_char_len((unsigned char)*p))
					chars++;
				continue;
			}
		}
		if (spans_on && *p == '{') {
			const char *t = p + 1;
			while (is_space(*t))
				t++;
			const char *te = t;
			while (*te && !is_space(*te) && *te != '}')
				te++;
			open_span(t, (size_t)(te - t), "}", te);
			for (; p < te; p += utf8_char_len((unsigned char)*p))
				chars++;
			cw = NULL;
			continue;
		}
		if (spans_on && (*p == '}' || *p == ')' || (l == 3 && strncmp(p, "\xe2\xb8\xa9", 3) == 0))) {
			char c[4];
			memcpy(c, p, (size_t)l);
			c[l] = 0;
			close_span(c);
			p += l;
			chars++;
			cw = NULL;
			continue;
		}
		if (spans_on && *p == '(') {
			const char *e;
			int ms = pause_at(p, &e);
			if (ms >= 0) {
				g_pause_ms += ms;
				for (; p <= e; p += utf8_char_len((unsigned char)*p))
					chars++;
				cw = NULL;
				continue;
			}
			open_span("()", 2, ")", p + 1);
			p++;
			chars++;
			cw = NULL;
			continue;
		}
		if (spans_on && l == 3 && strncmp(p, "\xe2\xb8\xa8", 3) == 0) {
			open_span("\xe2\xb8\xa8\xe2\xb8\xa9", 6, "\xe2\xb8\xa9", p + 3);
			p += l;
			chars++;
			cw = NULL;
			continue;
		}
		/* a group boundary ends the phrase: its pitch, its register, its slope */
		int minor = *p == '|' && p[1] != '|';
		int major = (l == 3 && (unsigned char)p[0] == 0xe2 && (unsigned char)p[1] == 0x80 &&
		             (unsigned char)p[2] == 0x96) || (*p == '|' && p[1] == '|');
		if (minor || major) {
			if ((n_levels && nuc == NULL) || n_next) {
				/* a tone typed with no syllable of this phrase to carry it ends with the phrase */
				evv_diag(EVV_DIAG_LOSS, "tone-no-syllable", "a tone with no syllable to carry it before a "
				         "group boundary is left off");
				n_levels = n_next = 0;
			}
			put_tone(nuc, levels, &n_levels, reg, slope, &slope_at);
			write_clause(major ? CLAUSE_PERIOD : CLAUSE_COMMA);
			reg = slope = slope_at = 0;
			nuc = NULL;
			cw = NULL;
			int two = major && *p == '|'; /* `||' typed for ‖ */
			p += two ? 2 : l;
			chars += two ? 2 : 1;
			continue;
		}
		if (l == 3 && (unsigned char)p[0] == 0xe2 && (unsigned char)p[1] == 0x80 && (unsigned char)p[2] == 0xbf) {
			p += l; /* ‿ links: the words are one already where nothing parts them */
			chars++;
			continue;
		}
		const EvvToneMark *tm = evv_map_tonemark(&g_map, p, (size_t)l);
		if (tm) {
			if (tm->kind == 'r') {
				/* the syllable before is done before the register moves */
				put_tone(nuc, levels, &n_levels, reg, slope, &slope_at);
				nuc = NULL;
				reg += tm->value;
			} else if (tm->kind == 's') {
				put_tone(nuc, levels, &n_levels, reg, slope, &slope_at);
				nuc = NULL;
				slope = tm->value;
				slope_at = 0;
			} else {
				for (int i = 0; i < tm->n && n_levels < 8; i++)
					levels[n_levels++] = tm->levels[i];
			}
			p += l;
			chars++;
			continue;
		}
		if (cw == NULL) {
			/* a word with no stress mark has its first syllable stressed */
			const char *e = p;
			while (*e && *e != ' ' && *e != '\t' && *e != '\n' && *e != '\r')
				e++;
			stress = 1;
			for (const char *q = p; q + 1 < e; q++)
				if ((unsigned char)q[0] == 0xcb && ((unsigned char)q[1] == 0x88 || (unsigned char)q[1] == 0x8c))
					stress = 0;
			cw = new_word(origin ? origin[chars] : chars, 0);
			cw->pause_ms = g_pause_ms;
			g_pause_ms = 0;
		}
		if (l == 2 && (unsigned char)p[0] == 0xcb && (unsigned char)p[1] == 0x88) { /* ˈ */
			stress = 1;
			p += l;
			chars++;
			continue;
		}
		if (l == 2 && (unsigned char)p[0] == 0xcb && (unsigned char)p[1] == 0x8c) { /* ˌ */
			stress = 2;
			p += l;
			chars++;
			continue;
		}
		if (*p == '.') {
			brk_next = 1;
			p++;
			chars++;
			continue;
		}
		/* one segment: this character and the marks after it; a tone
		   diacritic among them is the syllable's tone, not a mark of the
		   segment */
		const char *s = p;
		const EvvLetter *letter = evv_map_letter(&g_map, p, (size_t)l);
		size_t tied_len = 0;
		if (!letter)
			letter = evv_map_tied_letter(&g_map, p, &tied_len); /* ↀ͡r: its tie and letter join below (D80) */
		int seg_tone[8], n_seg_tone = 0;
		char seg[64];
		int seg_len = 0, cut = 0, tied = 0, had_tie = 0;
		memcpy(seg, p, (size_t)l);
		seg_len = l;
		p += l;
		chars++;
		int lt_len = letter ? l : 0; /* the letter's bytes, at the end of seg so far */
		if (!letter && evv_map_has_premod(&g_map, s, (size_t)l)) {
			/* marks written before a letter (extIPA's ʰp, ˬz: `premod' lines),
			   then the letter they belong to */
			while (*p && seg_len + 4 < (int)sizeof(seg)) {
				int ml = utf8_char_len((unsigned char)*p);
				const EvvLetter *lt = evv_map_letter(&g_map, p, (size_t)ml);
				if (!lt)
					lt = evv_map_tied_letter(&g_map, p, &tied_len); /* ʰↀ͡r (D80) */
				if (!lt && !evv_map_has_premod(&g_map, p, (size_t)ml))
					break;
				memcpy(seg + seg_len, p, (size_t)ml);
				seg_len += ml;
				p += ml;
				chars++;
				if (lt) {
					letter = lt;
					lt_len = ml;
					break;
				}
			}
		}
		while (*p && *p != ' ' && *p != '\t' && *p != '\n' && *p != '\r' && *p != '.' && *p != '|' &&
		       !(spans_on && (*p == '{' || *p == '}' || *p == '(' || *p == ')' || strncmp(p, "\xe2\xb8\xa8", 3) == 0 ||
		                      strncmp(p, "\xe2\xb8\xa9", 3) == 0))) {
			int ml = utf8_char_len((unsigned char)*p);
			const EvvToneMark *m = evv_map_tonemark(&g_map, p, (size_t)ml);
			if (lt_len && !tied && lt_len + ml < 16 && seg_len + ml < (int)sizeof(seg) &&
			    evv_map_letter(&g_map, p, (size_t)ml)) {
				/* a letter of two letters, the second right after the first
				   (extIPA's cluck ǃ¡: a click and the tongue's slap), is one
				   letter where the map lists the pair */
				char two[16];
				memcpy(two, seg + seg_len - lt_len, (size_t)lt_len);
				memcpy(two + lt_len, p, (size_t)ml);
				const EvvLetter *lt2 = evv_map_letter(&g_map, two, (size_t)(lt_len + ml));
				if (lt2) {
					letter = lt2;
					memcpy(seg + seg_len, p, (size_t)ml);
					seg_len += ml;
					p += ml;
					chars++;
					lt_len = 0; /* the pair is the letter: no third joins it */
					continue;
				}
			}
			lt_len = 0; /* anything between: no letter of two after it */
			if (letter && !tied && evv_map_has_premod(&g_map, p, (size_t)ml) &&
			    !evv_map_has_mod(&g_map, p, (size_t)ml, letter->cls)) {
				/* a mark this letter has no line for, written before the
				   next letter: that letter's (aʰpa: a pre-aspirated p) */
				const char *q = p;
				while (*q && !evv_map_letter(&g_map, q, (size_t)utf8_char_len((unsigned char)*q)) &&
				       evv_map_has_premod(&g_map, q, (size_t)utf8_char_len((unsigned char)*q)))
					q += utf8_char_len((unsigned char)*q);
				if (*q && (evv_map_letter(&g_map, q, (size_t)utf8_char_len((unsigned char)*q)) ||
				           evv_map_tied_letter(&g_map, q, &tied_len)))
					break;
			}
			int after_tie = 0;
			if (tied && evv_map_letter(&g_map, p, (size_t)ml)) {
				/* the letter after a tie bar belongs to this segment (and
				   may begin a letter of two: ŋ͡ǃ¡) */
				tied = 0;
				after_tie = 1;
			} else if (evv_map_letter(&g_map, p, (size_t)ml) || evv_map_tied_letter(&g_map, p, &tied_len) ||
			    (ml == 2 && (unsigned char)p[0] == 0xcb && ((unsigned char)p[1] == 0x88 || (unsigned char)p[1] == 0x8c)) ||
			    (m && !(m->kind == 't' && is_combining((const unsigned char *)p, ml))) ||
			    (ml == 3 && (unsigned char)p[0] == 0xe2 && (unsigned char)p[1] == 0x80 &&
			     ((unsigned char)p[2] == 0x96 || (unsigned char)p[2] == 0xbf)))
				break;
			if (ml == 2 && (unsigned char)p[0] == 0xcd && ((unsigned char)p[1] == 0xa1 || (unsigned char)p[1] == 0x9c ||
			                                               (unsigned char)p[1] == 0xa2)) {
				/* a tie bar, or extIPA's sliding mark (U+0362), which joins two letters too */
				tied = 1;
				had_tie = 1;
			}
			if (m) {
				for (int i = 0; i < m->n && n_seg_tone < 8; i++)
					seg_tone[n_seg_tone++] = m->levels[i];
			} else if (seg_len + ml < (int)sizeof(seg)) {
				memcpy(seg + seg_len, p, (size_t)ml);
				seg_len += ml;
				if (after_tie)
					lt_len = ml;
			} else {
				cut = 1;
			}
			p += ml;
			chars++;
		}
		seg[seg_len] = 0;
		if (cut)
			evv_diag(EVV_DIAG_LOSS, "ipa-segment-cut", "a letter with more than %d bytes of marks: cut to %d, the rest "
			         "left off", (int)sizeof(seg) - 1, seg_len);
		(void)s;
		if (!letter)
			evv_diag(EVV_DIAG_LOSS, "ipa-not-a-letter", "`%s' does not begin with a letter the map lists", seg);
		int matched = 0;
		/* a letter in a stretch under a label: composed with the label's marks too (D83) */
		char segx[64 + 4 * 96];
		const char *look = seg;
		if (letter && g_n_spans) {
			char sm[4 * 96];
			span_marks(sm, sizeof(sm));
			snprintf(segx, sizeof(segx), "%s%s", seg, sm);
			look = segx;
		}
		int n = evv_map_lookup_ex(&g_map, NULL, NULL, look, phones, EVV_MAX_PHONES, &matched);
		if (!matched)
			evv_diag(EVV_DIAG_LOSS, "phoneme-dropped", "/%s/ has no line in the map and cannot be composed", seg);
		int vowel = letter && letter->cls == 'v';
		/* C7: a consonant marked syllabic (U+0329) carries a syllable of its own; a
		   vowel marked non-syllabic (U+032F) carries none */
		int syllabic = vowel;
		if (strstr(seg, "\xcc\xa9"))
			syllabic = 1;
		if (vowel && strstr(seg, "\xcc\xaf"))
			syllabic = vowel = 0;
		if (syllabic && nuc != NULL)
			put_tone(nuc, levels, &n_levels, reg, slope, &slope_at); /* the syllable before is done */
		if (syllabic) {
			/* a tone mark put on a consonant before this nucleus is this syllable's */
			for (int i = 0; i < n_next && n_levels < 8; i++)
				levels[n_levels++] = next_levels[i];
			n_next = 0;
			for (int i = 0; i < n_seg_tone && n_levels < 8; i++)
				levels[n_levels++] = seg_tone[i];
		} else {
			for (int i = 0; i < n_seg_tone && n_next < 8; i++)
				next_levels[n_next++] = seg_tone[i];
			if (n_seg_tone)
				evv_diag(EVV_DIAG_NOTE, "tone-on-consonant", "a tone mark on /%s/ goes to the vowel of the "
				         "syllable after it", seg);
		}
		if (n == 0)
			continue;
		int first = cw->w.n;
		evv_word_add(&cw->w, &g_map, phones, n, syllabic, vowel, syllabic ? stress : 0, NULL);
		/* a tied segment said as two phones or more is one segment: the
		   syllables are not divided inside it */
		if (had_tie) {
			int seen = 0;
			for (int i = first; i < cw->w.n; i++)
				if (!cw->w.ph[i].made)
					cw->w.ph[i].glue = seen++ > 0;
		}
		if (brk_next) {
			for (int i = first; i < cw->w.n; i++)
				if (!cw->w.ph[i].made) {
					cw->w.ph[i].brk = 1;
					break;
				}
			brk_next = 0;
		}
		cw->src_len = (origin ? origin[chars] : chars) - cw->src;
		if (syllabic) {
			stress = 0;
			for (int i = cw->w.n - 1; i >= 0; i--)
				if (cw->w.ph[i].nucleus) {
					nuc = &cw->w.ph[i];
					break;
				}
		}
	}
	if ((n_levels && nuc == NULL) || n_next)
		evv_diag(EVV_DIAG_LOSS, "tone-no-syllable", "a tone with no syllable to carry it is left off");
	put_tone(nuc, levels, &n_levels, reg, slope, &slope_at);
	if (g_n_spans)
		evv_diag(EVV_DIAG_LOSS, "label-unclosed", "a stretch that %s closes is not closed; it ends with the text",
		         g_spans[g_n_spans - 1].close);
	write_clause(CLAUSE_PERIOD);
	if (g_pause_ms > 0) {
		/* a pause typed after the last word */
		char pz[24];
		int pl = snprintf(pz, sizeof(pz), " `p%d", g_pause_ms);
		out_put(pz, (size_t)pl);
	}
	put_header();
	g_input = NULL;
	free(expanded);
	free(origin);
	free(utf8);
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
	evv_diag_clear();
	int bad = evv_map_load(&g_map, map_path, err, errlen);
	evv_diag_line = 0;
	g_load_reported = 0;
	if (bad != 0)
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
			int failed = (flags & EVV_FE_FLAG_IPA) ? translate_ipa(text) : translate_text(text, flags);
			if (failed != 0) {
				reply_status(stdout, 0, failed == -2 ? "the text could not be decoded" : "no voice has been set");
				continue;
			}
			EvvResultHead r;
			r.n_anchors = (uint32_t)out.n_anchors;
			r.text_len = (uint32_t)out.len;
			uint32_t alen = (uint32_t)(out.n_anchors * sizeof(EvvAnchor));
			/* what was lost on the way, after the text, where a host that
			   does not know it reads past it */
			size_t dlen = 0;
			char *diag = evv_diag_text(&dlen);
			uint32_t dhead[2] = {EVV_FE_DIAG_MAGIC, (uint32_t)dlen};
			uint32_t dbytes = dlen ? (uint32_t)(sizeof(dhead) + dlen) : 0;
			/* head, anchors, text, diagnostics */
			EvvMsgHeader hh;
			hh.magic = EVV_FE_MAGIC;
			hh.type = EVV_FE_RESULT;
			hh.size = (uint32_t)sizeof(r) + alen + r.text_len + dbytes;
			fwrite(&hh, sizeof(hh), 1, stdout);
			fwrite(&r, sizeof(r), 1, stdout);
			if (alen)
				fwrite(out.anchors, 1, alen, stdout);
			if (r.text_len)
				fwrite(out.text, 1, r.text_len, stdout);
			if (dbytes) {
				fwrite(dhead, sizeof(dhead), 1, stdout);
				fwrite(diag, 1, dlen, stdout);
			}
			free(diag);
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
	/* for whoever measures a sound: [[...]] in the text is eSpeak NG's own
	   phoneme names, said as they stand */
	option_phoneme_input = has_arg(argc, argv, "--phonemes");
	if (has_arg(argc, argv, "--ipa"))
		translate_ipa(text);
	else
		translate_text(text, (has_arg(argc, argv, "--punctuation") ? EVV_FE_FLAG_PUNCTUATION : 0) |
		                         (has_arg(argc, argv, "--spell") ? EVV_FE_FLAG_SPELL : 0));
	if (has_arg(argc, argv, "--anchors")) {
		for (size_t i = 0; i < out.n_anchors; i++)
			printf("%u\t%u+%u\n", out.anchors[i].out_offset, out.anchors[i].src_offset, out.anchors[i].src_length);
	}
	printf("%s\n", out.text ? out.text : "");
	fflush(stdout);
	/* what was lost on the way, one line each: diag, level, kind, detail, count */
	size_t dlen = 0;
	char *diag = evv_diag_text(&dlen);
	for (char *line = diag; line && *line;) {
		char *end = strchr(line, '\n');
		if (!end)
			break;
		fprintf(stderr, "diag\t%.*s\n", (int)(end - line), line);
		line = end + 1;
	}
	free(diag);
	free(owned);
	/* --strict: a loss is a failure */
	return has_arg(argc, argv, "--strict") && evv_diag_losses() > 0 ? 3 : 0;
}
