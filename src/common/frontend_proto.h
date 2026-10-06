/*
 * Messages between the engine host (OpenEvvHost.exe) and the eSpeak NG
 * front-end (OpenEvvFrontend.exe), over two anonymous pipes: the front-end's
 * standard input and output.
 *
 * This header is shared by two programs under two licences -- the host under
 * the MIT licence and the front-end under the GPL version 3 or later -- and
 * is itself under the MIT licence so that both may include it:
 *
 * Copyright (c) 2026 the OpenEVV SAPI5 contributors
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this file, to deal in it without restriction, including without
 * limitation the rights to use, copy, modify, merge, publish, distribute,
 * sublicense, and/or sell copies of it, subject to the condition that this
 * notice is kept. It is provided "as is", without warranty of any kind.
 *
 * Every message is an EvvMsgHeader and `size' bytes. Little-endian, packed,
 * the same in both bitnesses.
 *
 *   host -> front-end   EVV_FE_VOICE      "voice\0map path\0"  (UTF-8)
 *                        answered by EVV_FE_STATUS
 *   host -> front-end   EVV_FE_TRANSLATE  uint32 flags, then the text in UTF-8, ended by a nought
 *                        answered by EVV_FE_RESULT, or EVV_FE_STATUS on failure
 *   host -> front-end   EVV_FE_QUIT
 *
 * A result is an EvvResultHead, n_anchors EvvAnchor records, and text_len
 * bytes of ASCII: the annotated text for the engine. Each anchor says where
 * in that text a word's annotation begins and which characters of the input
 * it was read from, counted in Unicode code points from nought.
 *
 * After the text a result may carry what was lost on the way to it: a
 * uint32 EVV_FE_DIAG_MAGIC, a uint32 length, and that many bytes of UTF-8
 * lines "level\tkind\tdetail\tcount\n", level being `loss' or `note'. A host
 * that does not know of it reads past it, as hosts before it did.
 */
#ifndef EVV_FRONTEND_PROTO_H
#define EVV_FRONTEND_PROTO_H

#include <stdint.h>

#define EVV_FE_MAGIC 0x45464556u /* "VEFE" */
#define EVV_FE_MAX_PAYLOAD (8u << 20)
#define EVV_FE_DIAG_MAGIC 0x47414944u /* "DIAG" */

/* flags of a translate request */
#define EVV_FE_FLAG_PUNCTUATION 1u /* say the names of punctuation marks, as spelling wants */
#define EVV_FE_FLAG_SPELL 2u       /* the whole text is to be spelled: every character by its name */
#define EVV_FE_FLAG_IPA 4u         /* the text is IPA, read by the map's letters and marks (C4) */

enum {
	EVV_FE_VOICE = 1,
	EVV_FE_TRANSLATE = 2,
	EVV_FE_QUIT = 3,
	EVV_FE_STATUS = 101,
	EVV_FE_RESULT = 102,
};

#pragma pack(push, 1)

typedef struct {
	uint32_t magic;
	uint32_t type;
	uint32_t size;
} EvvMsgHeader;

typedef struct {
	int32_t ok;
	char error[200];
} EvvStatus;

typedef struct {
	uint32_t n_anchors;
	uint32_t text_len;
} EvvResultHead;

typedef struct {
	uint32_t out_offset; /* byte offset of the word's annotation in the result text */
	uint32_t src_offset; /* its first character in the input, in code points */
	uint32_t src_length; /* how many characters of the input it was, as eSpeak NG counted them */
} EvvAnchor;

#pragma pack(pop)

#endif
