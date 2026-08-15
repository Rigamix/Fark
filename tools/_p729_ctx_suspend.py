# -*- coding: utf-8 -*-
"""P729 (A3): a lost WebGL context suspends the 3D layer; it no longer dies.

Denis rejoined a match and the dice 'were only spinning and not bouncing'
- with darker, more gradual shadows and a sharper glow. That is the
legacy D3 CSS engine: backgrounding the phone dropped the GL context,
P551's handler called _giveUp, and _giveUp is TERMINAL - the rest of the
session ran on CSS cubes whose 'roll' is a spin animation with no physics
at all. (The look he liked is that engine's face-ramp shading - A3b picks
that up separately.)

Context loss is not a failure, it is the OS taking the GPU away for a
while. The new _suspend hands the table to the DOM dice (P551's real
concern - nothing invisible) but leaves `fail` false - and that is the
whole fix, because the revive path already exists: resumeMatch and
syncMatch's not-ready branch both call boot(), which rebuilds renderer,
scene and model from scratch on a fresh canvas (fresh context). P551's
no-retry rule still holds for REAL failures: _giveUp still sets fail and
boot still refuses on it.
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


sub(u"  _giveUp:function(why){\n"
    u"    if(this.fail)return;\n"
    u"    this.fail=true;this.loading=false;this.ready=false;\n"
    u"    this._need.length=0;\n"
    u"    try{this.detach&&this.detach();}catch(e){}\n"
    u"    try{document.documentElement.classList.remove('fk3d');}catch(e){}\n"
    u"    try{console.warn('[D3X] 3D disabled, falling back to the DOM dice: '+why);}catch(e){}\n"
    u"  },",
    u"  _giveUp:function(why){\n"
    u"    if(this.fail)return;\n"
    u"    this.fail=true;this.loading=false;this.ready=false;\n"
    u"    this._need.length=0;\n"
    u"    try{this.detach&&this.detach();}catch(e){}\n"
    u"    try{document.documentElement.classList.remove('fk3d');}catch(e){}\n"
    u"    try{console.warn('[D3X] 3D disabled, falling back to the DOM dice: '+why);}catch(e){}\n"
    u"  },\n"
    u"  /* P729: A LOST CONTEXT IS A SUSPENSION, NOT A FAILURE. Backgrounding a\n"
    u"     phone can take the GPU away; P551 routed that into _giveUp and the\n"
    u"     rest of the session ran on CSS cubes whose roll is a spin animation\n"
    u"     with no physics (Denis's rejoined match). The DOM dice take over NOW\n"
    u"     - P551's real concern, nothing invisible - but `fail` stays false,\n"
    u"     so the revive costs nothing new: resumeMatch's warm and syncMatch's\n"
    u"     not-ready branch already call boot(), which rebuilds renderer, scene\n"
    u"     and model on a fresh canvas. Real failures still die in _giveUp. */\n"
    u"  _suspend:function(why){\n"
    u"    this.ready=false;this.loading=false;\n"
    u"    this._need.length=0;\n"
    u"    try{this.detach&&this.detach();}catch(e){}\n"
    u"    try{document.documentElement.classList.remove('fk3d');}catch(e){}\n"
    u"    try{console.warn('[D3X] suspended, DOM dice up - boot() revives: '+why);}catch(e){}\n"
    u"  },",
    '_suspend beside _giveUp')

sub(u"    try{r.domElement.addEventListener('webglcontextlost',function(ev){\n"
    u"      try{ev.preventDefault();}catch(e){}\n"
    u"      self._giveUp('the WebGL context was lost');\n"
    u"    },false);}catch(e){}",
    u"    try{r.domElement.addEventListener('webglcontextlost',function(ev){\n"
    u"      try{ev.preventDefault();}catch(e){}\n"
    u"      self._suspend('the WebGL context was lost');/* P729: revivable */\n"
    u"    },false);}catch(e){}",
    'context loss suspends')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits' % n)
