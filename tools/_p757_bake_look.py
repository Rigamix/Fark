# -*- coding: utf-8 -*-
"""P757: the gap was the card's own dark drop-shadow; Denis's numbers
become the game's authored look.

THE GAP. With the punch-out gone, the dark ring between card and glow
could only be paint from ABOVE the halo canvas - and it is: the card
element's own CSS drop-shadows (the resting contact shadow), drawn by
the card, over the glow. While a halo is live the glow IS the card's
grounding, so the drag, cant and armed rules drop the dark shadows and
keep only their brightness/grey terms. (On iOS these shadows were
clipped dead anyway - this also makes desktop and phone agree.)

THE LOOK, BAKED AS AUTHORED VALUES - not a localStorage record:
  key light   0.524 -> 0.998        ambient 0.72 -> 0.533
  bounce      0.12  -> 0.296  (his export carried THREE stacked warm
              fills - the game's 0.163, P754's fkBounce 0.061 and the
              lab's own 0.072; same colour, same direction, so they sum
              linearly into one clean light. One rig, no stacking.)
  SIDEDIM_MAX 0.82 -> 0.86
  shadow mask SIDEDIM_GRAD:0.14 (vertical only) -> SIDEDIM_MASK
              {axis:'x', amt:0.3} - the axis+sign gradient is the exact
              math of the lab override he tuned, baked into _dimMap;
              cache key carries axis+amt so lab changes still rebake.
  vignette 72 / size 48 / centre 0 / shadow depth normal - the DEFAULT
              look record: _applyLabLook now falls back to these when no
              lab save exists, so the phone and Pages get the approved
              room without any localStorage.
  GLOW - his numbers are already the shipped defaults (fb* are retired
              dials of the deleted fallback branch; ignored).
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


# ── 1. the dark drop-shadows leave while a halo is live ──
sub("""  filter:drop-shadow(0 0.9cqw 1.3cqw rgba(10,6,2,.5))
    brightness(calc(1.06 + 0.18*var(--arm,0)))}""",
    """  /* P757: NO dark drop-shadow here - the halo canvas under the card is
     the card's grounding now, and this shadow painted OVER it, which is
     the dark ring Denis circled. brightness alone still overrides the
     resting card's shadow pair, because a filter REPLACES the property. */
  filter:brightness(calc(1.06 + 0.18*var(--arm,0)))}""",
    'drag shadow gone')

sub("""  filter:saturate(calc(1 - 0.82*var(--arm,0))) brightness(calc(1 - 0.5*var(--arm,0)))
    drop-shadow(0 0.25cqw 0.3cqw rgba(10,6,2,.5))}""",
    """  filter:saturate(calc(1 - 0.82*var(--arm,0))) brightness(calc(1 - 0.5*var(--arm,0)))}/* P757: no dark ring over the halo */""",
    'cant shadow gone')

sub("""  scale:1.09;
  filter:drop-shadow(0 0.9cqw 1.3cqw rgba(10,6,2,.5))
  brightness(1.22)}/* P576: third of the three */""",
    """  scale:1.09;
  filter:brightness(1.22)}/* P576: third of the three; P757: the halo
  grounds an armed card - its dark shadow painted over the glow */""",
    'armed shadow gone')

# ── 2. the light rig takes his numbers as AUTHORED values ──
sub("""    /* P732: key 0.38 -> 0.524 and a warm bounce fill from below, per
       Denis's approved lab numbers. Ambient stays 0.72 (matched). */
    var key=new THREE.DirectionalLight(0xffffff,0.524);key.position.set(0,0.33,0.94);sc.add(key);
    sc.add(new THREE.AmbientLight(0xffffff,0.72));
    var bounce=new THREE.DirectionalLight(0xffe8c8,0.12);bounce.position.set(0,-1,0.6);sc.add(bounce);""",
    """    /* P732 set the first approved rig; P757 bakes the second: key 0.998,
       ambient 0.533, bounce 0.296. His export carried THREE stacked warm
       fills (the game's, P754's fkBounce, the lab's own) - same colour,
       same direction, so they sum linearly into this one light. Named,
       so the lab adopts it instead of adding another. */
    var key=new THREE.DirectionalLight(0xffffff,0.998);key.position.set(0,0.33,0.94);sc.add(key);
    sc.add(new THREE.AmbientLight(0xffffff,0.533));
    var bounce=new THREE.DirectionalLight(0xffe8c8,0.296);bounce.name='fkBounce';bounce.position.set(0,-1,0.6);sc.add(bounce);""",
    'light rig baked')

# ── 3. side shadow strength ──
sub("  SIDEDIM_MAX:0.82,/* P732: 0.5 -> 0.82, masked by SIDEDIM_GRAD */",
    "  SIDEDIM_MAX:0.86,/* P757: 0.82 -> 0.86, Denis's numbers; masked by SIDEDIM_MASK */",
    'side dim 0.86')

# ── 4. the mask gains its axis, exactly the lab override's math ──
sub("""  /* P732: the dim is STRONGER but fades ACROSS each face - Denis's final
     numbers went horizontal and subtler. GRAD is the fraction of the dim
     masked away at the right edge of each cell (all dice). */
  SIDEDIM_GRAD:0.14,""",
    """  /* P757: the mask carries Denis's approved axis and amount - the exact
     per-cell gradient the lab override bakes (axis picks the cell's UV
     direction, the sign flips which end holds full shadow), so what he
     tuned in the lab IS the shipped bake. */
  SIDEDIM_MASK:{axis:'x', amt:0.3},""",
    'mask config')

sub("""    /* P732: the dim fades toward each face's BASE (SIDEDIM_GRAD masks
       that fraction of it) - a per-cell vertical gradient of the multiply
       colour rather than one flat fill. The scoring cell is repainted
       bright below exactly as before, so top faces are untouched. */
    var _gd=this.SIDEDIM_GRAD||0;
    var _colAt=function(kk){return 'rgb('+fc.map(function(f){
      return Math.round(255*(1-(1-f)*kk));}).join(',')+')';};
    var _cw=w/3,_ch=h/2;
    for(var _cy=0;_cy<2;_cy++)for(var _cx2=0;_cx2<3;_cx2++){
      var _x0=_cx2*_cw,_y0=_cy*_ch;
      var _gr=cx.createLinearGradient(0,_y0,0,_y0+_ch);
      _gr.addColorStop(0,_colAt(kq));
      _gr.addColorStop(1,_colAt(kq*(1-_gd)));
      cx.fillStyle=_gr;cx.fillRect(_x0,_y0,_cw,_ch);
    }""",
    """    /* P732/P757: the dim fades ACROSS each cell along the mask's axis -
       the same math as the lab's override (sgn flips which end holds the
       full shadow), so the shipped bake and the tuning surface agree. */
    var _mk=this.SIDEDIM_MASK||{axis:'y',amt:0};
    var _gd=Math.abs(_mk.amt||0),_sgn=(_mk.amt||0)>0?1:-1;
    var _colAt=function(kk){return 'rgb('+fc.map(function(f){
      return Math.round(255*(1-(1-f)*kk));}).join(',')+')';};
    var _cw=w/3,_ch=h/2;
    for(var _cy=0;_cy<2;_cy++)for(var _cx2=0;_cx2<3;_cx2++){
      var _x0=_cx2*_cw,_y0=_cy*_ch;
      var _gr=(_mk.axis==='x')
        ?cx.createLinearGradient(_x0,0,_x0+_cw,0)
        :cx.createLinearGradient(0,_y0,0,_y0+_ch);
      _gr.addColorStop(_sgn>0?0:1,_colAt(kq));
      _gr.addColorStop(_sgn>0?1:0,_colAt(kq*(1-_gd)));
      cx.fillStyle=_gr;cx.fillRect(_x0,_y0,_cw,_ch);
    }""",
    'mask axis in the bake')

sub("""    var kq=Math.round(k*1000)/1000,key=v+'|'+kq;
    if(dm[key])return dm[key];
    var im=im""".replace('    var im=im', '    var im=tex.image;'),
    """    var _mkk=this.SIDEDIM_MASK||{};
    var kq=Math.round(k*1000)/1000,key=v+'|'+kq+'|'+(_mkk.axis||'')+(_mkk.amt||0);
    if(dm[key])return dm[key];
    var im=tex.image;""",
    'cache key carries the mask')

# ── 5. the default look record: vignette without any save ──
sub("""    var lk=null;try{lk=JSON.parse(localStorage.fkLabLook||'null');}catch(e){}
    if(!lk)return;
    var self=this;""",
    """    var lk=null;try{lk=JSON.parse(localStorage.fkLabLook||'null');}catch(e){}
    /* P757: no lab save means the APPROVED DEFAULTS, not nothing - the
       phone and the Pages build have no localStorage record, and the
       room Denis signed off (vignette 72/48, no centre boost, shadows
       at normal) must not depend on one. Dials and lights are already
       authored values above; only the DOM half needs the record. */
    if(!lk)lk={vgA:72,vgR:48,vgC:0,sh:0};
    var self=this;""",
    'default look record')

io.open(P, 'w', encoding='utf-8', newline='').write(s)

# ── lab: gradeDice's override reads the shipped mask as its base ──
L = os.path.join(ROOT, 'fark_lab.html')
sl = io.open(L, encoding='utf-8', newline='').read()
old = 'var sp=document.getElementById(\'lvG\');\n  if(sp)sp.textContent=amt===0?\'off\':((amt>0?\'+\':\'\')+amt+\' \'+axis);'
new = ('var sp=document.getElementById(\'lvG\');\n'
       '  if(sp)sp.textContent=amt===0?\'off\':((amt>0?\'+\':\'\')+amt+\' \'+axis);\n'
       '  /* P757: the slider IS the shipped dial now - write it through so a\n'
       '     copied look and the bake never disagree */\n'
       '  E(\'D3X.SIDEDIM_MASK={axis:\'+JSON.stringify(axis)+\',amt:\'+(amt/100)+\'}\');')
c = sl.count(old)
if c != 1:
    o2 = old.replace('\n', '\r\n')
    if sl.count(o2) == 1:
        old, new = o2, new.replace('\n', '\r\n')
    else:
        sys.exit('lab gradeDice tail anchor x%d (game written, lab NOT)' % c)
sl = sl.replace(old, new)
io.open(L, 'w', encoding='utf-8', newline='').write(sl)
edits.append('lab writes the shipped dial')

print('done: %d (%s)' % (len(edits), ', '.join(edits)))
