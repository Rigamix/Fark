# -*- coding: utf-8 -*-
"""P745: the amber holds and then dissolves; the tooltip narrows and its
title outline lightens.

- AMBER.holdMs/fadeMs: the shell stays 1.4s after the throw lands (Denis:
  'make amber return longer') and the crack DISSOLVES - swelling slightly
  while its opacity and the die's own colour return on the same curve -
  rather than blinking out. Both live on AMBER, beside the shell, so
  anything using amberShell inherits the timing.
- the tooltip BODY narrows inside the box (the box keeps its width for
  the title); the title's outline mixes far less black - it reads as a
  deep version of the title's own colour rather than near-black.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    """Collect, then write ONCE at the end - a sub that exits mid-way
    leaves the earlier edits unwritten, which is exactly how the first
    attempt at this patch silently did nothing."""
    global s
    c = s.count(old)
    if c != 1:
        old2 = old.replace('\n', '\r\n')
        if s.count(old2) == 1:
            old, new = old2, new.replace('\n', '\r\n')
        else:
            sys.exit('ANCHOR x%d for %s (nothing written)' % (c, label))
    s = s.replace(old, new)
    edits.append(label)


sub(u"  AMBER:{col:0xd88a20, corner:12, rims:2, op:0.42, spec:45, ghost:0.25, bub:4},",
    u"""  /* P745: holdMs is how long the amber STAYS once the throw has landed
     (Denis: 'make amber return longer'); fadeMs is the crack itself,
     which dissolves rather than vanishing. Beside the shell, so every
     user of amberShell inherits the same timing. */
  AMBER:{col:0xd88a20, corner:12, rims:2, op:0.42, spec:45, ghost:0.25, bub:4,
    holdMs:1400, fadeMs:520},""",
    'hold + fade constants')

sub(u"""    var have=d.obj.getObjectByName('fkAmber');
    if(!on){
      if(have){d.obj.remove(have);
        have.traverse(function(o){if(o.material&&o.material.dispose)o.material.dispose();});}
      d.obj.traverse(function(o){
        if(o.isMesh&&o.material&&o.userData._ambCol){
          o.material.color.copy(o.userData._ambCol);delete o.userData._ambCol;}
      });
      return true;
    }""",
    u"""    var have=d.obj.getObjectByName('fkAmber');
    if(!on){
      /* P745: THE CRACK DISSOLVES. Removing the group outright made the
         amber blink out; it swells a little and fades over fadeMs while
         the die's own colour returns on the same curve, so the die
         EMERGES rather than being uncovered. colOverride===0 forces the
         old instant path for teardown (a die leaving the table). */
      var _A=this.AMBER,_fade=(colOverride===0)?0:(_A.fadeMs||520);
      if(have&&_fade>0&&!have.userData._dying){
        have.userData._dying=1;
        var _t0=performance.now(),_op=[],_cols=[];
        have.traverse(function(o){if(o.isMesh&&o.material)_op.push([o,o.material.opacity]);});
        d.obj.traverse(function(o){
          if(o.isMesh&&o.material&&o.userData._ambCol)
            _cols.push([o,o.material.color.clone(),o.userData._ambCol]);
        });
        (function _step(){
          var k=(performance.now()-_t0)/_fade;
          if(k>=1){
            d.obj.remove(have);
            have.traverse(function(o){if(o.material&&o.material.dispose)o.material.dispose();});
            _cols.forEach(function(c){c[0].material.color.copy(c[2]);delete c[0].userData._ambCol;});
            return;
          }
          _op.forEach(function(b){b[0].material.opacity=b[1]*(1-k);});
          have.scale.setScalar(1+0.14*k);
          _cols.forEach(function(c){c[0].material.color.lerpColors(c[1],c[2],k);});
          requestAnimationFrame(_step);
        })();
        return true;
      }
      if(have){d.obj.remove(have);
        have.traverse(function(o){if(o.material&&o.material.dispose)o.material.dispose();});}
      d.obj.traverse(function(o){
        if(o.isMesh&&o.material&&o.userData._ambCol){
          o.material.color.copy(o.userData._ambCol);delete o.userData._ambCol;}
      });
      return true;
    }""",
    'crack dissolves')

sub(u"""  -webkit-text-stroke:0.3cqw color-mix(in srgb,var(--cft-a,#f0c860) 62%,#1a0d02);""",
    u"""  /* P745: 62% mixed toward near-black still read black. 82% of the
     title's own colour against a warm brown - a deep version of the
     hue, not a shadow of it - and thinner again. */
  -webkit-text-stroke:0.22cqw color-mix(in srgb,var(--cft-a,#f0c860) 82%,#5a2f08);""",
    'title outline lighter')

sub(u"""#cardFocusTip .cft-body{font-family:var(--font-dlg);font-size:3.4cqw;/* P728: the dialogue font (Denis) */""",
    u"""/* P745: the BODY narrows inside the box (Denis) - the title keeps the
   full width, the prose gets a shorter measure to read down. */
#cardFocusTip .cft-body{width:84%;margin-left:auto;margin-right:auto;
  font-family:var(--font-dlg);font-size:3.4cqw;/* P728: the dialogue font (Denis) */""",
    'body narrower')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
