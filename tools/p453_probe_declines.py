# -*- coding: utf-8 -*-
"""P453 - the twelve probes that could not say "I could not run".

The until() sweep found 164 discarded waits across the suite, and cut them to
the twelve that matter: probes that DISCARD a wait and have NO decline path.
Such a probe cannot report "I could not run" no matter what happens, so every
timeout becomes a verdict about the game. That is exactly what apv_preserve,
apv_bust_settle and apv_p405_extraturn each did before they were fixed one at
a time.

WHICH WAIT GETS THE GATE, and why it is the last one in each file rather than
all of them. Read across the twelve, every file's FINAL wait is its
precondition - the state its assertions are about:

    .fo-offer rendered          asset_404, font_reach, css_live
    G.phase==='choosing'        amber_oneshot, break_doublepush
    dice visible on the table   prop_overlap
    G.phase==='idle'            bust_settle_p2, bust_settle_player, feat_splash
    #gbLoadout .loFeat present  feat_wall_p425, feat_wall_pixels

The earlier waits in each file are navigation, and a navigation failure shows
up as the final wait timing out too - so gating the last one catches the whole
chain without pretending each intermediate step needs its own verdict.

WHAT THIS DELIBERATELY DOES NOT DO: turn the other 152 discarded waits into
gates. Most are settle-before-screenshot or a tap that a later wait re-checks,
where the discard is correct. The audit's own note says the judgement is per
site; this patch makes the twelve that provably cannot decline able to.
"""
import io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = ['apv_asset_404.js', 'apv_font_reach.js', 'apv_css_live.js',
         'apv_amber_oneshot.js', 'apv_break_doublepush.js', 'apv_bust_settle.js',
         'apv_prop_overlap.js', 'apv_bust_settle_p2.js', 'apv_bust_settle_player.js',
         'apv_feat_splash.js', 'apv_feat_wall_p425.js', 'apv_feat_wall_pixels.js']

NOTE = ("/* PRECONDITION, NOT A PAUSE. until() returns FALSE on timeout rather\n"
        "   than throwing, so discarding this result meant every assertion below\n"
        "   ran against a state that may never have arrived - and reported the\n"
        "   result as a verdict about the game. Three probes were fixed one at a\n"
        "   time for exactly this before it was swept for. */\n")

done, skipped = [], []
for name in FILES:
    p = os.path.join(HERE, name)
    s = io.open(p, encoding='utf-8').read()
    if re.search(r'return\s*\{\s*(skip|err)', s):
        continue                                  # already able to decline
    starts = [m.start() for m in re.finditer(r'await\s+until\s*\(', s)]
    assert starts, 'no await until in %s' % name
    st = starts[-1]
    # IS THE FINAL WAIT ACTUALLY DISCARDED? The audit counts discarded waits
    # PER FILE; it does not say the LAST one is among them. The first run of
    # this patch assumed it was and renamed `const drafted = await until(...)`
    # to `const _pre = ...` in apv_css_live and `rolled = ...` in
    # apv_prop_overlap - orphaning variables both probes went on to read, which
    # crashed one and silently changed the other.
    # Both CAPTURE their final wait and handle it their own way: css_live
    # records out.note, prop_overlap sleeps and carries on. Neither needs a
    # gate; they were flagged for OTHER discarded waits earlier in the file.
    # Acting on a per-file aggregate at a specific site, without checking that
    # site, is the mistake this project keeps finding in its own tools.
    i = st - 1
    while i >= 0 and s[i] in ' 	':
        i -= 1
    if i >= 0 and s[i] not in ('\n', ';', '{', '}'):
        skipped.append(name)
        continue
    # brace-match the call's parens so a multi-line condition is handled
    i = s.index('(', st)
    d, j = 0, i
    while j < len(s):
        if s[j] == '(': d += 1
        elif s[j] == ')':
            d -= 1
            if d == 0:
                break
        j += 1
    end = s.find(';', j)
    assert end > 0, 'no statement end in %s' % name
    call = s[st:end]
    # indentation of the line the wait starts on, so the insert reads right
    ls = s.rfind('\n', 0, st) + 1
    indent = re.match(r'[ \t]*', s[ls:st]).group(0)
    gated = (NOTE.replace('\n', '\n' + indent)
             + indent + 'const _pre = ' + call + ';\n'
             + indent + "if (!_pre) return { skip: 'precondition never arrived: "
             + name.replace('.js', '') + " had nothing to measure' };")
    s = s[:ls] + gated + s[end + 1:]
    io.open(p, 'w', encoding='utf-8', newline='').write(s)
    done.append(name)

print('gated %d probe(s):' % len(done))
for d_ in done:
    print('  ' + d_)
print('')
print('left alone - final wait already captured and handled (%d):' % len(skipped))
for k in skipped:
    print('  ' + k)
