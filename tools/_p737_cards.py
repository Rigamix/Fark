# -*- coding: utf-8 -*-
"""P737: honeytrap picks YOUR pair, and a card that cannot be played
says why instead of firing and apologising.

Denis, three reports:
- 'honeytrap says NOT NOW when I should be able to' - canUse counted
  only COMMITTED dice (k.vals), so a visible pair the player had just
  selected did not exist as far as the card was concerned.
- 'I kept two 5s, rerolled, selected two 4s, and it said the next roll
  pulls a 5' - use() walked Object.keys(vals) and took the LAST match.
  Numeric-ish keys enumerate in ascending order, so it always chose the
  HIGHEST pair on the table, never the one the player just made.
- 'when I move a card past the threshold but the game knows I cannot use
  it, grey it out and show me the text that explains why' - the drag
  armed regardless, cast on release, and the effect apologised with a
  bare NOT NOW afterwards.

The pair is now chosen by RECENCY: the live selection first (that is
what the player is pointing at), then the most recent kept group. The
drag arms only when the card can actually play; when it cannot, the card
greys and a one-line reason sits above it, and releasing does nothing at
all - no cast, no toast.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label, count=1):
    global s, n
    c = s.count(old)
    if c != count and '\n' in old:
        old2 = old.replace('\n', '\r\n')
        if s.count(old2) == count:
            old, c = old2, count
            new = new.replace('\n', '\r\n')
    if c != count:
        sys.exit('ANCHOR x%d (need %d) for %s' % (c, count, label))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# 1) honeytrap: the player's own pair, live selection included
sub(u"""CFX.honeytrap={
  canUse:function(){
    if(!G||G.phase==='opp')return false;
    var vals={};var ok=false;
    (G.kept||[]).forEach(function(k){(k.vals||[]).forEach(function(v){vals[v]=(vals[v]||0)+1;if(vals[v]>=2)ok=true;});});
    return ok;
  },
  use:function(inst){
    var vals={},pairVal=0;
    (G.kept||[]).forEach(function(k){(k.vals||[]).forEach(function(v){vals[v]=(vals[v]||0)+1;});});
    Object.keys(vals).forEach(function(v){if(vals[v]>=2)pairVal=Number(v);});
    if(!pairVal)return false;""",
    u"""/* P737: THE PAIR THE PLAYER MEANS. Two bugs lived here: only COMMITTED
   dice counted (so a pair you had just selected did not exist), and the
   winner was Object.keys' last match - ascending numeric order, i.e.
   always the HIGHEST pair on the table, never the one you just made.
   Recency decides now: the live selection first, then the most recent
   kept group, then anything else that pairs. */
function _honeyPairs(){
  var out=[];
  try{
    var sel=(G.pool||[]).filter(function(d){return d.sel&&!d.committed;});
    var sv={};sel.forEach(function(d){sv[d.val]=(sv[d.val]||0)+1;});
    Object.keys(sv).forEach(function(v){if(sv[v]>=2)out.push(Number(v));});
    for(var i=(G.kept||[]).length-1;i>=0;i--){
      var kv={};((G.kept[i]||{}).vals||[]).forEach(function(v){kv[v]=(kv[v]||0)+1;});
      Object.keys(kv).forEach(function(v){if(kv[v]>=2&&out.indexOf(Number(v))<0)out.push(Number(v));});
    }
    /* last resort: a pair spread across groups */
    var all={};
    (G.kept||[]).forEach(function(k){(k.vals||[]).forEach(function(v){all[v]=(all[v]||0)+1;});});
    Object.keys(all).forEach(function(v){if(all[v]>=2&&out.indexOf(Number(v))<0)out.push(Number(v));});
  }catch(e){}
  return out;
}
CFX.honeytrap={
  canUse:function(){
    if(!G||G.phase==='opp')return false;
    return _honeyPairs().length>0;
  },
  use:function(inst){
    var pairVal=_honeyPairs()[0]||0;
    if(!pairVal)return false;""",
    'honeytrap pairs by recency')

# 2) why a card cannot be played, in words
sub(u"""function _famCanPlay(i){""",
    u"""/* P737: WHY NOT, in one line. A card that cannot fire should say so
   BEFORE the player commits to the gesture, not apologise after. */
function _famWhyNot(inst){
  try{
    if(!inst)return '';
    var d=famDef(inst.id),fx=CFX[inst.id];
    if(!d)return '';
    if(d.kind!=='active')return 'PASSIVE — IT WORKS ON ITS OWN';
    if(!fx||!fx.use)return 'NOT WIRED UP YET';
    if(inst.charges<=0)return 'SPENT FOR THIS MATCH';
    if(G&&G.phase==='opp')return 'WAIT FOR YOUR TURN';
    if(fx.canUse&&!fx.canUse(inst)){
      var why={
        honeytrap:'KEEP OR SELECT A PAIR FIRST',
        preserve:'KEEP A 1 OR A 5 FIRST',
        transmute:'ROLL FIRST — IT NEEDS A DIE TO CHANGE',
        powder_keg:'ROLL FIRST',
        sacrifice:'ROLL FIRST — IT NEEDS A DIE TO SPEND',
        stargazer:'ROLL FIRST',
        sleight:'ROLL FIRST',
        tamper:'THE RIVAL HAS NOTHING TO TAMPER WITH YET',
        ill_omen:'NOT THIS MOMENT — IT FIRES ON THEIR TURN'
      }[inst.id];
      return why||'NOT RIGHT NOW';
    }
  }catch(e){}
  return '';
}
function _famCanPlay(i){""",
    '_famWhyNot')

# 3) the drag: arm only when playable; grey + reason when not
sub(u"""    var armed=(_famDrag.cy0+dy)<_famDrag.line;
    if(armed!==_famDrag.armed){_famDrag.armed=armed;el.classList.toggle('armed',armed);}""",
    u"""    var past=(_famDrag.cy0+dy)<_famDrag.line;
    /* P737: past the line is not the same as PLAYABLE. A card that
       cannot fire greys and says why, up where the player is looking -
       and releasing it does nothing at all. */
    var why=_famWhyNot(G&&G.pF&&G.pF[_famDrag.i]);
    var armed=past&&!why;
    if(armed!==_famDrag.armed){_famDrag.armed=armed;el.classList.toggle('armed',armed);}
    var blocked=past&&!!why;
    if(blocked!==_famDrag.blocked){
      _famDrag.blocked=blocked;
      el.classList.toggle('fcv-blocked',blocked);
      var lbl=document.getElementById('famWhyNot');
      if(blocked){
        if(!lbl){lbl=document.createElement('div');lbl.id='famWhyNot';
          (document.getElementById('screen-match')||document.body).appendChild(lbl);}
        lbl.textContent=why;
        var r2=el.getBoundingClientRect(),sr=(document.getElementById('screen-match')||document.body).getBoundingClientRect();
        lbl.style.top=(r2.top-sr.top-30)+'px';
        lbl.classList.add('on');
      }else if(lbl)lbl.classList.remove('on');
    }""",
    'drag arms only when playable')

sub(u"""  function end(){
    if(!_famDrag||_famDrag.el!==el)return;
    var live=_famDrag.live,idx=_famDrag.i;_famDrag=null;
    var armed=el.classList.contains('armed');
    el.classList.remove('fcv-drag','armed');
    el.style.transform='';
    if(!live)return;/* a tap - famCardTap's onclick still has it */
    if(!armed)return;/* released short of the line - it just goes home */""",
    u"""  function end(){
    if(!_famDrag||_famDrag.el!==el)return;
    var live=_famDrag.live,idx=_famDrag.i;_famDrag=null;
    var armed=el.classList.contains('armed');
    el.classList.remove('fcv-drag','armed','fcv-blocked');
    el.style.transform='';
    /* P737: the reason clears with the gesture */
    try{var _l=document.getElementById('famWhyNot');
      if(_l){_l.classList.remove('on');setTimeout(function(){if(_l&&!_l.classList.contains('on'))_l.textContent='';},400);}}catch(e){}
    if(!live)return;/* a tap - famCardTap's onclick still has it */
    if(!armed)return;/* released short of the line, or blocked - nothing
      fires and nothing apologises: the reason was already on screen */""",
    'end clears the reason')

# 4) the look of blocked + the reason line
sub(u"#famRowP .fcv.fcv-drag .fcvIn{animation:none}",
    u"#famRowP .fcv.fcv-drag .fcvIn{animation:none}\n"
    u"/* P737: dragged past the line but unplayable - grey, and the reason\n"
    u"   sits above the card where the eye already is */\n"
    u"#famRowP .fcv.fcv-blocked{filter:saturate(.18) brightness(.5)\n"
    u"  drop-shadow(0 0.25cqw 0.3cqw rgba(10,6,2,.5))}\n"
    u"#famWhyNot{position:absolute;left:0;right:0;text-align:center;z-index:9600;\n"
    u"  font-family:'JMH Beda',serif;font-size:3.6cqw;letter-spacing:.04em;\n"
    u"  color:#e8c9a0;text-shadow:0 0.2cqw 0.4cqw rgba(8,4,2,.9);\n"
    u"  pointer-events:none;opacity:0;transition:opacity .16s ease}\n"
    u"#famWhyNot.on{opacity:1}",
    'blocked look + reason line')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
