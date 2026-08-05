# -*- coding: utf-8 -*-
u"""P469 - the sixth design law, and the off-by-one it explains.

RULED: whatever applies to the player applies to the NPC by default. Asymmetry
needs a STATED reason, never a silence. Written into the brief as a standing law
rather than left as one card's fix, because tonight's mirror-pair investigation
was five separate instances of that default being violated by accident:

  challenge      the rival over-charged, the player under-charged  (P466/P467)
  ill_omen       "busted" one side, "scored nothing" the other     (P463)
  gain_when_ahead  a default on one seat only                      (P465)
  gain_pts / punish_busts  the same, twice                         (P468)
  bust_immune_turns  one turn against two                          (this patch)

Not one was a decision. Every one was a silence.

THE BASE CHECK MATTERED HERE, and nearly overturned the finding. `<` against
`<=` only means something if the counters share a base:

  G.turnNum                     inits 1, increments at turn END   -> 1 on turn 1
  G.npcCardState.oppTurnCount   inits 0, increments at turn START -> 1 on turn 1

Same base, so the operators really do differ: with turns:2 the player is immune
on turns 1 AND 2, the boss only on turn 1. Had oppTurnCount incremented at the
END the two would have covered identical turns and there would have been no bug
at all - which is why this was measured rather than read off the operator.

The boss's copy now matches the player's exactly, including the `||2` default
the player already had and the boss did not.
"""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'fark_proto.html')
BRIEF = os.path.join(ROOT, 'docs', 'briefs', 'FARK_MASTER_BRIEF.md')

# ── the law ──
with io.open(BRIEF, encoding='utf-8') as f:
    b = f.read()
LAW5 = (u"5. Colour belongs to FAMILIES exclusively. Trait seals are single-colour\n"
        u"   wax (dark red), distinguished by symbol only. Tier is border metal\n"
        u"   (tin/silver/gold) plus a roman numeral.")
assert b.count(LAW5) == 1, 'law 5 matched %d' % b.count(LAW5)
b = b.replace(LAW5, LAW5 + u"""
6. SYMMETRY BY DEFAULT. Whatever applies to the player applies to the NPC,
   and whatever applies to the NPC applies to the player. A rule that reads
   differently from the two seats needs a STATED reason — in the code and
   here. **Asymmetry is a design choice, never a silence.**
   THE NAMED EXCEPTION IS `challenge`: the player's terms are frozen when it
   is declared, because it spans a turn; the rival resolves immediately and
   reads them live. That is deliberate and documented. `bust_survive` is the
   second: an unconditional save for the player, a chance-based half-save for
   the boss, kept apart as a personality lever.
   Anything else that diverges is a bug until ruled otherwise. Five were
   found in one night — `challenge`, `ill_omen`, `gain_when_ahead`,
   `gain_pts`/`punish_busts`, `bust_immune_turns` — and not one was a
   decision.""")
with io.open(BRIEF, 'w', encoding='utf-8', newline='') as f:
    f.write(b)

# ── the fix ──
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

OLD = u"if(eff.mechanic==='bust_immune_turns'&&G.npcCardState.oppTurnCount<eff.turns)"
assert s.count(OLD) == 1, 'boss bust_immune_turns matched %d' % s.count(OLD)
s = s.replace(OLD, u"/* LAW 6: matches the player's copy exactly - `<=` and the same ||2\n"
                   u"             default. Both counters read 1 on their first turn (turnNum inits\n"
                   u"             1 and bumps at turn END; oppTurnCount inits 0 and bumps at turn\n"
                   u"             START), so `<` really did give the boss one turn against the\n"
                   u"             player's two. */\n"
                   u"            if(eff.mechanic==='bust_immune_turns'"
                   u"&&G.npcCardState.oppTurnCount<=(eff.turns||2))")

assert s != orig, 'nothing changed'
import re
body = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
assert body.count("G.npcCardState.oppTurnCount<=(eff.turns||2)") == 1
assert "G.npcCardState.oppTurnCount<eff.turns" not in body, 'old strict form still live'
# the player's copy is untouched
assert body.count("G.turnNum<=(_biC.effect.turns||2)") == 1, 'player copy changed'
# P468's tables undisturbed
assert body.count('BUST_FX.') == 9 and body.count('BANK_FX.') == 8

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P469 applied: law 6 written; bust_immune_turns matches the player')
