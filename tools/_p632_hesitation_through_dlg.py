# -*- coding: utf-8 -*-
"""P632: the rival's hesitation goes in the dialogue box, and through the pacing
that already exists. Denis's playthrough notes 5 and 6, which are one bug.

  5. "NPC dialogue is shown two different ways, broken: you have some lines
      appearing in the parchment box, and then the new lines appear as text the
      same way the 'Patron is rolling' is. Everything should be displayed in the
      dialogue box."
  6. "not every single action from the npc needs a dialogue for it. You need to
      create a system that creates space between lines... It's fine to have
      silences sometimes."

BOTH ARE MY P628. It called setStatusMsg - the "PATRON IS ROLLING…" channel -
and in doing so skipped DLG.trigger, which is where every other beat in the game
gets its surface AND its spacing.

AND THE BAND IT USED TO JUSTIFY ITSELF DOES NOT MEASURE WHAT IT CLAIMS.
P628 argued agg near 0.5 means "the decision was a coin flip". Measured over a
real match (tools/apv_dlg_hesitate_gate.js): agg was 0.53 on all seven calls -
the SAME VALUE EVERY TIME. Reading oppShouldBank explains it: agg starts as
rung.agg and is only moved by the opponent's persona, the handicap, and two
gap-dependent branches most matches never reach. For an ordinary patron it is
CONSTANT for the whole match.

So the band never selected close decisions. It selected OPPONENTS. A patron
whose agg sits inside 0.40-0.65 hesitated on EVERY SINGLE ROLL - seven lines in
a turn and a half, straight into the status channel - and a patron outside it
never hesitated at all. A separate whole-match run measured exactly that other
half: 24 calls, 0 lines (tools/apv_dlg_channels.js). Two runs, opposite results,
one cause. That is note 6 word for word.

THE FIX IS TO DELETE, NOT TO ADD. DLG.trigger already carries everything note 6
asks for and its own comment says so - "spaces lines out so they don't read as
rapid-fire chatter":
  * this.prob[cat]              a per-category chance, so not every event speaks
  * now < this.busyUntil+this.gap   nothing lands while a line is still up
  * a _priority whitelist       for the few beats allowed to interrupt
and DLG.show is what fills the parchment box. Routing the beat through it fixes
note 5 and note 6 at the same time, because they were the same shortcut.

WHAT GOES, AND WHY EACH IS SAFE:
  _dlgHesitate      its whole body was the band plus a _dlgEvent call, and
                    _DLG_MOMENT already performs exactly that _dlgEvent call for
                    every other moment. Keeping it would be a second way to do
                    one thing.
  _HESITATE_LO/HI   measured above; it is a per-opponent filter wearing the name
                    of a per-decision one. A knob that does something other than
                    what it says is worse than no knob.
  G._oppAgg         its only reader was _dlgHesitate. It was also WRONG on three
                    paths: oppShouldBank returns at oppBank>=3000, >=2000 and
                    >=1500 BEFORE the stash, so those decisions were read
                    against the previous decision's value. Removing it restores
                    the purity the P628 note claimed for the function.

WHAT ARRIVES IS TWO TABLE ENTRIES AND A TRIGGER CALL. No new state, no new
timer, no new pacing system, and the 36 lines P628 wrote are untouched and now
reachable for every opponent instead of roughly half of them.

THE TUNING KNOB IS NOW DLG.prob, where every other category's already is. 0.3
is deliberately low: the rival's turn has three or four decisions, so anything
higher and the pause stops being a pause. It also has to share the spacing gate
with OPP_BUST and OPP_BIG_BANK, which are the payoff beats - a hesitation that
lands too often will occasionally swallow one. That is Denis's dial to turn.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:120]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ── 1. the helper and its band come out ──────────────────────────────────
sub(u"/* P628: DOES THIS DECISION DESERVE A PAUSE?\n"
    u"   Only when it was genuinely close. `agg` is what oppShouldBank converges on\n"
    u"   and its last word is `Math.random() > agg`, so near 0.5 the same board goes\n"
    u"   either way and at 0.15 or 0.9 it does not. The band is taken from the two\n"
    u"   exits that gate on agg, not chosen for feel.\n"
    u"   Returns null for a blowout, and null is the caller's cue to say nothing -\n"
    u"   a hesitation on an obvious decision reads as noise, not character. */\n"
    u"var _HESITATE_LO=0.40,_HESITATE_HI=0.65;\n"
    u"function _dlgHesitate(willBank){\n"
    u"  try{\n"
    u"    var a=(typeof G!=='undefined'&&G)?G._oppAgg:undefined;\n"
    u"    if(typeof a!=='number')return null;\n"
    u"    if(a<_HESITATE_LO||a>_HESITATE_HI)return null;\n"
    u"    /* the two moments fall straight out of the decision itself */\n"
    u"    return _dlgEvent(willBank?'banksafe':'push');\n"
    u"  }catch(e){return null;}\n"
    u"}\n"
    u"/* the four DLG events these answer, and which side each belongs to */\n"
    u"var _DLG_MOMENT={OPP_BUST:'bust',PLAYER_BUST:'yourBust',\n"
    u"                 OPP_BIG_BANK:'bank',BIG_BANK:'yourBank'};",
    u"/* P632: THE HESITATION BEAT IS JUST ANOTHER MOMENT NOW.\n"
    u"   P628 gave it a private helper with an `agg` band, on the reasoning that agg\n"
    u"   near 0.5 meant the rival's decision was a coin flip. Measured over a real\n"
    u"   match, agg was 0.53 on all seven calls - the same value every time, because\n"
    u"   it starts as rung.agg and for an ordinary patron nothing moves it. So the\n"
    u"   band selected OPPONENTS, not decisions: in-band patrons hesitated on every\n"
    u"   single roll, out-of-band ones never (24 calls, 0 lines, in a second run).\n"
    u"   Both the helper and the band are gone. These two are ordinary _DLG_MOMENT\n"
    u"   entries, so they reach the same _dlgEvent every other beat uses and inherit\n"
    u"   DLG.trigger's probability and spacing - which is where a pause belongs, and\n"
    u"   was the whole of what the band was pretending to do. */\n"
    u"/* the moments these answer, and which side each belongs to */\n"
    u"var _DLG_MOMENT={OPP_BUST:'bust',PLAYER_BUST:'yourBust',\n"
    u"                 OPP_BIG_BANK:'bank',BIG_BANK:'yourBank',\n"
    u"                 OPP_HESITATE_PUSH:'push',OPP_HESITATE_BANK:'banksafe'};",
    'P632 drop _dlgHesitate + the band, add the two moments')

# ── 2. oppShouldBank goes back to being pure ─────────────────────────────
sub(u"  /* P628: agg is FINAL here - nothing below mutates it, the branches only\n"
    u"     read it. Stashed so the call site can tell a coin-flip from a foregone\n"
    u"     conclusion without this function knowing anything about dialogue. Same\n"
    u"     pattern as G._lastBankAmount: expose a value computed mid-decision\n"
    u"     rather than reshape the return. */\n"
    u"  try{if(typeof G!=='undefined'&&G)G._oppAgg=agg;}catch(e){}\n",
    u"  /* P632: P628's G._oppAgg stash removed. Its only reader has gone, and it\n"
    u"     was never sound anyway - the three huge-bank returns above exit before\n"
    u"     this line, so those decisions were read against the PREVIOUS one's\n"
    u"     value. This function knows nothing about dialogue again. */\n",
    'P632 remove the agg stash')

# ── 3. the call site: through DLG, like every other beat ─────────────────
sub(u"      /* P628: the hesitation beat goes in the pause that was ALREADY here.\n"
    u"         _oppDelay(1900) exists so the rival's decision does not land\n"
    u"         instantly; on a close call it now has something in it. No new timing,\n"
    u"         and the delay is unchanged whether or not a line comes back.\n"
    u"         Here and not inside oppShouldBank, which stays pure - and this is the\n"
    u"         in-match call, so FSIM's own caller never speaks. */\n"
    u"      try{var _hes=_dlgHesitate(bank);if(_hes)setStatusMsg(_hes,'');}catch(e){}\n",
    u"      /* P632: the hesitation beat goes in the pause that was ALREADY here -\n"
    u"         _oppDelay(1900) exists so the rival's decision does not land instantly\n"
    u"         - but it goes through DLG like every other beat, so it lands in the\n"
    u"         parchment box and obeys the same probability and spacing. P628 called\n"
    u"         setStatusMsg here, which put dialogue in the 'PATRON IS ROLLING…'\n"
    u"         channel AND skipped the pacing gate, so a mid-aggression rival\n"
    u"         hesitated on every roll. Denis's notes 5 and 6, one line apart.\n"
    u"         Still the in-match call, so FSIM's own caller never speaks. */\n"
    u"      try{if(window.DLG)DLG.trigger(bank?'OPP_HESITATE_BANK':'OPP_HESITATE_PUSH');}catch(e){}\n",
    'P632 route the hesitation through DLG.trigger')

# ── 4. the knob, beside every other category's ───────────────────────────
sub(u"PLAYER_CARD_REACT:1,TELL:1},",
    u"PLAYER_CARD_REACT:1,TELL:1,"
    u"/* P632: low on purpose. A rival turn holds three or four decisions, so a\n"
    u"       high number stops the pause reading as a pause; and these share the\n"
    u"       spacing gate with OPP_BUST and OPP_BIG_BANK, which are the payoff\n"
    u"       beats. This is the dial - there is no other. */"
    u"OPP_HESITATE_PUSH:.3,OPP_HESITATE_BANK:.3},",
    'P632 the two probabilities')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
