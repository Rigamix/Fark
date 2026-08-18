# -*- coding: utf-8 -*-
"""P760: NPC phase 1 - the EV floor, the bank plan, and the release
block's deletion. (docs/NPC_AI_BRIEF.md section 5, phase 1.)

Three changes, each killing one of Denis's sightings by construction:

1. THE EV FLOOR. Every candidate keep is priced once in _oppChooseFrom -
   pts + survival x expected gain off the measured _npcEvTable - and no
   persona may pick a keep that gives up more than NPC_MAX_GIVE (500)
   against the best candidate. aggro keeps its identity (the research
   validates minimal keeps: "1 2 2 2 5 4 - keep the 1, roll five" beats
   holding the triple) but can no longer keep a bare 1 off a straight,
   because that gives up ~1400. The straights persona's signature
   run-gamble (~450) survives under the cap, which is what the cap is
   FOR: in-character mistakes bounded, catastrophes impossible.

2. THE BANK PLAN. Keep-then-decide was the structural bug behind
   "banked a 1 with a 1 and 5 on the table": the style keep is chosen
   first and the bank verdict is powerless to revise it. Now
   _oppChooseFrom asks oppShouldBank FIRST, against the max-pts keep -
   and if the answer is bank, the max-pts keep IS the pick ("when you
   have decided to stop, take everything scoring" - the coupling every
   Farkle solver treats as one decision). The verdict is stashed with
   the base it was computed on; the bank site reuses it only when
   nothing changed the numbers in between, else calls fresh. The
   residual corner (a card modifier changes the total AND the fresh
   call's random branch flips to bank after a persona keep) is bounded
   by the floor at 500 give-up - annoying at worst, never idiotic.

3. THE RELEASE BLOCK IS DELETED. It was a second chooser re-litigating
   the first with its own randomness, it broke straights (its comment
   promised "not part of a triple/straight" while the code checked only
   triples), and it refunded flat 100/50 against dice that scored as
   combo parts - the arithmetic drift behind "ignored a straight and
   banked a single 5". Its job - keep fewer, reroll more - is what the
   EV pricing does soundly.

Found while building the verification: the ?sim=1 harness never runs
the persona chooser at all (simTurn always keeps the maximal set), so
the sim was structurally blind to every one of these bugs. The probe
drives the LIVE functions instead.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    c = s.count(old)
    if c != 1:
        o2 = old.replace('\n', '\r\n')
        if s.count(o2) == 1:
            old, new = o2, new.replace('\n', '\r\n')
        else:
            sys.exit('ANCHOR x%d for %s (nothing written)' % (c, label))
    s = s.replace(old, new)
    edits.append(label)


# ── 1+2. the floor and the plan, in _oppChooseFrom ──
sub("""function _oppChooseFrom(freeD,total,bank){
  if(!freeD||!freeD.length)return null;
  if(!total||total<=0)return null;/* bust: there is nothing to keep */
  var cands;
  try{ cands=_legalKeeps(freeD,'o',bank||0); }catch(e){ return null; }
  if(!cands||!cands.length)return null;
  var pick;
  try{ pick=_npcChooseKeep(cands,(typeof G!=='undefined'&&G)?G.rung:null); }catch(e){ return null; }
  return (pick&&pick.sel&&pick.sel.length)?pick:null;
}""",
    """/* P760: the most a persona may give up against the best candidate, in
   EV. Wide enough for every signature move (the straights persona's
   run-gamble costs ~450; aggro's minimal keeps usually 200-400), far
   below any catastrophe (a discarded straight is 1400+). One number,
   sim-tunable. */
