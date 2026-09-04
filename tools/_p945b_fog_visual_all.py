# -*- coding: utf-8 -*-
u"""P945b: the fog VISUAL follows every cut, not just the first.

P945 made the fog scoring path take every due mark - collected, spliced
descending, restored ascending - and left the visual reading _oFree[_fi], the
first cut alone. Two fogs would have blinded two seats in the reckoning and
dimmed one die with one cloud over it.

That is the half-applied shape exactly, in the patch written to avoid it: P919
taught that fixing one side of a two-part behaviour is worse than fixing
neither, because the disagreement is live and invisible - and here the
disagreement would be between what the rival CANNOT SEE and what the player is
SHOWN it cannot see. The screen would be lying about the mechanic.

The dim and the cloud now run per cut, and _fi is gone rather than left as a
stale first-of-many that a later reader could mistake for the fogged seat.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


sub(u"""        var _fi=_fogIdx.length?_fogIdx[0]:-1;
        _fogCuts=_fogIdx.slice();""",
    u"""        _fogCuts=_fogIdx.slice();""",
    '1 the stale first-of-many goes')

sub(u"""        if(_fogCuts.length){
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
    u"""        if(_fogCuts.length){
          try{famLog('FOG — THEY MISREAD '+(_fogCuts.length>1?'TWO SEATS':'A SEAT'));}catch(e){}
          /* P823: THE FOG SHOWS. Chip overlays are invisible under the 3D
             canvas (screenshot-proven), so the blinded die goes DARK
             through the dim system and a cloud drifts over its seat in
             the top layer. The dim lingers until their row rebuilds.
             P945b: ONCE PER CUT. This read _oFree[_fi] - the first fogged
             index - while the scoring path had already been taught to blind
             every one, so two fogs hid two seats from the rival and showed the
             player one cloud. The screen would have been lying about the
             mechanic, which is the half-applied shape P919 exists to warn
             about. */
          _fogCuts.forEach(function(_fx){
            try{
              var _fgChip=_oFree[_fx]&&_oFree[_fx].el;
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
          });
        }""",
    '2 the dim and the cloud run per cut')

# ── post-asserts ────────────────────────────────────────────────────
code = re.sub(r'/\*[\s\S]*?\*/', '', s)

# THE STALE INDEX IS GONE - SCOPED TO THE FOG REGION. A whole-file search for
# the bare token matched an unrelated loop counter in a string-hash function
# (for(var _fi=0;_fi<_gn.length;_fi++)), so the assert failed on code it has no
# business reading. The region is the unit; the token is not. Sixth instance of
# that family, and the first one caught before it cost an edit.
_fogStart = code.index('var _fogCuts=[];')
_fogEnd = code.index('crowsCtx.crowsLuckFiredThisRoll=false;', _fogStart)
if re.search(r'\b_fi\b', code[_fogStart:_fogEnd]):
    sys.exit('the stale _fi survives in the fog block (nothing written)')
# the visual iterates the cuts
_v = code.index('_fogCuts.forEach(function(_fx)')
if code.count('_fogCuts.forEach(function(_fx)') != 1:
    sys.exit('the visual does not iterate the cuts exactly once (nothing written)')
if '_oFree[_fx]' not in code[_v:_v + 400]:
    sys.exit('the visual does not read the per-cut index (nothing written)')
# and the scoring path is untouched: descending out, ascending back
if 'return b-a;' not in code:
    sys.exit('the descending splice was lost (nothing written)')
if '_fogCuts.forEach(function(ix){used.splice(ix,0,false);});' not in code:
    sys.exit('the ascending restore was lost (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
