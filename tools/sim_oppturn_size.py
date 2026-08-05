# -*- coding: utf-8 -*-
u"""Sizing the sim's opponent-turn fix. Measured, not estimated.

RULED: build it. The sim's F.oppTurn reimplements the opponent's turn loop and
so never runs finOpp's nine card branches - a patron that punishes the player
but structurally cannot help itself.

THE QUESTION IS NOT "HOW MANY LINES". It is why finOpp was reimplemented in the
first place, because that reason is the actual work. The harness comment says
runOppTurn is "an animation chain end to end" - so the blocker is presentation
and timers braided through the state changes, not the state changes themselves.

So this counts, inside finOpp:

  STATE lines      score pools, banks, card flags - what the sim needs
  PRESENTATION     triggerCard, spawnPop, setStatusMsg, DLG, setTimeout,
                   document/DOM - what the sim cannot run and does not want
  BRAIDED lines    both in one statement - the ones that cannot simply be
                   skipped, and therefore the ones that decide the approach

A high braided count means the branches must be SPLIT before either caller can
share them, which is the same move as the BANK_FX tables one level up: pull the
rule out, leave the presentation at the call site. A low braided count means the
sim could call finOpp behind a quiet flag and the job is much smaller.

That distinction is the estimate. Everything else is line counting.
"""
import io, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = io.open(os.path.join(ROOT, 'fark_proto.html'), encoding='utf-8').read()
h = io.open(os.path.join(ROOT, 'tools', 'sim_harness.js'), encoding='utf-8').read()

def fnbody(src, name):
    for m in re.finditer(r'\bfunction\s+' + re.escape(name) + r'\s*\(', src):
        b = src.index('{', m.end() - 1)
        d, j = 0, b
        while j < len(src):
            if src[j] == '{':
                d += 1
            elif src[j] == '}':
                d -= 1
                if d == 0:
                    return src[b:j + 1]
            j += 1
    return ''

fin = fnbody(s, 'finOpp')
oppsim = ''
m = re.search(r'F\.oppTurn\s*=\s*function', h)
if m:
    b = h.index('{', m.end() - 1)
    d, j = 0, b
    while j < len(h):
        if h[j] == '{':
            d += 1
        elif h[j] == '}':
            d -= 1
            if d == 0:
                oppsim = h[b:j + 1]
                break
        j += 1

PRES = re.compile(r'triggerCard|spawnPop|setStatusMsg|famLog|DLG\.|spawnPixelSparks|'
                  r'setTimeout|document\.|querySelector|classList|innerHTML|style\.|'
                  r'updHUD|refreshKeptTray|_renderSelTags|spawnBankPop|SFX\.')
STATE = re.compile(r'G\.(oPts|pPts|npcCardState|oCards|target|oTurns)|oppBank|pts\s*[-+*/]?=')

# STATEMENTS, NOT LINES. A first version split on newlines and reported
# `pts=BANK_FX.flat_bonus(pts,eff);triggerCard(...)` as braided - but that is TWO
# statements sharing a line, trivially separable. JS separates statements with
# `;`, and measuring the wrong unit overstates the work. The same proxy mistake
# as every other one tonight, on the unit of measurement this time.
_raw = re.sub(r'/\*.*?\*/', '', fin, flags=re.S)
lines = [x.strip() for x in re.split(r';|\n', _raw) if x.strip()]
pres = [l for l in lines if PRES.search(l) and not STATE.search(l)]
state = [l for l in lines if STATE.search(l) and not PRES.search(l)]
braid = [l for l in lines if STATE.search(l) and PRES.search(l)]

print('finOpp:            %d code lines' % len(lines))
print('  state only:      %d' % len(state))
print('  presentation:    %d' % len(pres))
print('  BRAIDED:         %d  <- the ones that decide the approach' % len(braid))
print('  neither:         %d' % (len(lines) - len(pres) - len(state) - len(braid)))
print('\nF.oppTurn (sim):   %d code lines'
      % len([l for l in oppsim.split('\n') if l.strip()]))

print('\nBRAIDED LINES, which is where the work actually is:')
for l in braid[:10]:
    print('  ' + l.encode('ascii', 'replace').decode()[:96])
if len(braid) > 10:
    print('  ... and %d more' % (len(braid) - 10))

# how many of the nine branches contain a braided line?
MECHS = ['challenge', 'double_first_bank', 'flat_bonus', 'gain_when_ahead',
         'steal_pct', 'halve_first_bank', 'steal_low_bank', 'block_low_bank',
         'periodic_drain']
print('\nPER BRANCH - can it be shared without splitting?')
need_split = 0
for mech in MECHS:
    mm = re.search(r"mechanic\s*===\s*'" + mech + r"'", fin)
    if not mm:
        print('  %-20s not in finOpp' % mech)
        continue
    b = fin.find('{', mm.end())
    d, j = 0, b
    while j < len(fin) and j - b < 2500:
        if fin[j] == '{':
            d += 1
        elif fin[j] == '}':
            d -= 1
            if d == 0:
                break
        j += 1
    blk = fin[b:j + 1]
    bl = [x.strip() for x in re.split(r';|\n', re.sub(r'/\*.*?\*/', '', blk, flags=re.S)) if x.strip()]
    nb = len([l for l in bl if STATE.search(l) and PRES.search(l)])
    if nb:
        need_split += 1
    print('  %-20s %s' % (mech, ('%d braided line(s) - SPLIT' % nb) if nb else 'clean - shareable as-is'))

print('\n%d of %d branches need splitting before either caller can share them.'
      % (need_split, len(MECHS)))
print("""
READ THAT AS THE ESTIMATE. Branches that are clean can move behind a quiet flag
today. Branches with braided lines need the rule pulled out and the presentation
left at the call site - the same move as BANK_FX, one level up, and the reason
this is real work rather than a flag.""")
