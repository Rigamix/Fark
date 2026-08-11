# -*- coding: utf-8 -*-
"""P617: the activation beat gets particles, and every cue takes the card's own colour.

Denis: "attaching a visual reference for activation glow and particles although
the color should depend on the card family (color of their borders)".

--card-accent IS THAT COLOUR. It is already the border: `.mcard-active .gcard`
draws `border:2px solid var(--card-accent,...)` and each card id sets its own
(frozen_die a pale blue, double_down a warm gold, wild_die violet...). So the
glow, the fire flash and the sparks all read the same custom property, and a
card that never sets one falls back to the deck gold - no new colour table, and
no way for the four cues to disagree about what colour a card is.

THE PARTICLES REUSE FX, which is the existing pooled emitter behind every other
burst in the game (spawnPixelSparks, spawnShards, the coin fountain). Its
contract is {x,y,vx,vy,life,size,color,g,rot,vr,fade} and `g` is gravity, so an
upward plume that slows and falls back - the reference image's shape - needs no
new machinery at all. spawnPixelSparks was NOT reused directly: it fires a flat
8-direction ring in a hardcoded #c8a050, which is the wrong shape and the wrong
colour for this.

WHY THE PLUME AND NOT A RING: the reference shows the light leaving the card
UPWARD, which is also the direction the player just dragged. A radial ring reads
as an impact; a plume reads as the card discharging along the gesture.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:120]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ── 1. the emitter, beside the other burst helpers ────────────────────────
sub(u"/* Shatter burst — angular chunks pop outward + tumble + fall under",
    u"/* P617: THE CARD ACTIVATION PLUME. Light leaves the card upward - the way\n"
    u"   the player just dragged it - rises, slows under gravity and falls back,\n"
    u"   which is the shape in Denis's reference. A radial ring would read as an\n"
    u"   impact; this reads as the card discharging along the gesture.\n"
    u"   The colour is the CARD'S OWN --card-accent, i.e. its border, so the plume\n"
    u"   can never disagree with the glow or the frame. Reuses FX, the pooled\n"
    u"   emitter behind every other burst here - the pool silently drops when it is\n"
    u"   full, so a busy moment costs nothing. */\n"
    u"function _cardAccent(el){\n"
    u"  try{\n"
    u"    var c=getComputedStyle(el).getPropertyValue('--card-accent');\n"
    u"    c=(c||'').trim();\n"
    u"    if(c)return c;\n"
    u"  }catch(e){}\n"
    u"  return 'rgba(255,215,0,.9)';\n"
    u"}\n"
    u"function spawnCardBurst(el,color){\n"
    u"  if(!el||typeof FX==='undefined'||!FX.emit)return;\n"
    u"  var r=el.getBoundingClientRect();\n"
    u"  if(!(r.width>0))return;\n"
    u"  var cx=r.left+r.width/2, cy=r.top+r.height*0.42;\n"
    u"  var col=color||_cardAccent(el);\n"
    u"  for(var i=0;i<26;i++){\n"
    u"    /* upward, +/- ~30 degrees, so the plume keeps a clear direction */\n"
    u"    var a=-Math.PI/2+(Math.random()-0.5)*1.05;\n"
    u"    var sp=70+Math.random()*150;\n"
    u"    FX.emit({x:cx+(Math.random()-0.5)*r.width*0.78,\n"
    u"             y:cy+(Math.random()-0.5)*r.height*0.42,\n"
    u"             vx:Math.cos(a)*sp, vy:Math.sin(a)*sp,\n"
    u"             g:150+Math.random()*90,\n"
    u"             life:0.55+Math.random()*0.55,\n"
    u"             size:(Math.random()<0.4?3:4),\n"
    u"             color:col});\n"
    u"  }\n"
    u"  /* a few bright motes that hang and drift, the slow ones in the reference */\n"
    u"  for(var j=0;j<7;j++){\n"
    u"    var a2=-Math.PI/2+(Math.random()-0.5)*1.6;\n"
    u"    FX.emit({x:cx+(Math.random()-0.5)*r.width*0.9, y:cy,\n"
    u"             vx:Math.cos(a2)*30, vy:Math.sin(a2)*46, g:26,\n"
    u"             life:0.9+Math.random()*0.7, size:2, color:col});\n"
    u"  }\n"
    u"}\n"
    u"/* Shatter burst — angular chunks pop outward + tumble + fall under",
    'P617 spawnCardBurst')

# ── 2. fire it on activation ──────────────────────────────────────────────
sub(u"  try{_haptic([12,30,12]);}catch(e){}\n"
    u"  mcardEl.classList.add('card-fired');",
    u"  try{_haptic([12,30,12]);}catch(e){}\n"
    u"  /* P617: the plume, in the card's own colour, BEFORE the effect runs - so a\n"
    u"     card that rebuilds the row as part of its effect (the Pyre, a self-refund)\n"
    u"     still gets its beat off the element the player was actually holding. */\n"
    u"  try{spawnCardBurst(mcardEl);}catch(e){}\n"
    u"  mcardEl.classList.add('card-fired');",
    'P617 fire the plume')

# ── 3. every cue takes --card-accent ──────────────────────────────────────
sub(u".mcard.armed .gcard{outline:0.22cqw solid rgba(255,226,150,.92);outline-offset:-0.22cqw}",
    u"/* P617: the armed rim is the CARD'S border colour, not a fixed gold */\n"
    u".mcard.armed .gcard{outline:0.22cqw solid var(--card-accent,rgba(255,226,150,.92));\n"
    u"  outline-offset:-0.22cqw}",
    'P617 armed rim colour')

sub(u".mcard.dragging.armed{\n"
    u"  filter:drop-shadow(0 8px 24px rgba(0,0,0,.7))\n"
    u"         drop-shadow(0 0 0.9cqw rgba(255,214,120,.95))\n"
    u"         drop-shadow(0 0 2.6cqw rgba(255,180,60,.55))\n"
    u"         brightness(1.16) saturate(1.12)!important}",
    u".mcard.dragging.armed{\n"
    u"  filter:drop-shadow(0 8px 24px rgba(0,0,0,.7))\n"
    u"         drop-shadow(0 0 0.9cqw var(--card-accent,rgba(255,214,120,.95)))\n"
    u"         drop-shadow(0 0 2.6cqw var(--card-accent,rgba(255,180,60,.55)))\n"
    u"         brightness(1.16) saturate(1.12)!important}",
    'P617 armed halo colour')

sub(u"@keyframes cardFired{\n"
    u"  0%{filter:drop-shadow(0 0 1.4cqw rgba(255,240,200,1)) brightness(1.6) saturate(1.2)}\n"
    u"  100%{filter:none}}",
    u"@keyframes cardFired{\n"
    u"  0%{filter:drop-shadow(0 0 1.6cqw var(--card-accent,rgba(255,240,200,1)))\n"
    u"            drop-shadow(0 0 0.5cqw rgba(255,248,225,.9)) brightness(1.55) saturate(1.2)}\n"
    u"  100%{filter:none}}",
    'P617 fired flash colour')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits applied' % n)
