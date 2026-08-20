# -*- coding: utf-8 -*-
"""P835b: ONE drag canceller, and it cancels the real state.

Three identical copies of a broken canceller (coin-flip / nudge /
chisel activation paths) nulled _vgDragState through field names the
state never carried (clone/srcEl - a previous drag system's shape).
Net effect on a real cancel: the carried die stayed LIFTED (phys.y
never restored), the neighbour lerp kept running (raf never
cancelled), move listeners leaked, and the origin class stuck.

One canonical _vgDragCancel() using the actual state shape; the three
copies become calls. (One function, one exit path - the same rule
_removeDieAt records.)
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label, count=1):
    global s
    hits = s.count(old)
    if hits == count:
        s = s.replace(old, new)
        edits.append(label)
        return
    # the standing trap: regions mix per-line endings - CRLF fallback
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != count:
        sys.exit('ANCHOR x%d (wanted %d) for %s (nothing written)' % (len(ms), count, label))
    # replace each, preserving that site's own line endings in NEW
    for m in reversed(ms):
        seg = m.group(0)
        rep = new.replace('\n', '\r\n') if '\r\n' in seg else new
        s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


# the canonical canceller, beside the drag code
sub("""function _commitVagabondDrag(){""",
    """/* P835b: THE ONE CANCELLER. Three activation paths carried identical
   copies nulling the state through clone/srcEl - fields this drag
   system never had - so a cancel left the carried die lifted, the
   neighbour lerp running and the listeners leaked. */
function _vgDragCancel(){
  var _st=(typeof _vgDragState!=='undefined')?_vgDragState:null;
  if(!_st)return;
  _vgDragState=null;
  try{
    if(_st.raf)cancelAnimationFrame(_st.raf);
    if(_st.onMove){document.removeEventListener('pointermove',_st.onMove,{passive:false});
      document.removeEventListener('touchmove',_st.onMove,{passive:false});}
    if(_st.die)_st.die.classList.remove('vg-drag-origin');
    if(_st.me&&_st.y0!==undefined)_st.me.phys.y=_st.y0;
    if(_st.order&&_st.homes)_st.order.forEach(function(d,i){d.phys.x=_st.homes[i];});
  }catch(e){}
}
function _commitVagabondDrag(){""",
    'the one canceller')

# the three broken copies become calls
sub("""  if(typeof _vgDragState!=='undefined'&&_vgDragState){
    if(_vgDragState.clone&&_vgDragState.clone.parentNode)_vgDragState.clone.parentNode.removeChild(_vgDragState.clone);
    if(_vgDragState.srcEl)_vgDragState.srcEl.classList.remove('vg-drag-origin');
    _vgDragState=null;
  }""",
    """  try{_vgDragCancel();}catch(e){}/* P835b: the one canceller (the old inline copy used a dead state shape) */""",
    'three copies become calls', count=3)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d (%s)' % (len(edits), ', '.join(edits)))