var NPC_MAX_GIVE=500;
function _oppChooseFrom(freeD,total,bank){
  if(typeof G!=='undefined'&&G)G._oPlannedBank=null;/* P760: never stale */
  if(!freeD||!freeD.length)return null;
  if(!total||total<=0)return null;/* bust: there is nothing to keep */
  var cands;
  try{ cands=_legalKeeps(freeD,'o',bank||0); }catch(e){ return null; }
  if(!cands||!cands.length)return null;
  /* P760: PRICE EVERY CANDIDATE ONCE - pts + survival x expected gain,
     off the same measured table combo already used. Hot dice (left 0)
     prices the hand a sweep actually deals. */
  try{
    var _evT=_npcEvTable((G&&G.matchOppDice)||(G&&G.oppDice||[]).map(function(d){return d.mat;}));
    var _bestEV=-Infinity;
    cands.forEach(function(k){
      var _L=(k.left===0)?_oHandAfterSweep():k.left;
      k.ev=k.pts+((_L>=1&&_L<=6)?(1-(_evT.bust[_L]||0))*(_evT.gain[_L]||0):0);
      if(k.ev>_bestEV)_bestEV=k.ev;
    });
    /* P760: THE BANK PLAN. Keep and bank are ONE decision (every Farkle
       solver couples them): ask the bank question FIRST, against the
       max-pts keep - and if the answer is bank, take everything
       scoring. The verdict is stashed with the base it priced, so the
       bank site reuses it rather than re-rolling its dice. */
    if(typeof oppShouldBank==='function'&&G&&G.rung){
      var _c0=cands[0];/* _legalKeeps sorts by pts desc */
      var _l0=(_c0.left===0)?_oHandAfterSweep():_c0.left;
      var _plan=false;
      try{_plan=oppShouldBank(G.rung,(bank||0)+_c0.pts,_l0,G.oPts,G.pPts,G.target);}catch(e){}
      if(_plan){
        G._oPlannedBank={verdict:true,base:(bank||0)+_c0.pts};
        return _c0;
      }
    }
    /* P760: THE FLOOR. Personas choose freely among candidates within
       NPC_MAX_GIVE of the best - style decides WHICH good option, never
       whether to take a bad one. */
    var _sane=cands.filter(function(k){return k.ev>=_bestEV-NPC_MAX_GIVE;});
    if(_sane.length)cands=_sane;
  }catch(e){}
  var pick;
  try{ pick=_npcChooseKeep(cands,(typeof G!=='undefined'&&G)?G.rung:null); }catch(e){ return null; }
  return (pick&&pick.sel&&pick.sel.length)?pick:null;
}""",
    'EV floor + bank plan')

# ── 2b. the bank site consumes the plan ──
sub("""      const bank=oppShouldBank(G.rung,oppBank,left,G.oPts,G.pPts,G.target);""",
    """      /* P760: the plan made at keep time is the decision - reused only
         when nothing (Quick Hands, snare, anchor, triple hunter...)
         changed the numbers it priced; else decided fresh. */
      var _pl=G._oPlannedBank;G._oPlannedBank=null;
      const bank=(_pl&&_pl.verdict===true&&_pl.base===oppBank)
        ?true
        :oppShouldBank(G.rung,oppBank,left,G.oPts,G.pPts,G.target);""",
    'bank site consumes the plan')

# ── 3. the release block goes ──
START = "      /* ── NPC strategic dice keeping ──"
END = "      /* Slippery Table: 25% chance one kept die slips back */"
i = s.find(START)
j = s.find(END)
if i < 0 or j < 0 or j <= i:
    sys.exit('release block markers not found (nothing written)')
s = s[:i] + (
    "      /* P760: the 'strategic dice keeping' release block is DELETED.\n"
    "         It was a second chooser re-litigating the persona's pick with\n"
    "         its own randomness; it broke straights (its comment promised\n"
    "         'not part of a triple/straight' while the code checked only\n"
    "         triples) and refunded flat 100/50 against dice that had scored\n"
    "         as combo parts, drifting oppBank. Its job - keep fewer, reroll\n"
    "         more - is priced soundly by the EV floor in _oppChooseFrom. */\n"
) + s[j:]
edits.append('release block deleted')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
