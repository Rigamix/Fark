# -*- coding: utf-8 -*-
u"""P875 (Denis: "create triggers for them"): the two stranded moments get
their beats, and 91 written rows come alive.

P874 shipped the voice pass with `preroll` and `waiting` rows that nothing
could fire - _DLG_MOMENT maps seven categories and neither was among them.
This adds the two categories and the two events behind them.

WHAT THE LINES THEMSELVES SPECIFY, which is what the triggers are built to:
  preroll  "HERE WE GO!" / "Ooh, my go! My go!" / "Sendin' it." / "Mm."
           -> the PATRON is about to throw. Their turn, before their first
              roll.
  waiting  "ROLL! ROLL 'EM!" / "Still with me, duckling?" / "I could've swept
           the whole room by now." / "Take your time. I mean it."
           -> the patron is waiting on the PLAYER. The player's turn, and
              nothing has happened for a while.
The semantics were never ambiguous; only the cadence was, and the two numbers
that decide it are named below so they are a dial rather than a guess.

PREROLL rides the head of runOppTurn, which runs exactly ONCE per rival turn -
its internal step() is what loops per roll, so the head cannot double-fire.
Probability .3, deliberately matching OPP_HESITATE's dial and for the reason
that dial's own comment gives: "a rival turn holds three or four decisions",
and this beat now competes with the hesitation, the bust and the big bank for
the same window. DLG's existing spacing gate (busyUntil + gap) does the rest.

WAITING is armed on a timer, and the timer is the only genuinely new mechanism
here. It is a setTimeout, NOT an interval: there is no polling, the clock is
re-armed by player input and simply never fires while someone is playing.
  * 9 seconds. Long enough that a player reading the board is not nagged,
    short enough to land while they are still deciding.
  * ONCE PER TURN, latched, reset in startPTurn. A patron who nags twice in
    one turn is a patron you turn the sound off for.
  * Probability 1 at the trigger. The idle threshold and the once-per-turn
    latch ARE the gate; layering a coin flip on top would make the beat feel
    random rather than earned, which is the opposite of what a "get on with
    it" line is for.

RE-ARMED FROM ONE HOOK, not from every player action. A single capture-phase
pointerdown listener on the document resets the clock, so committing a die,
opening a panel, dragging a card and pressing a button all count as "still
there" without instrumenting any of them. Instrumenting N call sites is how a
mechanism like this ends up missing the N+1th.

THREE GUARDS AT FIRING TIME, because a timer that outlives its match is the
classic version of this bug: the match must still exist, it must not have
ended, and the phase must still be one the player can act in (idle or
choosing - never rolling, opp or yielding). The clock is also cleared at the
head of the rival's turn, so the common case never even reaches the guards.

BOSSES STAY SILENT ON BOTH BEATS, and that is a consequence rather than a
decision: a boss match sets no seat art, so these resolve through the trait
pools - and the voice brief wrote patron lines only, so there are no
trait:*:preroll or trait:*:waiting rows to find. getLine returns null and
nothing is shown. Writing boss lines for these beats is a separate ask.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new); edits.append(label); return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


# ── 1. the two moments join the map ──────────────────────────────────
sub(u"""                 OPP_HESITATE_PUSH:'push',OPP_HESITATE_BANK:'banksafe',
                 GRUDGE_TAKEN:'grudge'/* P720: you kept a die of theirs */};""",
    u"""                 OPP_HESITATE_PUSH:'push',OPP_HESITATE_BANK:'banksafe',
                 /* P875: the two the voice pass wrote lines for and nothing
                    could fire. preroll is the patron about to throw; waiting
                    is the patron waiting on YOU. */
                 OPP_TURN_START:'preroll',PLAYER_IDLE:'waiting',
                 GRUDGE_TAKEN:'grudge'/* P720: you kept a die of theirs */};

/* ═══ P875: THE IDLE CLOCK ═══════════════════════════════════════════
   The only new mechanism in this patch, and it is a setTimeout rather than an
   interval on purpose: nothing polls, the clock is re-armed by player input,
   and while somebody is actually playing it simply never fires.
   RE-ARMED FROM ONE HOOK. A single capture-phase pointerdown on the document
   resets it, so committing a die, dragging a card, opening a panel and
   pressing a button all count as "still there" without instrumenting any of
   them - instrumenting N call sites is how this kind of mechanism ends up
   missing the N+1th. */
