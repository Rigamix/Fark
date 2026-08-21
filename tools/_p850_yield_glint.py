# -*- coding: utf-8 -*-
"""P850: the yield window lights up.

Measured for Denis's ruling-1 gate (apv_yield_window): the
timing:'yielding' window is 853ms, canActivateCard is true for all of
it, and the card sits on screen the whole time - but NOTHING signals
it. The glint never fires, and both buttons go .disabled, which reads
as "hands off" at the exact moment the card is playable.

The cause is one phase of ordering: _updateCardGlints runs from updHUD
(30148), which happens BEFORE showYieldButton sets G.phase='yielding',
so every glint is computed against the previous phase and never
recomputed while the window is open. _glintReady's own default branch
names "yield-window cards" as the case it serves - the call just never
arrives during the window.

This is the SIGNAL half only. The reroll build behind this gate stays
parked on Denis's ruling, per his instruction to report the
measurement before writing it.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

old = """  G.phase='yielding';
  document.getElementById('btnRoll').classList.add('disabled');
  document.getElementById('btnBank').classList.add('disabled');"""
new = """  G.phase='yielding';
  document.getElementById('btnRoll').classList.add('disabled');
  document.getElementById('btnBank').classList.add('disabled');
  /* P850: LIGHT THE WINDOW. Measured: this phase is open for ~850ms
     with canActivateCard true throughout and the card on screen - and
     nothing said so, because glints refresh from updHUD, which runs
     one phase earlier. _glintReady's default branch already serves
     "yield-window cards"; the call simply never arrived while the
     window was open. Both buttons are .disabled here, which reads as
     "wait" - so an unlit yield-timing card is invisible by default. */
  if(typeof _updateCardGlints==='function'){try{_updateCardGlints();}catch(e){}}"""

# the house sub(): this region is CRLF while others are LF, so match
# exact first, then the \r?\n fallback, preserving the site's endings
if s.count(old) == 1:
    s = s.replace(old, new)
else:
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d (nothing written)' % len(ms))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: the yield window refreshes glints')
