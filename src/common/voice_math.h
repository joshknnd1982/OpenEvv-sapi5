// From SAPI's rate, pitch and volume, and the user's settings, to the engine's
// own voice parameters.
#pragma once

#include "languages.h"
#include "settings.h"

namespace evv {

// A voice's eight parameters as they will be spoken: the preset's values,
// with the user's changes on top. Unknown values stay -1 ("the preset's").
void effective_voice(const LanguageInfo& lang, int preset, const Settings& s, int out[8]);

// The engine speed for a SAPI rate of -10..+10. Nought is the voice's own
// speed; +10 reaches the configured maximum (250 with rate boost); -10 the
// configured minimum. The engine's speed is already exponential -- each ten
// units is about 22% faster -- so a straight line in speed is an even ratio
// per SAPI step.
int engine_speed(int voice_speed, int sapi_rate, const Settings& s);

// The pitch baseline for a SAPI pitch of -10..+10.
int engine_pitch(int voice_pitch, int sapi_pitch, const Settings& s);

// The engine volume for SAPI's volume (0..100) and a fragment's (0..100).
int engine_volume(int voice_volume, unsigned site_volume, unsigned fragment_volume);

} // namespace evv
