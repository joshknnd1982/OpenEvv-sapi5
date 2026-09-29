#!/usr/bin/env python3
"""Measures a language module: what each of its phones sounds like.

An eSpeak NG language is spoken by an openevv module, and a sound the module
lacks is made out of the nearest one it has. How far the two are apart can
only be said if it is known where the module's own phone is, and that is
measured here rather than assumed: every phone is put through the module as
a pronunciation annotation, and what the module asked the synthesiser for is
read off the frames.

For a vowel: its formants where they are steadiest, after b, d and g, and
how long it lasts stressed and unstressed.
For a stop: how long it is shut, and how long after the release the voice
begins, at the start of a word and between vowels.
For a fricative, a nasal or a liquid: its formants and its noise.
For every phone: what the module says when it is handed it, since a module
says an affricate as two phones and may say one phone as another; and what it
does with it at the end of a word.

    python engine/accent/chassis.py dede            writes engine/accent/chassis/dede.json
    python engine/accent/chassis.py all
"""
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from probe import INERT, LANGUAGE, Probe, quote  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

# The phones of each module, as its statement table names them, and which of
# them are vowels. `#' is the pause and is not a sound.
MODULES = {
    'dede': dict(vowels='i I e E E: a A u U o O y Y oe OE @ R aj aw oj a~ E~ o~ oe~',
                 consonants='p b t d k g f v s z S Z X x r P T C J h m n G l j w'),
    'itit': dict(vowels='i e E a u o c',
                 consonants='b p d t k g v f z s Z S J C D T m n N G r R l L y w'),
    'eses': dict(vowels='i e a o u',
                 consonants='p t k b d g B D G Y f v s z T j S Z C J L m n N ng r R l y w'),
    'esus': dict(vowels='i e a o u',
                 consonants='p t k b d g B D G Y f v s z T j S Z C J L m n N ng r R l y w'),
    'frfr': dict(vowels='a A e E i I y Y o c u U eu oe a~ E~ o~ oe~ OE~ x',
                 consonants='b p d t k g D T v f z s Z C J S h m n nj ng N r R l j w H ?'),
    'enus': dict(vowels='i I e E A X Xx H x R @ c@ a@ Aa H@ a u U o c Y W O',
                 consonants='b p d t F ? k g D T v f z s Z S J C h m n G Q r l y w L'),
    'engb': dict(vowels='i I e E A X Xx H x R @ c@ a@ Aa H@ a u U o c Y W O',
                 consonants='b p d t F ? k g D T v f z s Z S J C h m n G Q r l y w L'),
}

# Modules that write the stress digit before the nucleus rather than before
# the syllable.
FRENCH = ('frfr', 'frca')
FRENCH_BASE = {}


def syllable(tag, stress, onset, vowel, coda=''):
    o = ''.join(quote(p) for p in onset)
    c = ''.join(quote(p) for p in coda)
    if tag in FRENCH or FRENCH_BASE.get(tag):
        return '.' + o + str(stress) + quote(vowel) + c
    return '.' + str(stress) + o + quote(vowel) + c


def word(tag, *syllables):
    return '`[' + ''.join(syllables) + ']'


