# -*- coding: utf-8 -*-
"""P823: the enchant description pass + fog finally SHOWS.

Denis's playthrough notes, verbatim targets: "enchant descriptions
pass (Fog confusing)" and "Fog does nothing + enchant effects should
linger visually".

DESCRIPTIONS (census-confirmed wrong or empty):
 - ward said "a bust halves your BANK" - wrong direction: doBust
   CREDITS half the turn to the bank. Now says what happens.
 - snare never said what the trap does (halves that lane's score once).
 - break said "for good" - stale: removal is match-scoped by ruling.
 - fog's "hides this seat from the rival's reckoning" - the flagged
   one; now says what the player will see.

THE FOG LOOK (reachability-tested first): a chip-level overlay is
INVISIBLE under the 3D canvas (screenshot-proven), so the look rides
the layers that do show: the fogged die's face drops PAST full shadow
through the dim system (d._fogDim floors the ramp at 1.15 in both dim
sites - _dimMap already supports k>1, "the bust wipe" comment), and a
drifting cloud glyph floats in the top layer at the die's rect for the
reckoning beat. The dim persists until their row naturally rebuilds -
the lingering Denis asked for. FKFX meta gains 'ench:fog' and
'ench:break' so their fire beats stop falling to the generic spray
(the census's only two unlisted enchants).
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


# ── descriptions ──
sub(r"""    desc:'Brand a shield on one face. Keep it: it banks nothing and arms this turn — a bust halves your bank instead of taking it all.',""",
    r"""    desc:'Brand a shield on one face. Keep it: it banks nothing and arms this turn — bust, and HALF the turn is saved to your bank instead of losing it all.',""",
    'ward desc says the true direction')

sub(r"""    desc:'Brand a snare on one face. Keep it: it banks nothing and sets a trap in this lane for the rival\u2019s next turn.',""",
    r"""    desc:'Brand a snare on one face. Keep it: it banks nothing and traps this lane — next turn, the rival\u2019s die in this seat scores HALF, once.',""",
    'snare desc says what the trap does')

sub(r"""    desc:'Brand a skull on one face. Keep it: it banks nothing and breaks another of your dice for good — and whatever that die was dies loudly.',""",
    r"""    desc:'Brand a skull on one face. Keep it: it banks nothing and breaks another of your dice for the rest of the match — and whatever that die was dies loudly.',""",
    'break desc matches the match-scoped ruling')

sub(r"""    desc:'Brand a cloud on one face. Keep it: it banks nothing and hides this seat from the rival\u2019s reckoning next turn.',""",
    r"""    desc:'Brand a cloud on one face. Keep it: it banks nothing and blinds the rival to this seat next turn — the fogged die goes dark on their table and they play around it.',""",
    'fog desc says what the player sees')

# ── FKFX meta for the two generic-firing enchants ──
sub("""    'ench:snuff':{f:'BREAK',c:'#4a4060',p:1}, 'ench:quicksilver':{f:'TRANSFORM',c:'#dfe8f2',p:1},""",
    """    'ench:snuff':{f:'BREAK',c:'#4a4060',p:1}, 'ench:quicksilver':{f:'TRANSFORM',c:'#dfe8f2',p:1},
    'ench:break':{f:'BREAK',c:'#c66058',p:2}, 'ench:fog':{f:'SET',c:'#a8b0b8',p:1},/* P823: the census's only two unlisted enchants */""",
    'fog and break get their family fires')

# ── the fog dim floor, both dim sites ──
sub("""    var _kk=(Math.round(_k*_R.steps)/_R.steps)*this.SIDEDIM_MAX;""",
    """    var _kk=(Math.round(_k*_R.steps)/_R.steps)*this.SIDEDIM_MAX;
    if(d._fogDim)_kk=Math.max(_kk,1.15);/* P823: a fogged die sits past full shadow (_dimMap supports k>1 - the bust-wipe path) */""",
    'settleDim honors the fog')

sub("""            var _kkL=(Math.round(_kL*D3X.SIDEDIM_RAMP.steps)/D3X.SIDEDIM_RAMP.steps)*D3X.SIDEDIM_MAX;""",
    """            var _kkL=(Math.round(_kL*D3X.SIDEDIM_RAMP.steps)/D3X.SIDEDIM_RAMP.steps)*D3X.SIDEDIM_MAX;
            if(d._fogDim)_kkL=Math.max(_kkL,1.15);/* P823 */""",
    'sync dim honors the fog')

# ── the consumption branch paints the look ──
sub("""        if(_fi>=0&&_fogV.length>1){
          _fogV.splice(_fi,1);_fogM.splice(_fi,1);if(_fogE)_fogE.splice(_fi,1);_fogCut=_fi;/* P762 */
          try{famLog('FOG — THEY MISREAD A SEAT');}catch(e){}
        }""",
    """        if(_fi>=0&&_fogV.length>1){
          _fogV.splice(_fi,1);_fogM.splice(_fi,1);if(_fogE)_fogE.splice(_fi,1);_fogCut=_fi;/* P762 */
          try{famLog('FOG — THEY MISREAD A SEAT');}catch(e){}
          /* P823: THE FOG SHOWS. Chip overlays are invisible under the 3D
             canvas (screenshot-proven), so the blinded die goes DARK
             through the dim system and a cloud drifts over its seat in
             the top layer. The dim lingers until their row rebuilds. */
          try{
            var _fgChip=_oFree[_fi]&&_oFree[_fi].el;
            if(_fgChip&&window.D3X&&D3X.dice){
              var _fgD=null;
              for(var _fk=0;_fk<D3X.dice.length;_fk++)if(D3X.dice[_fk].chip===_fgChip){_fgD=D3X.dice[_fk];break;}
              if(_fgD){_fgD._fogDim=true;try{D3X._settleDim(_fgD);}catch(e2){}}
            }
            if(_fgChip){
              var _fgR=_fgChip.getBoundingClientRect();
              if(_fgR.width>0){
                var _fgTag=document.createElement('div');
                _fgTag.className='fog-float';_fgTag.textContent='\\u2601';
                _fgTag.style.left=(_fgR.left+_fgR.width/2)+'px';
                _fgTag.style.top=(_fgR.top+_fgR.height/2)+'px';
                document.body.appendChild(_fgTag);
                setTimeout(function(){if(_fgTag.parentNode)_fgTag.remove();},3200);
              }
            }
          }catch(e){}
        }""",
    'the fog paints its look')

# ── the cloud CSS ──
sub("""/* — Grog's Flask: warm amber — */""",
    """/* P823: the fog cloud - floats in the top layer over the blinded die
   (chip-level overlays are invisible under the 3D canvas). */
.fog-float{position:fixed;transform:translate(-50%,-55%);font-size:30px;color:#cdd5dc;
  text-shadow:0 2px 6px #000c,0 0 14px #a8b0b880;pointer-events:none;z-index:60;
  animation:fogFloatDrift 2.4s ease-in-out infinite}
@keyframes fogFloatDrift{0%,100%{transform:translate(-58%,-55%);opacity:.92}
  50%{transform:translate(-42%,-58%);opacity:1}}
/* — Grog's Flask: warm amber — */""",
    'the cloud CSS')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
