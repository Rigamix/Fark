# -*- coding: utf-8 -*-
u"""P948 (brief 3.13): a bust disarms this turn's armings. Bank keeps, bust clears.

THE RULING, and why it is a mechanic rather than a display rule. I had found
that doBust never touches G._laneMark and proposed fitting the DISPLAY to that -
revealing at turn end so a mark could never fire unseen. Denis ruled the other
way and upstream: the behaviour was wrong, not the reveal. Arming was previously
free of risk, so "I have armed a snare - do I push or lock it in?" was not a
decision. Now it is. A branded die already never scores (3.4), so a brand was
always a commitment; this gives it a moment of jeopardy.

With the disarm in place a mark survives to the rival's turn IF AND ONLY IF the
turn ended in a bank, so 3.12's original wording - the mark appears when the die
is banked - is literally correct and needs no fallback. The turn-end trigger I
proposed is not built.

ONLY THIS TURN'S ARMINGS. A mark armed two turns ago and still pending survives:
a bank already paid for it. That cannot be read off m.turn - _lmSpend re-stamps
turn for a Kindred mark's second attempt (24945), so a re-stamped old mark and a
fresh arming look identical. The arming turn is recorded separately, as armedOn.
G.pTurns is the right counter: it counts COMPLETED player turns and increments in
endPTurn (37250), so it is constant for the whole turn and still un-incremented
when doBust runs.

WHERE. The file already names the point, at 35653: "THE bust event, on the path
where a bust actually happened. Everything above either returned or continued
the turn." Amber's shield returns ABOVE it, so an eaten bust disarms nothing and
the turn goes on. The ward branch is BELOW it, and should disarm - the ward pays
half and ends the turn, which is a bust with a consolation, not a bank.

A ZEROED BANK STILL ARMS, and that is the rule rather than an exception to it.
LAST CALL and The Reckoning set total=0 and fall through, so famFire('bank')
runs: the player ended the turn voluntarily and safely and got nothing for it.
Bank keeps, bust clears - one sentence, no special cases. Nothing here tests
_bankRefused; that gate belongs only to 3.12's flavour beat.

LEGACY SAVES: a mark snapshotted before this patch has no armedOn, and
undefined === (G.pTurns||0) is false, so it SURVIVES a bust. That is the
conservative direction - an old save keeps an effect the player paid for rather
than losing one it never knew was at risk.
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


# 1 ── the mark records the turn it was armed on ────────────────────
sub(u"""  var m={t:type,lane:lane,live:true,turn:(G.oppTurnCount||0)+1,turns:turns||1};""",
    u"""  /* P948 (3.13): armedOn is the PLAYER turn this mark was placed on, and it is
     a separate field because `turn` cannot answer the question. _lmSpend
     re-stamps `turn` for a Kindred mark's second attempt, so an old mark that
     has already been paid for by a bank and a mark placed thirty seconds ago
     are indistinguishable by it. G.pTurns counts COMPLETED player turns and is
     incremented in endPTurn, so it is constant across the turn being played. */
  var m={t:type,lane:lane,live:true,turn:(G.oppTurnCount||0)+1,turns:turns||1,
         armedOn:(G.pTurns||0)};""",
    '1 the mark records its arming turn')

# 2 ── the disarm itself, beside the rest of the lane-mark verbs ────
sub(u"""function _lmDueList(type){""",
    u"""/* P948 (brief 3.13): A BUST TAKES THIS TURN'S ARMINGS WITH THE POINTS.
   Bank keeps, bust clears. Arming used to be free of risk, which made "push or
   lock it in?" a non-decision; a brand already banks nothing under 3.4, so this
   is the jeopardy that makes the commitment mean something.
   ONLY THIS TURN'S. A mark armed on an earlier turn was already paid for by the
   bank that ended that turn, and survives. A mark with no armedOn at all - one
   restored from a snapshot written before this patch - also survives, which is
   the conservative direction for a save that never knew the risk existed. */
function _lmBustDisarm(){
  if(typeof G==='undefined'||!G)return 0;
  var now=(G.pTurns||0),M=_lmMap(),n=0;
  for(var L in M){
    if(!M.hasOwnProperty(L))continue;
    var m=M[L];
    if(!m||!m.live)continue;
    if(m.armedOn!==now)continue;
    m.live=false;n++;
  }
  return n;
}
function _lmDueList(type){""",
    '2 the disarm verb')

# 3 ── called where the file says a bust actually happened ──────────
sub(u"""  /* THE bust event, on the path where a bust actually happened. Everything
     above either returned or continued the turn. */
  try{famFire('bust',{actor:'p',lost:_bustLost});}catch(e){}""",
    u"""  /* THE bust event, on the path where a bust actually happened. Everything
     above either returned or continued the turn. */
  try{famFire('bust',{actor:'p',lost:_bustLost});}catch(e){}
  /* P948 (3.13): AND THE ARMINGS GO WITH THE POINTS. This is the one place the
     file already identifies as "a bust actually happened", which is exactly the
     scope the ruling needs: Amber's shield returns above it, so an eaten bust
     disarms nothing and the turn continues, while the ward branch sits below it
     and does disarm - the ward pays half and ENDS the turn, which is a bust with
     a consolation rather than a bank. */
  try{
    var _lmGone=_lmBustDisarm();
    if(_lmGone)famLog(_lmGone>1?'THE BRANDS GO WITH THE TURN':'THE BRAND GOES WITH THE TURN');
  }catch(e){}""",
    '3 the bust disarms')

# ── post-asserts, against code with comments stripped ──────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

if 'armedOn:(G.pTurns||0)' not in code:
    sys.exit('the arming turn is not recorded (nothing written)')
if code.count('function _lmBustDisarm(') != 1:
    sys.exit('the disarm verb is not defined exactly once (nothing written)')
if code.count('_lmBustDisarm()') != 2:      # the definition + the one call
    sys.exit('expected exactly one caller of _lmBustDisarm, found %d '
             '(nothing written)' % (code.count('_lmBustDisarm()') - 1))
# IT MUST BE SCOPED TO THIS TURN, or a bust eats marks a bank already paid for
if 'm.armedOn!==now' not in code:
    sys.exit('the disarm is not scoped to this turn (nothing written)')
# AND IT MUST SIT BELOW THE AMBER RETURN. Measured by position rather than by
# reading: the call has to come after the famFire('bust') the file identifies as
# the real-bust point, and there must be exactly one of those.
if code.count("famFire('bust',{actor:'p',lost:_bustLost})") != 1:
    sys.exit('the real-bust event is not unique (nothing written)')
if code.index('_lmBustDisarm();') < code.index("famFire('bust',{actor:'p',lost:_bustLost})"):
    sys.exit('the disarm runs before the bust is final (nothing written)')
# the ruling explicitly does NOT gate on the bank being refused
if re.search(r'_bankRefused[\s\S]{0,120}_lmBustDisarm', code):
    sys.exit('the disarm is entangled with the bank gate (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
