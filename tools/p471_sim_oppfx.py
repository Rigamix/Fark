# -*- coding: utf-8 -*-
u"""P471 - the sim runs the patron turn's card effects. The stop can lift.

RULED: build it. F.oppTurn reimplemented the opponent's turn loop and so ran NO
bank-triggered card effects for either seat. P470 extracted finOpp's four loops
into named functions; this wires them into the sim and silences the presentation
they call.

ORDER MATCHES finOpp EXACTLY, which is the whole point - a sim that applies the
same effects in a different order measures a different game, which is the thing
this was supposed to stop doing:

  _oppFxOwnA(bank)    patron's own cards
  _oppFxOwnB(bank)    patron's own cards
  _oppFxPlayer(bank)  the PLAYER's cards, taking from the patron's bank
  G.oPts += bank      <- the bank lands
  _oppFxDrain()       periodic_drain, after

AND ONLY ON A SUCCESSFUL BANK. finOpp is called when the patron banks and not
when it busts, so guarding on !out.busted is what reproduces that - applying
them on a bust would invent behaviour the game does not have.

QUIET: triggerCard, setStatusMsg and famLog join _QUIET_FN. They are
side-effect-only - no return value, no caller consuming one, and no writes to G
or S.

updHUD IS DELIBERATELY NOT STUBBED, and that is the interesting one. It looks
like pure presentation and it is not: it writes G._featMaxDeficit, which a feat
condition reads (`check:function(G){return (G._featMaxDeficit||0)>=2000;}`).
Stubbing it would trade a real correctness risk for an UNMEASURED speed guess,
and the failure would be the quietest kind - no crash, no visibly wrong number,
just a feat condition reading a value that stopped updating. Side-effect-free
and state-write-free are different claims; only the second one matters here.
"""
import io, os, re

H = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 'tools', 'sim_harness.js')
with io.open(H, encoding='utf-8') as f:
    s = f.read()
orig = s

# ── 1. wire the four calls, in finOpp's order ──
OLD = u"if(!out.busted){G.oPts=(G.oPts||0)+bank;out.banked=bank;}"
assert s.count(OLD) == 1, 'bank-lands line matched %d' % s.count(OLD)
s = s.replace(OLD, u"""/* P471 - THE PATRON'S CARD EFFECTS, in finOpp's exact order. Without these
     the sim modelled a game where no bank-triggered card fired for either seat:
     three of the nine are the patron's own, six are the PLAYER's taking from
     the patron's bank. Guarded on !busted because finOpp is only called when
     the patron banks. Guarded on typeof so an older page still runs. */
  if(!out.busted){
    if(typeof _oppFxOwnA==='function')  bank=_oppFxOwnA(bank);
    if(typeof _oppFxOwnB==='function')  bank=_oppFxOwnB(bank);
    if(typeof _oppFxPlayer==='function')bank=_oppFxPlayer(bank);
    G.oPts=(G.oPts||0)+bank;out.banked=bank;
    if(typeof _oppFxDrain==='function') _oppFxDrain();
  }""")

# ── 2. silence the three that are safe to silence ──
m = re.search(r'_QUIET_FN\s*=\s*\[', s)
assert m, '_QUIET_FN not found'
end = s.index(']', m.start())
assert "'triggerCard'" not in s[m.start():end], 'triggerCard already quiet'
s = s[:end] + (u",\n  /* P471: side-effect-only - no return value, no caller consuming one, no\n"
               u"     writes to G or S. updHUD is NOT here on purpose: it writes\n"
               u"     G._featMaxDeficit, which a feat condition reads. */\n"
               u"  'triggerCard','setStatusMsg','famLog'") + s[end:]

assert s != orig, 'nothing changed'
# TWICE EACH, BY DESIGN: once in the `typeof` guard, once in the call. The
# first version of this assert expected 1 and fired - the expectation was
# wrong, not the patch, which is exactly what an assert is for.
for n in ['_oppFxOwnA', '_oppFxOwnB', '_oppFxPlayer', '_oppFxDrain']:
    assert s.count(n) == 2, '%s appears %d times, expected 2' % (n, s.count(n))
# the calls sit in the right order relative to the bank landing
i_a = s.index('_oppFxOwnA'); i_p = s.index('_oppFxPlayer')
i_bank = s.index('G.oPts=(G.oPts||0)+bank'); i_d = s.index('_oppFxDrain')
assert i_a < i_p < i_bank < i_d, 'call order does not match finOpp'
for q in ["'triggerCard'", "'setStatusMsg'", "'famLog'"]:
    assert s.count(q) >= 1, '%s not added to _QUIET_FN' % q
assert "'updHUD'" not in s, 'updHUD must NOT be stubbed - it writes _featMaxDeficit'

with io.open(H, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P471 applied: sim runs the four card-effect functions; 3 fns silenced, updHUD left alone')
