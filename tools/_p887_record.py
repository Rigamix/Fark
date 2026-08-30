# -*- coding: utf-8 -*-
u"""P887: five corrections to the record, and one counter that makes a claim
testable. An adversarial audit of P879-P884 found these; none is a behaviour
change except the counters.

1. A FOURTH COMMENT STILL ARGUED FOR THE DELETED SPLIT, and it is the worst
   sited of the four: the docblock of _lmSpend itself, which says "Snare does
   not call this - see the note above" while the snare block calls exactly
   this. P879 said it had updated all three; there were four. Its own standard
   applies - a stale claim in a function's own docblock is worse than the three
   it did fix, because that is where a reader looks first.

2. THE STAGGER CLAIM IS TRUE OF ONE EXIT, NOT BOTH. _landed's comment says the
   hook is at the die's own settle "because the tape ends on the last die, and
   six jolts fired together are one noise". That holds for _physPose, which
   runs per drawn die per frame. The WATCHDOG retires every overdue die in ONE
   pass, so on that path the beats do batch - measured, three inside 1ms. It is
   the right trade (the watchdog only catches dice the frame never drew) but
   the comment claimed a property the code does not have on both paths.
   _landedVia counts the exits so the claim is testable at all: before this,
   no probe could tell which exit had fired, and measurement showed the
   _physPose exit - the one players actually take - had never been exercised.

3. THE COST BOUND WAS BORROWED FROM A NOTE THAT DOES NOT COVER IT. P879's
   cardmark comment reaches for "the same thing the note below says about the
   selection glow: one thin hull on an otherwise empty surface". That note
   actually reads "this canvas is only painted WHILE DICE ARE SELECTED, and it
   is one thin shape on an otherwise empty surface" - and the selection
   condition is precisely what P876 widened and what the state layer discards
   outright. The bound may well hold; it is not inherited, so it is stated on
   its own terms and marked unmeasured. Step 7 builds on this, so it matters
   that it is not resting on a borrowed premise.

4. _beam IS REACHABLE FROM NOTHING ON A DIE. P883 shipped all three primitives
   onto the over-canvas and its commit called that "PAY's glow and beam, and
   STRIKE's flash". Resolved at runtime: the only play() site that passes a die
   element is the enchant keep, and no enchant id resolves to PAY, FATE or ARM.
   So on a die, _flash arrives via BREAK (not STRIKE), _glow only through
   moment 2, and _beam through nothing at all. The primitives are correct and
   worth having; the reach was overstated, and the note now says where each one
   actually arrives so nobody assumes _beam is exercised.

5. FOUR LINE CITATIONS WERE STALE. Comments are this file's navigation and
   these were cited as evidence in commits. Rather than update numbers that go
   stale on the next patch - all four were stale within one session - they are
   replaced by the name of the thing being pointed at, which does not drift.
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


# ── 1. the fourth stale comment ─────────────────────────────────────
sub(u"""/* Spend one turn of the window: re-arm for the next opponent turn, or retire.
   Snare does not call this - see the note above. */""",
    u"""/* Spend one ATTEMPT: re-arm for the next opponent turn, or retire.
   P887: this used to name Snare as the one mark that never reached this
   function, and Snare has reached it since P879 - which claimed to have
   updated all three comments arguing for the old split and missed the one
   sitting on the function itself. By its
   own standard that is the worst of the four: a reader checking what _lmSpend
   is for looks here first. All three marks spend once per due turn now. */""",
    '1 the fourth stale comment')

# ── 2. the exits are counted, and the stagger claim is scoped ───────
sub(u"""     It is hooked at the DIE's own settle rather than the tape's end because
     the tape ends on the last die, and six jolts fired together are one noise.""",
    u"""     It is hooked at the DIE's own settle rather than the tape's end because
     the tape ends on the last die, and six jolts fired together are one noise.
     P887: THAT IS TRUE OF _physPose AND NOT OF THE WATCHDOG. _physPose runs
     per drawn die per frame, so each die's beat lands on its own frame and the
     stagger is free. The watchdog retires every overdue die in ONE pass, so
     beats batch there - measured, three inside 1ms. That is the right trade,
     because the watchdog only ever catches dice the frame never drew, but the
     sentence above was claiming a property this code has on one path of two.
     _landedVia counts the exits: before it, nothing could tell which had
     fired, and the _physPose exit - the one players take - had never once been
     exercised by a probe.""",
    '2 the stagger claim scoped')

sub(u"""  _landed:function(d){
    if(!d||!d.match||!d.chip)return false;""",
    u"""  _landedVia:{physPose:0,watchdog:0},
  _landed:function(d,via){
    if(via&&this._landedVia[via]!==undefined)this._landedVia[via]++;
    if(!d||!d.match||!d.chip)return false;""",
    '3 the exit counter')

sub(u"""      this._landed(d);/* P884b: one of TWO settle exits - see _landed */""",
    u"""      this._landed(d,'physPose');/* P884b: one of TWO settle exits - see _landed */""",
    '4 physPose tags its exit')

sub(u"""      D3X._landed(d);/* P884b: the OTHER settle exit - the rule above applies
                        to the beat exactly as it applies to the payload */""",
    u"""      D3X._landed(d,'watchdog');/* P884b: the OTHER settle exit - the rule
                        above applies to the beat exactly as it applies to the
                        payload. P887: and this one batches - see _landed */""",
    '5 the watchdog tags its exit')

# ── 3. the cost bound stands on its own ─────────────────────────────
sub(u"""           player deliberates. What actually bounds the cost is the same thing
           the note below says about the selection glow: one thin hull on an
           otherwise empty surface, which holds however long the mark lives.
           The state layer is built on this next, and states are long-lived by
           definition - so it must not inherit an argument about transience. */""",
    u"""           player deliberates.
           P887: AND THE BOUND IS NOT BORROWED, because the note it was taken
           from does not cover this. That note reads "this canvas is only
           painted WHILE DICE ARE SELECTED, and it is one thin shape on an
           otherwise empty surface" - and the selection condition is exactly
           what P876 widened and what the state layer discards. So, on its own
           terms: the cost is one thin hull per marked die per frame on a
           surface that is otherwise empty, and the pass sleeps entirely when
           no die carries a registered class. That is per-frame and independent
           of how long a mark lives, which is what the state layer needs, and
           it is UNMEASURED - a frame-time comparison against an empty registry
           is the thing that would settle it. */""",
    '6 the cost bound stands on its own')

# ── 4. where each primitive actually arrives ────────────────────────
sub(u"""  _beam:function(el,col,ms){
    /* P883: z-index 4, under the dice canvas at 41 - same story as _flash. */""",
    u"""  _beam:function(el,col,ms){
    /* P883: z-index 4, under the dice canvas at 41 - same story as _flash.
       P887: AND NOTHING ON A DIE REACHES IT TODAY. Resolved at runtime, the
       only play() site passing a die element is the enchant keep, and no
       enchant id resolves to PAY, FATE or ARM - the three families that call
       this. On a die _flash arrives via BREAK, _glow only through moment 2,
       and _beam through nothing at all. The painter is correct and worth
       having ready; it is simply not exercised, and P883's commit overstated
       the reach by saying otherwise. */""",
    '7 where the primitives actually arrive')

# ── 5. citations by name, not by number ─────────────────────────────
sub(u"""     `opacity` is read by D3X at 29629 as "hide this die". Invisible, and two
     ways harmful.""",
    u"""     `opacity` is read by D3X's frame pass as a visibility signal - a chip
     computed at or under .02 hides its die. Invisible, and two ways harmful.""",
    '8 the opacity citation')

sub(u"""  /* P881: NUDGE - kick's sibling. kick (29594) is a one-way displacement with""",
    u"""  /* P881: NUDGE - kick's sibling. kick, in the same settled branch, is a
     one-way displacement with""",
    '9 the kick citation')

sub(u"""      /* P884c: NOT window.G. G is a `let` (30882), so it is a global binding""",
    u"""      /* P884c: NOT window.G. G is a `let`, so it is a global binding""",
    '10 the let citation')

sub(u"""         same note is already at 31018, where the same mistake silently
         no-opped a whole migration.""",
    u"""         same note is already on _dropKeptToTray_OLD's guard, where the same
         mistake silently no-opped a whole migration.""",
    '11 the note citation')

# ── post-asserts, against code with comments stripped where relevant ─
if 'Snare does not call this' in s:
    sys.exit('the fourth stale comment survives (nothing written)')
if s.count("_landed:function(d,via){") != 1:
    sys.exit('the exit tag is not on the function (nothing written)')
if s.count("this._landed(d,'physPose')") != 1 or s.count("D3X._landed(d,'watchdog')") != 1:
    sys.exit('the two exits are not tagged exactly once each (nothing written)')
if s.count('_landedVia:{physPose:0,watchdog:0}') != 1:
    sys.exit('the counter is not declared exactly once (nothing written)')
# no bare four/five-digit line citations left in the comments this session wrote
for stale in ('29629', '29594', '30882', '31018'):
    if stale in s:
        sys.exit('the stale citation %s survives (nothing written)' % stale)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