var DLG_IDLE_MS=9000;      /* long enough to read the board, short enough to land */
var _dlgIdleT=null,_dlgIdleFired=false,_dlgIdleHooked=false;
function _dlgIdleClear(){if(_dlgIdleT){clearTimeout(_dlgIdleT);_dlgIdleT=null;}}
function _dlgIdleFire(){
  _dlgIdleT=null;
  try{
    /* THREE GUARDS, because a timer outliving its match is the classic
       version of this bug: the match must exist, must not have ended, and the
       phase must still be one the player can act in. */
    if(typeof G==='undefined'||!G||G._endMatchFired)return;
    if(G.phase!=='idle'&&G.phase!=='choosing')return;
    var sc=document.getElementById('screen-match');
    if(!sc||!sc.classList.contains('active'))return;
    _dlgIdleFired=true;                 /* once per turn - latched here, not on arm */
    if(window.DLG)DLG.trigger('PLAYER_IDLE');
  }catch(e){}
}
function _dlgIdleArm(){
  _dlgIdleClear();
  if(_dlgIdleFired)return;              /* already nagged this turn */
  _dlgIdleT=setTimeout(_dlgIdleFire,DLG_IDLE_MS);
}
function _dlgIdleHook(){
  if(_dlgIdleHooked)return;_dlgIdleHooked=true;
  try{document.addEventListener('pointerdown',function(){
    if(typeof G==='undefined'||!G)return;
    if(G.phase!=='idle'&&G.phase!=='choosing')return;
    _dlgIdleArm();
  },true);}catch(e){}
}""",
    '1 moments + the idle clock')

# ── 2. the probabilities, beside the dial they are set against ───────
sub(u"""OPP_HESITATE_PUSH:.3,OPP_HESITATE_BANK:.3},""",
    u"""OPP_HESITATE_PUSH:.3,OPP_HESITATE_BANK:.3,
      /* P875. OPP_TURN_START matches the hesitation dial for the reason that
         dial's own note gives - a rival turn holds three or four decisions,
         and this beat now competes with the hesitation, the bust and the big
         bank for the same window.
         PLAYER_IDLE is 1 because its gate is elsewhere and is already strict:
         nine seconds of no input, once per turn. A coin flip on top would make
         a "get on with it" line feel random rather than earned. */
      OPP_TURN_START:.3,PLAYER_IDLE:1},""",
    '2 the two dials')

# ── 3. preroll: the head of the rival's turn ─────────────────────────
sub(u"""function runOppTurn(){
  if(typeof _npcArmActives==='function')_npcArmActives();""",
    u"""function runOppTurn(){
  /* P875: THE PATRON IS ABOUT TO THROW. This is the head of runOppTurn, which
     runs exactly once per rival turn - its internal step() is what loops per
     roll - so the beat cannot double-fire. The player's idle clock is stopped
     in the same breath: their turn is over, and a pending nag must not survive
     into the rival's. */
  try{_dlgIdleClear();}catch(e){}
  try{if(window.DLG)DLG.trigger('OPP_TURN_START');}catch(e){}
  if(typeof _npcArmActives==='function')_npcArmActives();""",
    '3 preroll fires')

# ── 4. waiting: armed at the player's turn start ─────────────────────
sub(u"""function startPTurn(){""",
    u"""function startPTurn(){
  /* P875: a fresh turn earns a fresh nag. The latch resets here - the single
     entry into a player turn - and the clock starts running; any pointerdown
     re-arms it, so it only ever reaches zero if nothing has happened. */
  try{_dlgIdleFired=false;_dlgIdleHook();_dlgIdleArm();}catch(e){}""",
    '4 waiting armed')

# ── post-asserts ─────────────────────────────────────────────────────
for needed in ["OPP_TURN_START:'preroll'", "PLAYER_IDLE:'waiting'",
               'function _dlgIdleFire(', 'function _dlgIdleArm(',
               'function _dlgIdleClear(', 'var DLG_IDLE_MS=9000;',
               "DLG.trigger('OPP_TURN_START')", "DLG.trigger('PLAYER_IDLE')"]:
    if needed not in s:
        sys.exit('KEEPER MISSING: %s (nothing written)' % needed)
# exactly one arm site and one latch reset, or the once-per-turn rule is a lie
# the RESET site, not the token: the declaration initialises the latch to false
# too, so a bare count is 2 on a correct patch.
if s.count('try{_dlgIdleFired=false;') != 1:
    sys.exit('the latch is reset from %d places, expected 1 (nothing written)'
             % s.count('try{_dlgIdleFired=false;'))
if s.count('setTimeout(_dlgIdleFire,DLG_IDLE_MS)') != 1:
    sys.exit('the clock is armed from %d places, expected 1 (nothing written)'
             % s.count('setTimeout(_dlgIdleFire,DLG_IDLE_MS)'))
# the fire path must carry all three guards
_fire = s[s.index('function _dlgIdleFire('):s.index('function _dlgIdleArm(')]
for g in ['_endMatchFired', "G.phase!=='idle'", "classList.contains('active')"]:
    if g not in _fire:
        sys.exit('THE FIRE GUARD IS MISSING %s - a timer that outlives its '
                 'match is the whole hazard here (nothing written)' % g)
# and only ONE global listener, added once
if s.count("addEventListener('pointerdown',function(){") < 1:
    sys.exit('the re-arm hook is missing (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
