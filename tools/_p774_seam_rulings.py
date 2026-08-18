# -*- coding: utf-8 -*-
"""P774: the three bank-seam rulings land.

Denis ruled (2026-08-19):
1. GAIN_WHEN_AHEAD counts the incoming bank on BOTH seats - 'ahead' is
   evaluated on the result of the banking action, not a snapshot from
   before it. The rival's side already read it that way; the player's
   test gains the bank.
2. HALVE_FIRST_BANK gates on THE FIRST BANK specifically, both seats -
   the card's own text says 'the opponent's very first bank'. The
   rival-owned copy already latched G.npcCardState.firstBankDone; the
   player-owned copy gains the mirror latch (oppFirstBankDone, set where
   the rival's bank credits - the mirror of handleBank's 33608 latch)
   and gates on it instead of the once-per-match counter. The counter
   still increments (bookkeeping parity); the GATE is the flag.
3. CHALLENGE: gut-check confirmed missing-check-not-design - the two
   arm sites' turn gates are equivalent (turnNum>=3 vs oppTurnCount>=2,
   per the init offset P768 documented), so the only real gap was the
   threshold read. The player-owned arm now requires the rival to be
   scoring at challenge scale (G.oPts>=threshold), the exact mirror of
   the rival's pPts>=threshold.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new)
        edits.append(label)
        return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    hits = re.findall(pat, s)
    if len(hits) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(hits), label))
    s = re.sub(pat, lambda m: new, s, count=1)
    edits.append(label)


# ── 1. gain_when_ahead: the player's test counts the incoming bank ──
sub("""    if(eff&&eff.mechanic==='gain_when_ahead'&&G.pPts>G.oPts){""",
    """    /* P774 RULING: 'ahead' counts the incoming bank on both seats -
       evaluated on the result of the banking action, matching the
       rival's reading at _oppFxOwnB. */
    if(eff&&eff.mechanic==='gain_when_ahead'&&(G.pPts+total)>G.oPts){""",
    'gain_when_ahead bank-inclusive')

# ── 2. halve_first_bank: the rival's FIRST bank, latched like the player's ──
sub("""        /* Halve first bank (fine_print) */
        if(eff.type==='on_player_bank'&&eff.mechanic==='halve_first_bank'&&(G.npcCardState.playerOnce[cid]||0)<_useCap(cid)&&pts>0){
          G.npcCardState.playerOnce[cid]=(G.npcCardState.playerOnce[cid]||0)+1;
          var half=pts-BANK_FX.halve_first_bank(pts,eff);pts-=half;
          triggerCard(cid,npc.name+' −'+half,true);
        }""",
    """        /* Halve first bank (fine_print). P774 RULING: 'the opponent's
           VERY FIRST bank' - the card's own text - so the gate is the
           first-bank latch (the mirror of firstBankDone), not the
           once-per-match counter. The counter still increments for
           bookkeeping parity; the flag decides. */
        if(eff.type==='on_player_bank'&&eff.mechanic==='halve_first_bank'&&!G.npcCardState.oppFirstBankDone&&pts>0){
          G.npcCardState.playerOnce[cid]=(G.npcCardState.playerOnce[cid]||0)+1;
          var half=pts-BANK_FX.halve_first_bank(pts,eff);pts-=half;
          triggerCard(cid,npc.name+' −'+half,true);
        }""",
    'halve gates on the first bank')

# the latch: the rival's bank credits -> their first bank is done. The
# mirror of handleBank's unconditional latch after its rider loop.
sub("""        pts+=famFire('bankBonus',{actor:'o',amt:pts,total:pts});
        G.oPts+=pts;_npcActuallyBanked=true;""",
    """        pts+=famFire('bankBonus',{actor:'o',amt:pts,total:pts});
        G.oPts+=pts;_npcActuallyBanked=true;
        G.npcCardState.oppFirstBankDone=true;/* P774: the mirror of firstBankDone */""",
    'the rival latch')

# ── 3. challenge: the player-owned arm reads the threshold ──
sub("""        if(eff.type==='once'&&eff.mechanic==='challenge'&&(G.npcCardState.playerOnce[cid]||0)<_useCap(cid)&&G.oppTurnCount>=2&&pts>0&&Math.random()<0.4){""",
    """        /* P774 RULING (gut-check confirmed missing-check-not-design):
           the arm requires the rival to be scoring at challenge scale -
           the exact mirror of the rival-owned arm's pPts>=threshold.
           The turn gates were already equivalent (init offset, P768). */
        if(eff.type==='once'&&eff.mechanic==='challenge'&&(G.npcCardState.playerOnce[cid]||0)<_useCap(cid)&&G.oppTurnCount>=2&&pts>0&&G.oPts>=(eff.threshold||0)&&Math.random()<0.4){""",
    'challenge arm reads the threshold')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
