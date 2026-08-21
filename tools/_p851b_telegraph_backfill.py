# -*- coding: utf-8 -*-
"""P851b: the early-night telegraph cap stops costing a card.

P851 raised the patron draw to 3, but nights 2-4 measured 1.9-2.6, not
3: the night<5 rule ("at most ONE active before night 5") DROPS every
active past the first, so a hand that happened to draw two actives
shipped one card short.

The rule's intent is "an early player should not face two actives at
once", not "an early patron holds fewer cards". So the excess active is
now REPLACED with a passive from the same usable pool rather than
deleted - the telegraph holds and the count holds with it. Only if no
passive is left does the hand shrink.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

old = """  if(night<5){/* telegraph rule sibling: at most ONE active before night 5 */
    var _na=0;
    _gp.fcards=fc.filter(function(c){var cd=famDef(c.id);
      if(cd&&cd.kind==='active'){_na++;return _na<=1;}return true;});
  }"""
new = """  if(night<5){/* telegraph rule sibling: at most ONE active before night 5 */
    /* P851b: SWAP, DON'T DROP. This used to filter the excess actives
       out, which quietly cost the patron a card whenever it drew two -
       measured at 1.9-2.6 cards on nights 2-4 against a target of 3.
       The rule means "not two actives at once", not "a smaller hand",
       so a surplus active is replaced by a passive from the same
       usable pool and only an empty pool shrinks the hand. */
    var _na=0,_swap=[];
    _gp.fcards=fc.filter(function(c){var cd=famDef(c.id);
      if(cd&&cd.kind==='active'){_na++;if(_na>1){_swap.push(c);return false;}}
      return true;});
    if(_swap.length){
      var _held={};_gp.fcards.forEach(function(c){_held[c.id]=1;});
      var _pass=FAM_CARDS.filter(function(d){
        return _famDraftable(d)&&_npcUsable(d)&&d.kind!=='active'&&!_held[d.id];});
      _swap.forEach(function(c){
        if(!_pass.length)return;
        var p=_pass.splice(Math.floor(Math.random()*_pass.length),1)[0];
        _gp.fcards.push({id:p.id,tier:c.tier});
      });
    }
  }"""

if s.count(old) == 1:
    s = s.replace(old, new)
else:
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d (nothing written)' % len(ms))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]

if 'SWAP, DON' not in s:
    sys.exit('KEEPER MISSING (nothing written)')
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: the telegraph cap swaps instead of dropping')
