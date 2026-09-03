# -*- coding: utf-8 -*-
u"""P923: TAR PIT never took a die away, and its own message said it did.

THE BUG. In startPTurn the rival-cast Tar Pit spends its charge and sets the
player's dice count nine lines BEFORE the line that rebuilds the hand:

    if(G&&G._oTarPit>0){
      G._oTarPit--;G.numDice=Math.min(G.numDice||6,5);
      famLog('TAR PIT - YOU ROLL '+G.numDice);
    }
    ...
    G.phase='idle';G.turnPts=0;G.kept=[];G.numDice=G.matchDice?G.matchDice.length:6;

numDice is set to 5 and overwritten with 6. The charge is still consumed and the
log still reads "TAR PIT - YOU ROLL 5", so the card is spent, the player is told
it worked, and the player rolls six dice. A rival card that does nothing, with a
message vouching for it.

WHISPER'S HEX IS THE PROOF AND THE FIX. It does the same thing - lowers numDice
by one - from BELOW the rebuild, and it works. It also survives the later clamp,
because that clamp is Math.min(loadout, numDice) and its own comment is explicit:
"The loadout term is a CEILING, not a floor - it cannot rescue a numDice ...
anything that lowers numDice mid-turn is now load-bearing on this line." So the
block simply belongs beside the Hex block, which is where it goes.

THE FILE ALREADY NAMED THIS HAZARD, TWICE, ABOUT A DIFFERENT CARD. Preserve's
comment records being wrong in exactly this shape: "First: four lines above
`G.kept=[];G.numDice=matchDice.length`, so the data was overwritten before the
turn began and Preserve announced 'THE AMBER CRACKS' having delivered nothing."
Same wipe, same position, same announce-without-effect. It ends "Anything added
below that clears the row belongs ABOVE this block" - the reciprocal rule, that
anything the rebuild would overwrite belongs BELOW the rebuild, was the half
nobody wrote down.

The rival-side version at 37212 sets numDice in a different function and is not
affected.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


# ── 1. lift it out of the dead position ─────────────────────────────
sub(u"""  if(G&&G._oTarPit>0){
    G._oTarPit--;G.numDice=Math.min(G.numDice||6,5);
    famLog('TAR PIT \u2014 YOU ROLL '+G.numDice);
  }
""",
    u"""  /* P923: TAR PIT MOVED DOWN, beside Whisper's Hex - see there. It sat here,
     above `G.kept=[];G.numDice=matchDice.length`, so it spent its charge, said
     "YOU ROLL 5" and was overwritten with 6 before the turn began. */
""",
    '1 the dead position is emptied')

# ── 2. put it where it survives, beside the card that already does ──
sub(u"""  /* NPC-armed Whisper's Hex: reduce player's dice count this turn */
  if(G._npcHexArmed){""",
    u"""  /* P923: TAR PIT, which never took a die away. It used to sit nine lines
     above `G.kept=[];G.numDice=G.matchDice?G.matchDice.length:6`, so numDice
     went to 5 and was immediately overwritten with 6 - while the charge was
     still spent and famLog still said "TAR PIT - YOU ROLL 5". A card that did
     nothing, with a message vouching for it.
     IT BELONGS HERE BECAUSE WHISPER'S HEX IS HERE. Both are rival-cast dice
     reducers, and the Hex has always worked for exactly one reason: it runs
     BELOW the rebuild. Both also survive the clamp at the roll, which is
     Math.min(loadout, numDice) - a CEILING, not a floor, as that line's own
     comment says, so anything lowering numDice from below the rebuild holds.
     THE FILE HAD ALREADY NAMED THIS HAZARD, about Preserve, twice: "four lines
     above `G.kept=[];G.numDice=matchDice.length`, so the data was overwritten
     before the turn began and Preserve announced 'THE AMBER CRACKS' having
     delivered nothing." Same wipe, same position, same announce-without-effect.
     That comment ends "anything added below that clears the row belongs ABOVE
     this block"; the reciprocal - anything the rebuild would overwrite belongs
     BELOW the rebuild - is the half that was never written down. It is now. */
  if(G&&G._oTarPit>0){
    G._oTarPit--;G.numDice=Math.min(G.numDice||6,5);
    famLog('TAR PIT \u2014 YOU ROLL '+G.numDice);
  }
  /* NPC-armed Whisper's Hex: reduce player's dice count this turn */
  if(G._npcHexArmed){""",
    '2 it moves below the rebuild')

# ── post-asserts ────────────────────────────────────────────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

# exactly one tar pit consumption block, and it is BELOW the rebuild
if code.count('G._oTarPit--') != 1:
    sys.exit('tar pit is consumed %d times (nothing written)' % code.count('G._oTarPit--'))
_rebuild = code.index("G.kept=[];G.numDice=G.matchDice?G.matchDice.length:6")
_tar = code.index('G._oTarPit--')
if _tar < _rebuild:
    sys.exit('tar pit still runs before the rebuild that overwrites it (nothing written)')
# and it sits beside the card that proves the position works
_hex = code.index('G._npcHexArmed=false')
if abs(_tar - _hex) > 400:
    sys.exit('tar pit did not land beside the hex block (nothing written)')
# the hex block itself is untouched and still below the rebuild
if _hex < _rebuild:
    sys.exit("Whisper's Hex moved above the rebuild (nothing written)")
if code.count('G.numDice=Math.max(3,G.numDice-1)') != 1:
    sys.exit('the hex block was disturbed (nothing written)')
# the clamp that both depend on is unchanged - it is a ceiling, not a floor
if code.count('G.numDice=Math.min((G.matchDice?G.matchDice.length:6)') != 1:
    sys.exit('the roll clamp changed (nothing written)')
# the rival-side tar pit, in another function, is untouched
if code.count('G.numDice=Math.max(1,6-_cut)') != 1:
    sys.exit('the rival-side dice cut was disturbed (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