def steady(frames, key='f1'):
    """The run of voiced frames over which a formant moves least."""
    voiced = [f for f in frames if f['av'] >= 30 and f['af'] == 0]
    if len(voiced) < 3:
        return voiced
    best, spread = None, None
    n = max(3, len(voiced) // 3)
    for i in range(0, len(voiced) - n + 1):
        run = voiced[i:i + n]
        s = sum(max(f[k] for f in run) - min(f[k] for f in run) for k in ('f1', 'f2', 'f3'))
        if spread is None or s < spread:
            best, spread = run, s
    return best


def is_steady(frames, i):
    """As the engine judges it: a frame whose neighbours say the same thing,
    which is where a sound may be made longer or shorter."""
    f = frames[i]
    a = frames[i - 1] if i > 0 else f
    b = frames[i + 1] if i + 1 < len(frames) else f
    for k in ('av', 'af', 'ah', 'f1', 'f2', 'f3'):
        tol = f[k] // 50 + 4 if k.startswith('f') else 1
        if abs(a[k] - b[k]) > tol:
            return False
    return True


def median(values):
    return int(round(statistics.median(values))) if values else 0


def accepted(r, text_words):
    """Whether the module took the annotation rather than reading it aloud."""
    names = [t['name'] for t in r.trace if t['name'] not in ('#', '-')]
    return 0 < len(names) <= text_words * 6


def measure_vowel(p, v, aid):
    out = {'kind': 'vowel'}
    f = {1: [], 2: [], 3: [], 4: []}
    b = {1: [], 2: [], 3: []}
    ends = {1: [], 2: [], 3: []}
    starts = {1: [], 2: [], 3: []}
    durs, durs0 = [], []
    sounds, steadies = [], []
    said = None
    extra = {}
    for c in ('b', 'd', 'g'):
        text = INERT + word(p.tag, syllable(p.tag, 1, [c], v), syllable(p.tag, 0, [c], aid)) + '.'
        r = p.speak(text)
        tr = [t for t in r.trace if t['name'] not in ('#', '-')]
        if len(tr) < 2 or tr[0]['name'] != c:
            continue
        # everything between the first consonant and the second is the vowel
        k = 1
        while k < len(tr) and tr[k]['name'] != c:
            k += 1
        parts = tr[1:k]
        if not parts:
            continue
        names = [t['name'] for t in parts]
        if said is None:
            said = names
        frames = [fr for fr in r.frames if parts[0]['out_a'] <= fr['at'] < parts[-1]['out_b']]
        voiced = [fr for fr in frames if fr['av'] >= 30 and fr['af'] == 0]
        run = steady(frames)
        if not run:
            continue
        for i in (1, 2, 3, 4):
            f[i].append(median([fr['f%d' % i] for fr in run]))
        for i in (1, 2, 3):
            b[i].append(median([fr['b%d' % i] for fr in run]))
        if len(voiced) >= 6:
            third = max(2, len(voiced) // 4)
            for i in (1, 2, 3):
                starts[i].append(median([fr['f%d' % i] for fr in voiced[third:third * 2]]))
                ends[i].append(median([fr['f%d' % i] for fr in voiced[-third:]]))
        durs.append(parts[-1]['out_b'] - parts[0]['out_a'])
        # how long the vowel sounds: from where the voice is up after the
        # consonant before it to where it goes down into the one after
        after = [fr for fr in r.frames if fr['at'] >= parts[0]['out_a']]
        n = 0
        while n < len(after) and after[n]['av'] < 35:
            n += 1
        m = n
        while m < len(after) and after[m]['av'] >= 35:
            m += 1
        if m > n:
            sounds.append(sum(fr['step'] for fr in after[n:m]))
        steadies.append(sum(frames[i]['step'] for i in range(len(frames)) if is_steady(frames, i)))
        extra['fnz'] = max(fr['fnz'] - fr['fnp'] for fr in run)
        extra['av'] = median([fr['av'] for fr in run])
        # and unstressed, in the syllable after
        text = INERT + word(p.tag, syllable(p.tag, 1, [c], aid), syllable(p.tag, 0, [c], v)) + '.'
        r = p.speak(text)
        tr = [t for t in r.trace if t['name'] not in ('#', '-')]
        idx = [i for i, t in enumerate(tr) if t['name'] == c]
        if len(idx) >= 2 and idx[1] + 1 < len(tr):
            durs0.append(tr[-1]['out_b'] - tr[idx[1] + 1]['out_a'])
    if not f[1]:
        return None
    out['f'] = [median(f[i]) for i in (1, 2, 3, 4)]
    out['b'] = [median(b[i]) for i in (1, 2, 3)]
    out['said'] = said
    out['ms'] = median(durs)
    out['ms_sound'] = median(sounds)
    out['ms_steady'] = median(steadies)
    out['ms_unstressed'] = median(durs0)
    if starts[1]:
        out['from'] = [median(starts[i]) for i in (1, 2, 3)]
        out['to'] = [median(ends[i]) for i in (1, 2, 3)]
    out.update(extra)
    return out


def measure_consonant(p, c, aid):
    out = {'kind': 'consonant'}
    # between vowels, before an unstressed vowel
    text = INERT + word(p.tag, syllable(p.tag, 1, [], aid), syllable(p.tag, 0, [c], aid)) + '.'
    r = p.speak(text)
    tr = [t for t in r.trace if t['name'] not in ('#', '-')]
    if len(tr) < 3 or tr[0]['name'] != aid or len(tr) > 6:
        return None
    parts = tr[1:-1]
    out['said'] = [t['name'] for t in parts]
    own = [fr for fr in r.frames if parts[0]['out_a'] <= fr['at'] < parts[-1]['out_b']]
    after = [fr for fr in r.frames if tr[-1]['out_a'] <= fr['at'] < tr[-1]['out_b']]
    out['ms'] = parts[-1]['out_b'] - parts[0]['out_a']
    shut = [fr for fr in own if fr['af'] == 0 and fr['ah'] == 0 and fr['av'] < 30]
    out['shut_ms'] = sum(fr['step'] for fr in shut)
    out['shut_av'] = median([fr['av'] for fr in shut]) if shut else 0
    noisy = [fr for fr in own if fr['af'] > 0]
    out['af'] = max([fr['af'] for fr in own] + [0])
    out['av'] = median([fr['av'] for fr in own if fr['av'] > 0]) if any(fr['av'] > 0 for fr in own) else 0
    if noisy:
        top = max(noisy, key=lambda fr: fr['af'])
        out['amp'] = [top[k] for k in ('a2f', 'a3f', 'a4f', 'a5f', 'a6f', 'ab')]
    mid = own[len(own) // 2] if own else None
    if mid:
        out['f'] = [mid['f1'], mid['f2'], mid['f3'], mid['f4']]
    last = own[-1] if own else None
    if last:
        out['locus'] = [last['f1'], last['f2'], last['f3'], last['f4']]
    # the release, in the stretch after
    noise = 0
    voiced_at = None
    burst = 0
    asp = 0
    t0 = after[0]['at'] if after else 0
    # a burst that began in the stop's own stretch counts from there
    began = None
    seen_shut = False
    for fr in own:
        if fr['af'] == 0 and fr['ah'] == 0 and fr['av'] < 30:
            seen_shut = True
        elif seen_shut and fr['af'] > 0 and began is None:
            began = fr['at']
    for fr in after:
        if fr['av'] >= 30:
            voiced_at = fr['at']
            break
        if fr['af'] > 0 or fr['ah'] > 0:
            noise += fr['step']
            burst = max(burst, fr['af'])
            asp = max(asp, fr['ah'])
    if voiced_at is not None and shut:
        out['vot'] = voiced_at - (began if began is not None else t0)
        out['burst'] = burst
        out['asp'] = asp
    # at the start of a word, stressed
    text = INERT + word(p.tag, syllable(p.tag, 1, [c], aid), syllable(p.tag, 0, ['m'], aid)) + '.'
    r = p.speak(text)
    tr = [t for t in r.trace if t['name'] not in ('#', '-')]
    k = 0
    while k < len(tr) and tr[k]['name'] != aid:
        k += 1
    if 0 < k < len(tr):
        own0 = [fr for fr in r.frames if tr[0]['out_a'] <= fr['at'] < tr[k - 1]['out_b']]
        after0 = [fr for fr in r.frames if tr[k]['out_a'] <= fr['at'] < tr[k]['out_b']]
        began = None
        for fr in own0:
            if fr['af'] > 0 and began is None:
                began = fr['at']
        voiced_at = None
        for fr in after0:
            if fr['av'] >= 30:
                voiced_at = fr['at']
                break
        if voiced_at is not None and after0:
            out['vot_initial'] = voiced_at - (began if began is not None else after0[0]['at'])
    # at the end of a word
    text = INERT + word(p.tag, syllable(p.tag, 1, [], aid, [c])) + ' ' + \
        word(p.tag, syllable(p.tag, 1, ['m'], aid)) + '.'
    r = p.speak(text)
    tr = [t for t in r.trace if t['name'] not in ('#', '-')]
    if tr and tr[0]['name'] == aid:
        k = 1
        while k < len(tr) and tr[k]['name'] != 'm':
            k += 1
        out['said_final'] = [t['name'] for t in tr[1:k]]
    # doubled between vowels
    text = INERT + word(p.tag, syllable(p.tag, 1, [], aid, [c]), syllable(p.tag, 0, [c], aid)) + '.'
    r = p.speak(text)
    tr = [t for t in r.trace if t['name'] not in ('#', '-')]
    if len(tr) >= 3 and tr[0]['name'] == aid:
        out['said_double'] = [t['name'] for t in tr[1:-1]]
        out['ms_double'] = tr[-2]['out_b'] - tr[1]['out_a']
    # after a vowel and before a consonant
    text = INERT + word(p.tag, syllable(p.tag, 1, [], aid, [c]), syllable(p.tag, 0, ['t'], aid)) + '.'
    r = p.speak(text)
    tr = [t for t in r.trace if t['name'] not in ('#', '-')]
    if len(tr) >= 3 and tr[0]['name'] == aid:
        k = 1
        while k < len(tr) and tr[k]['name'] != 't':
            k += 1
        out['said_coda'] = [t['name'] for t in tr[1:k]]
    return out


def measure(tag):
    # `dexx:dede' is a module made from another: its phones are the other's
    base = tag
    if ':' in tag:
        tag, base = tag.split(':', 1)
    p = Probe(tag, language=LANGUAGE[base])
    m = MODULES[base]
    aid = 'a'
    if base in FRENCH:
        FRENCH_BASE[tag] = True
    out = {'module': tag, 'base': base, 'phones': {}}
    for v in m['vowels'].split():
        got = measure_vowel(p, v, aid)
        if got:
            out['phones'][v] = got
            print('%s %-4s %s %s ms %s' % (tag, v, got['f'], got.get('said'), got['ms']))
        else:
            print('%s %-4s would not be said' % (tag, v))
    for c in m['consonants'].split():
        got = measure_consonant(p, c, aid)
        if got:
            out['phones'][c] = got
            print('%s %-4s said %s final %s double %s coda %s shut %s vot %s/%s af %s' % (
                tag, c, got.get('said'), got.get('said_final'), got.get('said_double'), got.get('said_coda'),
                got.get('shut_ms'), got.get('vot'), got.get('vot_initial'), got.get('af')))
        else:
            print('%s %-4s would not be said' % (tag, c))
    # the pitch of a plain statement, for what the module does by itself
    os.makedirs(os.path.join(HERE, 'chassis'), exist_ok=True)
    path = os.path.join(HERE, 'chassis', tag + '.json')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write('\n')
    print('wrote', path)


if __name__ == '__main__':
    tags = sys.argv[1:] or ['dede']
    if tags == ['all']:
        tags = sorted(MODULES)
    for t in tags:
        measure(t)
