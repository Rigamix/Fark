# -*- coding: utf-8 -*-
u"""P950 (brief 3.12): the state a table mark needs - landed, hit, and how it ended.

This is the STATE half. It paints nothing; P951 is the paint. Split because the
state is verifiable on its own and the paint is not verifiable without it, and
because a fields-only patch cannot regress anything that reads them today
(nothing does).

THREE FACTS THE MARK DOES NOT CURRENTLY CARRY:

1. WHEN IT LANDED. 3.12 puts the mark on the table at the BANK, and 3.13 makes
   that meaningful: a bust takes this turn's armings, so reaching the table is
   what banking buys. Arming is not landing - a mark armed at keep-time may
   never land at all.
   `shownAt` is stamped at the bank seam, and `flourish` records whether that
   bank actually paid. Denis's split: the arming stays UNGATED so a voided bank
   still arms (LAST CALL and The Reckoning zero the total and fall through), but
   the flourish is gated on !_bankRefused && total>0 - the mark lands either
   way, quietly when the bank was refused.
   Stamped only once: an older mark that landed on a previous turn keeps its
   original moment, or every bank would restart its entrance animation. That is
   the group-stamp-resets-a-per-item-ramp trap, and it is cheap to avoid here.

2. WHETHER IT HIT. 3.3 rules that a miss must look different from a fire, and
   3.12 satisfies that only if the removal path has BOTH branches from the
   start - the cloud thinning and drifting off with the dice untouched, against
   the dice landing in it and it doing its work. Retrofitting a miss onto a form
   designed for a fire is how a failure state gets bolted on later.
   The three fire sites already know: fog by whether a seat was cut, snuff by
   whether a seat was actually dropped (the one-die floor can refuse it), snare
   by whether the marked seat scored. Each calls _lmHit(lane).

3. HOW IT ENDED. _lmSpend is the one place a mark dies, so it is the one place
   the outcome is decided: `outcome` is 'fire' if anything stamped hit, 'miss'
   otherwise, and `endedAt` gives the exit animation its clock. A dead mark is
   kept in the map (it already was) so the ending can play; _lmArm tests `live`,
   so its lane is free again immediately, which is unchanged.

WHY _lmHit RATHER THAN A RETURN VALUE FROM THE FIRE SITES: the sites are three
separate blocks in two different functions, and two of them iterate several due
marks at once (two fogs on two lanes, two snuffs on two seats). Only the site
knows which LANE landed, so the lane is what it reports.
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


# 1 ── the three verbs, beside the rest of the lane-mark machinery ──
sub(u"""function _lmBustDisarm(){""",
    u"""/* P950 (3.12): THE MARK REACHED THE TABLE. Called from the bank seam, once per
   mark. `flourish` says whether the bank that carried it actually paid - a
   voided bank (LAST CALL, The Reckoning) still arms and still lands the mark,
   but lands it quietly.
   STAMPED ONCE. An older mark that landed on a previous turn keeps its own
   moment; re-stamping every mark on every bank would restart the entrance
   animation of a cloud that has been sitting there for a turn, which is a group
   stamp resetting a per-item ramp. */
function _lmLand(flourish){
  if(typeof G==='undefined'||!G)return 0;
  var M=_lmMap(),n=0;
  for(var L in M){
    if(!M.hasOwnProperty(L))continue;
    var m=M[L];
    if(!m||!m.live||m.shownAt)continue;
    m.shownAt=Date.now();m.flourish=!!flourish;n++;
  }
  return n;
}
/* P950: THIS MARK LANDED ON SOMETHING. Reported by lane because the fire sites
   resolve several due marks at once and only the site knows which seat it
   actually took - the snuff's one-die floor can refuse a seat that was due, and
   a fog whose seat is the last readable one is dropped the same way. */
function _lmHit(lane){
  if(typeof G==='undefined'||!G)return false;
  var m=_lmMap()[lane];
  if(!m||!m.live)return false;
  m.hit=true;
  return true;
}
function _lmBustDisarm(){""",
    '1 the land and hit verbs')

# 2 ── the outcome is decided where the mark dies ───────────────────
sub(u"""function _lmSpend(type){""",
    u"""/* P950 (3.3 + 3.12): A MARK ENDS ONE OF TWO WAYS AND THE ENDING IS RECORDED
   HERE, because _lmSpend is the one place a mark dies. `hit` is stamped by the
   fire site that took a seat; anything that comes due and takes nothing has
   MISSED, which is a real outcome under 3.2 - a due mark costs an attempt
   whether it lands or not - and under 3.3 must look different.
   endedAt is the exit animation's clock. The mark stays in the map, dead, so
   the ending has something to play; _lmArm tests `live`, so the lane is free
   again the instant it dies, which is unchanged. */
function _lmEnd(m){
  if(!m)return;
  m.live=false;
  m.outcome=m.hit?'fire':'miss';
  m.endedAt=Date.now();
}
function _lmSpend(type){""",
    '2 the outcome verb')

# 3 ── the bank seam lands the marks ────────────────────────────────
sub(u"""  _turnScoreClear();G.numDice=6;
  /* THE GRUDGE NPC mirror: increment opp's grudge stack when player banks""",
    u"""  /* P950 (3.12): THE MARKS REACH THE TABLE. Here rather than at the credit,
     because The Tab's escrow branch does not credit and does not fire the bank
     hook yet still ends the turn through this line - a hook at G.pPts+= would
     miss it. This is the last point in handleBank where the turn is known to
     have ended in a bank at all.
     UNGATED, per the ruling: a voided bank still arms, so it still lands. Only
     the FLOURISH is gated - LAST CALL and The Reckoning zero the total and fall
     through to here, and a mark landing after a bank that paid nothing should
     not be celebrating. */
  try{_lmLand(!_bankRefused&&total>0);}catch(e){}
  _turnScoreClear();G.numDice=6;
  /* THE GRUDGE NPC mirror: increment opp's grudge stack when player banks""",
    '3 the bank seam lands the marks')

# 4 ── FOG: a cut seat is a hit ─────────────────────────────────────
sub(u"""        if(_fogCuts.length){
          try{famLog('FOG — THEY MISREAD '+(_fogCuts.length>1?'TWO SEATS':'A SEAT'));}catch(e){}""",
    u"""        if(_fogCuts.length){
          /* P950: which LANES were actually blinded - not which were due. The
             one-readable-seat floor above drops cuts, so a due fog can take
             nothing and that is a miss under 3.3. */
          try{_fogCuts.forEach(function(_fc){
            var _fl=_oFree[_fc]&&_oFree[_fc].lane;
            if(typeof _fl==='number')_lmHit(_fl);
          });}catch(e){}
          try{famLog('FOG — THEY MISREAD '+(_fogCuts.length>1?'TWO SEATS':'A SEAT'));}catch(e){}""",
    '4 fog reports the seats it took')

# 5 ── SNUFF: a dropped seat is a hit ───────────────────────────────
sub(u"""        left--;/* the seat itself is dropped where rungDice is built, below */
        _snuffLanes.push(L);""",
    u"""        left--;/* the seat itself is dropped where rungDice is built, below */
        _snuffLanes.push(L);
        try{_lmHit(L);}catch(e){}/* P950: inside the floor, so only seats really taken */""",
    '5 snuff reports the seats it took')

# 6 ── SNARE: a halved seat is a hit ────────────────────────────────
sub(u"""            var _snX2=!!m.x2;
            total=Math.floor(total/(_snX2?4:2));/* Kindred halves it twice */""",
    u"""            var _snX2=!!m.x2;
            try{_lmHit(m.lane);}catch(e){}/* P950: it caught something */
            total=Math.floor(total/(_snX2?4:2));/* Kindred halves it twice */""",
    '6 snare reports the seat it caught')

# 7 ── _lmSpend routes its death through _lmEnd ─────────────────────
# ANCHOR THE WHOLE STATEMENT, NOT ITS FIRST LINE. The first version matched
# only the `if` and inserted an else in front of the `else m.live=false;` that
# was already on the next line - two elses, and the parse gate caught it. A
# two-line statement needs a two-line anchor.
sub(u"""    if(m.turns>0)m.turn=(G.oppTurnCount||0)+1;
    else m.live=false;""",
    u"""    if(m.turns>0)m.turn=(G.oppTurnCount||0)+1;
    /* P950: out of attempts. _lmEnd does what `m.live=false` did and also
       records WHICH of the two endings this was - a fire if any site stamped
       hit, a miss otherwise. 3.3 requires both from the start. */
    else _lmEnd(m);""",
    '7 spend routes death through _lmEnd')

# ── post-asserts ───────────────────────────────────────────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

for fn, n in (('_lmLand', 1), ('_lmHit', 1), ('_lmEnd', 1)):
    if code.count('function %s(' % fn) != n:
        sys.exit('%s is not defined exactly once (nothing written)' % fn)
# THE HIT IS REPORTED BY ALL THREE ENCHANTS, or one of them can never fire
if code.count('_lmHit(') != 4:          # 1 definition + 3 fire sites
    sys.exit('expected 3 _lmHit call sites, found %d (nothing written)'
             % (code.count('_lmHit(') - 1))
if code.count('_lmLand(') != 2:         # 1 definition + the bank seam
    sys.exit('expected exactly one _lmLand caller (nothing written)')
# THE LANDING IS UNGATED AND THE FLOURISH IS NOT - the ruling's exact split
if '_lmLand(!_bankRefused&&total>0)' not in code:
    sys.exit('the flourish is not gated on the bank paying (nothing written)')
# and it must run BEFORE the turn is cleared, or G.kept is already gone
_land = code.index('_lmLand(!_bankRefused')
_clear = code.index('_turnScoreClear();G.numDice=6;', _land - 4000)
if _land > _clear:
    sys.exit('the marks land after the turn is cleared (nothing written)')
# THE STAMP IS ONCE-ONLY, or an old mark restarts its entrance every bank
if 'm.shownAt)continue' not in code:
    sys.exit('the landing re-stamps marks that already landed (nothing written)')
# BOTH ENDINGS EXIST. A form built for a fire with a miss added later is what
# 3.3 exists to prevent, so the miss branch has to be there from the start.
if "m.outcome=m.hit?'fire':'miss'" not in code:
    sys.exit('the two endings are not both recorded (nothing written)')
# AND THE OLD DEATH PATH IS GONE, or a mark can die without an outcome and the
# exit animation has nothing to play
if re.search(r'else m\.live=false;', code):
    sys.exit('a mark can still die without recording an outcome (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
