# -*- coding: utf-8 -*-
"""P820: the boss win shows the card draft, like a regular win (Denis).

Recon: boss and patron wins share one end screen, one .res-card, and
the draft renderer has nothing patron-scoped in it - famOffer reads
only run state and every draft outcome converges on _famEndReady. The
boss branch simply diverged into the SPOILS greybox and stopped.

The seam: famSpoilsPick's tail. After the spoils land, the same
injection block the patron branch runs (offer html + the P644
.fo-skip hoist + drag + focus prep) renders the draft, with the
spoils message as a header line. SKIP pays honestly: the boss payout
now stashes S.run._lastWinGold=_bossGold (it used to be written only
by patron wins, so a boss-win SKIP would have paid 75% of the
PREVIOUS patron purse).

Ambrose (night 8) keeps his renown card - no draft on the final
screen, noted in OPEN.md. Tier note (also OPEN.md): _settleEndRoute
has already advanced S.run.tier when the delayed block runs, so a
boss-win draft rolls at the NEW night's odds - the reward is for the
night you just entered.
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


# 1) the boss purse feeds the decline gold
sub("""    if(_bossGold){
      _getS();S.run.gold=(S.run.gold||0)+_bossGold;save();""",
    """    if(_bossGold){
      _getS();S.run.gold=(S.run.gold||0)+_bossGold;
      S.run._lastWinGold=_bossGold;/* P820: SKIP on the boss draft pays 75% of THIS purse, not the previous patron's */
      save();""",
    'boss purse stashed for decline gold')

# 2) the draft follows the spoils
sub("""  window._spoils=null;save();
  var rc=document.querySelector('#end-ov .res-card');
  if(rc)rc.innerHTML='<div style="font-family:monospace;color:#dc5;padding:30px 10px;text-align:center">'+msg+'</div>';
  _famEndReady();
}""",
    """  window._spoils=null;save();
  var rc=document.querySelector('#end-ov .res-card');
  /* P820: THE DRAFT FOLLOWS THE SPOILS (Denis: "the boss win screen must
     show the card draft like a regular win"). Same offer, same P644 skip
     hoist, same funnel - every draft outcome ends in _famEndReady, which
     re-shows #end-btns. The spoils message rides as a header line. */
  try{
    _famOffer=famOffer(false);
    var _dg=_famDeclineGold();
    if(rc){rc.innerHTML='<div style="font-family:monospace;color:#dc5;padding:6px 10px 2px;text-align:center;font-size:12px;letter-spacing:1px">'+msg+'</div>'
      +famOfferHtml(_famOffer,'famDraftPick',_dg);rc.classList.add('show');}
    var _ovSk=document.getElementById('end-ov');
    _ovSk.querySelectorAll(':scope>.fo-skip').forEach(function(e){e.remove();});
    var _sk=rc&&rc.querySelector('.fo-skip');
    if(_sk&&_ovSk)_ovSk.appendChild(_sk);
    try{_foInstallDrag();}catch(e){}
    try{_foFocusPrep();}catch(e){}
    var _eb=document.getElementById('end-btns');if(_eb)_eb.style.display='none';
  }catch(e){
    if(rc)rc.innerHTML='<div style="font-family:monospace;color:#dc5;padding:30px 10px;text-align:center">'+msg+'</div>';
    _famEndReady();
  }
}""",
    'the draft follows the spoils')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
