# -*- coding: utf-8 -*-
"""P431 - famLog gets a queue, and somewhere to speak when the match is not up.

TWO FAILURES, MEASURED, NOT ASSUMED.

1. OVERWRITE. setStatusMsg assigns textContent directly, and famLog is a thin
   wrapper over it. Two effects resolving in the same tick both call it
   synchronously, so the second lands before a frame has painted and the first
   is never seen at all. 105 call sites feed this one line.

2. A HIDDEN DIV. statusTop and statusBot live inside #screen-match (line 9051).
   Every famLog fired from the shop, the loadout or a settle path - the innkeep
   buying spare cards, THE TAB IS PAID, FEAT lines, THREE CARDS ONLY - writes
   into an element on a screen that is not displayed. Those messages have never
   been seen by anyone.

The queue fixes the first. A body-level toast fixes the second. They are one
patch because famLog is the single funnel both go through.

WHAT THIS DELIBERATELY DOES NOT DO: setStatusMsg keeps its ~40 direct callers
untouched. Those are turn-state messages ("YOUR TURN", "WARD HOLDS") that are
authoritative and SHOULD replace whatever was there. A queued announcement and
a direct state write can still collide; narrowing that is a separate job with a
different risk profile, and doing it unasked inside this one is how a small fix
becomes a regression.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

def sub_once(hay, old, new, what):
    n = hay.count(old)
    assert n == 1, 'anchor %s matched %d times (want 1)' % (what, n)
    return hay.replace(old, new)

# ── the queue ─────────────────────────────────────────────────────────
s = sub_once(s,
  u"function famLog(msg,color){try{setStatusMsg(msg,color||'gold');}catch(e){}}",
  u"""/* ── THE ANNOUNCE QUEUE ────────────────────────────────────────────────
   famLog used to be a one-line pass-through to setStatusMsg, which assigns
   textContent. Two effects resolving in the same tick both called it
   synchronously, so the second overwrote the first before a frame painted and
   the first was never seen - with 105 call sites feeding one line, that is not
   an edge case.
   A LONGER TIMEOUT WOULD NOT HAVE FIXED IT. The collision happens inside one
   synchronous run of the game loop; only holding the messages somewhere can
   preserve both. */
var _famQ=[],_famQTimer=null;
function famLog(msg,color){
  if(msg===undefined||msg===null||msg==='')return;
  _famQ.push({m:String(msg),c:color||'gold'});
  /* A STORM MUST NOT BECOME A BACKLOG. A hot-dice chain can fire a dozen
     announcements in a second; making the player sit through all of them in
     sequence is worse than dropping the middle. Keep the newest, because the
     latest state is the one that still matters. */
  if(_famQ.length>10)_famQ.splice(0,_famQ.length-10);
  if(!_famQTimer)_famQStep();
}
function _famQStep(){
  var it=_famQ.shift();
  if(!it){_famQTimer=null;return;}
  _famAnnounce(it.m,it.c);
  /* backed up? speak faster, so a queue never reads as lag */
  _famQTimer=setTimeout(_famQStep,_famQ.length>2?380:820);
}
/* One announcement, to whichever surface can actually show it. */
function _famAnnounce(m,c){
  /* THE STRIPS ARE INSIDE #screen-match. Off that screen they are an element
     on a hidden page, which is where every shop, loadout and settle-path
     message has been going: the innkeep buying spare cards, THE TAB IS PAID,
     the FEAT lines. Those have never been seen by anyone. */
  var live=(typeof _currentScreen!=='undefined')&&_currentScreen==='match';
  if(live){
    try{setStatusMsg(m,c);return;}catch(e){}
  }
  try{_famToast(m,c);}catch(e){}
}
/* The off-match surface. Appended to BODY on purpose - putting it in a screen
   is the bug this exists to fix. */
function _famToast(m,c){
  var el=document.getElementById('famToast');
  if(!el){
    el=document.createElement('div');el.id='famToast';
    (document.getElementById('phoneShell')||document.body).appendChild(el);
  }
  el.textContent=m;
  el.className='fam-toast '+(c||'gold');
  /* restart the animation on a repeat message - without this a second toast
     with the same class never re-triggers the fade and looks stuck */
  el.classList.remove('on');void el.offsetWidth;el.classList.add('on');
  clearTimeout(el._t);
  el._t=setTimeout(function(){el.classList.remove('on');},1500);
}""",
  'famLog queue')

# ── the toast's styling ───────────────────────────────────────────────
# Placed next to .status-msg so the two announcement surfaces sit together and
# share a font. No semi-transparency on the plate: the art rules forbid it, and
# a translucent panel over a painted background is exactly what they forbid it
# for. The TEXT fades; the plate does not.
s = sub_once(s,
  u".status-msg.active{color:var(--text);opacity:.85}",
  u""".status-msg.active{color:var(--text);opacity:.85}
/* THE OFF-MATCH ANNOUNCEMENT. Lives on the shell, not inside a screen, because
   the bug it fixes is that #screen-match's status strips are invisible from
   anywhere else. Same family as .status-msg above so the game keeps one voice.
   The PLATE is fully opaque - the art rules forbid semi-transparency over a
   painted background - and only the whole element fades, as one piece. */
.fam-toast{
  position:absolute;left:50%;bottom:11%;transform:translate(-50%,8px);
  max-width:82%;padding:.9cqh 2.6cqh;
  font-family:'JMH Beda',serif;font-size:3.6cqw;letter-spacing:.03em;
  text-align:center;line-height:1.25;
  background:#1c1208;border:2px solid #6b5228;border-radius:4px;
  box-shadow:0 3px 0 #0a0603;
  color:#f0c860;text-shadow:0 1px 0 rgba(20,12,4,.85);
  opacity:0;pointer-events:none;z-index:9400;
  transition:opacity .22s ease,transform .22s ease;
}
.fam-toast.on{opacity:1;transform:translate(-50%,0)}
.fam-toast.red{color:#e07058;border-color:#7a3428}
.fam-toast.green{color:#7ec888;border-color:#3f6b44}""",
  'toast css')

assert s != orig, 'nothing changed'
assert s.count(u'function famLog(') == 1, 'famLog declared %d times' % s.count(u'function famLog(')
assert u'_famQStep' in s and u'.fam-toast{' in s
with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P431 applied: famLog queued, off-match toast added')
