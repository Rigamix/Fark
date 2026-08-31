# -*- coding: utf-8 -*-
u"""P895 (FX brief step 8): the states move onto the roster and thirteen CSS
rules that were painting squares around a cube come out.

THE THREE STATES. frozen and dampened are CRUST, blind is a VEIL, per the
brief's table - the form decides the canvas, so the two crusts go under on
dgCanvas and the veil goes over on stCanvas. Their inks are the deleted rules'
own colours converted, not new ones: #64b4ff IS rgba(100,180,255) from
.die.die-frozen, #c8a064 is the sawdust tint's rgba(200,160,100), #1a1a2a is
the blind rule's own background.

THE FOURTH STATE IS ALREADY DONE AND NOT BY A MARK. `spent` is `brand-spent`
(24568) and D3X._spentLook (28589) already drives it on the die's own emissive
map, re-derived every sync. That is the material route _paintForm's comment
points at for true desaturation, and it is better than a fill: it dims the
brand's glow specifically rather than washing the whole face. There is nothing
to move.

THE PREDICATE READS THE CHIP, NOT THE RECORD. The brief's sketch row used
`!!d._frozen`, but `d` inside a roster row is D3X's {chip,obj,mat,...} record
and `_frozen` lives on the game's pool die. It would have been undefined on
every die, forever, and the row would have painted nothing while looking
entirely correct.

WHAT COMES OUT, and why each was wrong rather than merely unused:
  nine that painted an axis-aligned box on a 3D die - all sit after
  `.die.d3on{box-shadow:none!important}` (2811) at equal specificity, so all
  of them win: .die.combo-glow, the four .die.eff-glow-*, .die.card-reroll,
  .die.card-reroll.crr-blue, .die.card-reroll-settle, .die.die-frozen,
  .die.die-blind;
  four that painted nothing at all - `.die.d3on::before,::after{display:none
  !important}` (2812) sets `display`, and none of these pseudo rules declares
  it, so the !important none survives every one of them: .die.die-dampened
  ::before, .die.die-dampened-fresh::after, .die.die-kindred::before/::after,
  .die.combo-glow::after.

A TOMBSTONE AT EACH SITE rather than one at the top. Six of these deletions
are hundreds of lines apart, and a reader who greps for a missing selector
should land on the reason, not on nothing.

WHAT SURVIVES, asserted below because each is a near neighbour of something
deleted: .die.die-frozen-mark, .die.die-frozen-entry, .die-reveal, the
`:not(.die-frozen)` in the idle-breath guard (4020 - a frozen die must still
not breathe), the dRoll keyframes (17 references), .die.die-palmed and
cfBankPuff.

NOT DONE HERE, and recorded in docs/OPEN.md: the JS still adds and removes
combo-glow, card-reroll, crr-blue, card-reroll-settle and the four eff-glow-*
classes. They are now inert. Their beats are not silent - every eff-glow site
also calls spawnPixelSparks, which goes through FX.emit and works - but the
die-local part of them is gone until somebody routes it through _fxMark, and
that is a decision about feel, not a mechanical follow-on.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
before_len = len(s)
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


# ══ 1. the three rows ═══════════════════════════════════════════════
sub(u"""         return false;
       }}]},
  ],""",
    u"""         return false;
       }}]},
    /* P895: THE STATES. through:true is what makes them states - a frozen die
       stays frozen while the others tumble, which is exactly the guard the
       old global _rolling() skip could not express. The inks are the deleted
       CSS rules' own colours converted, never new ones: #64b4ff is
       rgba(100,180,255) from .die.die-frozen, #c8a064 is the sawdust tint's
       rgba(200,160,100), #1a1a2a is .die.die-blind's own background.
       THESE READ THE CHIP, NOT THE RECORD. `d` here is D3X's {chip,obj,mat}
       row; the game's `_frozen` flag lives on the pool die, so a predicate
       reading d._frozen would be undefined on every die forever and this row
       would paint nothing while looking right.
       ORDER against the two rows above does not matter - every form goes
       through _paintHalo, which composites with 'lighter', and step 7 proved
       that pass byte-identical with the order swapped. */
    {id:'frozen',layer:'under',through:true,style:'crust',ink:'#64b4ff',
     on:function(d){return d.chip.classList.contains('die-frozen');}},
    /* dampened ends when the fade begins. `dampen-fade` is the class that used
       to restore the filter, so it is already this file's own signal that the
       state is over - and it has to be read, because `die-dampened` itself is
       never removed from the die. */
    {id:'damp',layer:'under',through:true,style:'crust',ink:'#c8a064',
     on:function(d){return d.chip.classList.contains('die-dampened')&&
       !d.chip.classList.contains('dampen-fade');}},
    {id:'blind',layer:'over',through:true,style:'veil',ink:'#1a1a2a',
     on:function(d){return d.chip.classList.contains('die-blind');}},
  ],""",
    '1 the three state rows')

# ══ 2. combo-glow: a box pulse plus a sheen that never painted ══════
sub(u""".die.combo-glow{animation:comboGlow .45s ease-out both;animation-delay:var(--gd,0s)}
@keyframes comboGlow{0%{filter:brightness(1);box-shadow:0 0 8px rgba(200,160,80,.4)}40%{filter:brightness(1.25);box-shadow:0 0 14px 3px rgba(255,200,80,.65)}100%{filter:brightness(1);box-shadow:0 0 8px rgba(200,160,80,.4)}}
.die.combo-glow::after{
  content:'';position:absolute;inset:0;border-radius:2px;z-index:3;pointer-events:none;
  background:linear-gradient(105deg,transparent 40%,rgba(255,240,200,.15) 48%,rgba(255,255,255,.2) 50%,rgba(255,240,200,.15) 52%,transparent 60%);
  background-size:300% 100%;
  animation:comboSheen .5s ease-out both;animation-delay:var(--gd,0s);
}
@keyframes comboSheen{0%{background-position:200% 0;opacity:0}12%{opacity:1}80%{opacity:1}100%{background-position:-100% 0;opacity:0}}""",
    u"""/* P895: .die.combo-glow deleted. Its pulse was a box-shadow, which around a
   cube is an axis-aligned square that does not touch the silhouette, and its
   ::after sheen never painted at all - 2812 sets display:none!important on
   every .d3on pseudo-element and this rule never declared display. The class
   is still added and removed by the combo code; it is inert now. */""",
    '2 combo-glow')

# ══ 3. the four effect glows ════════════════════════════════════════
sub(u""".die.eff-glow-gold,.die.eff-glow-green,.die.eff-glow-red,.die.eff-glow-blue{transition:box-shadow .3s ease,filter .3s ease}
.die.eff-glow-gold{box-shadow:0 0 12px 3px rgba(255,200,60,.6),0 0 4px rgba(255,180,40,.35)!important;filter:brightness(1.15)}
.die.eff-glow-green{box-shadow:0 0 12px 3px rgba(60,200,90,.6),0 0 4px rgba(40,180,60,.35)!important;filter:brightness(1.12)}
.die.eff-glow-red{box-shadow:0 0 12px 3px rgba(220,60,40,.6),0 0 4px rgba(200,40,30,.35)!important;filter:brightness(1.1)}
.die.eff-glow-blue{box-shadow:0 0 12px 3px rgba(80,160,240,.6),0 0 4px rgba(60,140,220,.35)!important;filter:brightness(1.12)}""",
    u"""/* P895: the four .die.eff-glow-* deleted - four coloured squares around a
   cube, each winning over 2811 on source order. The sparks at these sites are
   untouched: spawnPixelSparks goes through FX.emit, which is the one pipeline
   that always worked on a match die. */""",
    '3 the effect glows')

# ══ 4. sawdust: a filter on the chip and a poof that never painted ══
sub(u"""/* Sawdust dampened die */
/* dieDampen used to set `animation:` which overrode the .rolling
   keyframes — dampened dice appeared to skip rolling and just appear at
   their final face. Use a `transition:` on filter instead so it stacks
   cleanly on top of the rolling rotation. */
/* Sawdust dampened die — clearly tinted brown with a sepia/dust look so the player
   can see at a glance which opp dice the Sawdust card neutered. */
.die.die-dampened{
  filter:brightness(.55) saturate(.3) sepia(.6) hue-rotate(-15deg);
  transition:filter .5s ease-out;
  position:relative;
}
.die.die-dampened::before{
  content:'';position:absolute;inset:0;pointer-events:none;border-radius:inherit;
  background:radial-gradient(circle at 50% 30%,rgba(200,160,100,.25) 0%,rgba(120,80,40,.18) 60%,transparent 100%);
  mix-blend-mode:multiply;z-index:1;
}
.die.die-dampened.dampen-fade{filter:brightness(1) saturate(1) sepia(0) hue-rotate(0)}
.die.die-dampened.dampen-fade::before{opacity:0;transition:opacity .5s ease-out}
/* Sawdust spray — quick poof when the die is initially dampened.
   CRITICAL: this MUST run on a ::after pseudo-element, NOT on the die
   itself. Setting `animation:` on `.die` overrides the `.rolling` spin
   keyframes — the exact bug the comment above warns about, which got
   reintroduced. Driving the poof on ::after leaves the die's own
   `animation` slot free for `.rolling` (and its `filter` free for the
   `.die-dampened` brown tint). */
.die.die-dampened-fresh::after{
  content:'';position:absolute;inset:-5px;pointer-events:none;border-radius:6px;
  z-index:3;
  background:radial-gradient(circle,rgba(210,165,95,.65) 0%,rgba(160,115,55,.32) 42%,transparent 72%);
  animation:sawdustPoof .55s ease-out both;
}
@keyframes sawdustPoof{
  0%  {opacity:0;transform:scale(.35)}
  35% {opacity:1;transform:scale(1.25)}
  100%{opacity:0;transform:scale(1.7)}
}""",
    u"""/* P895: the sawdust rules deleted, and the state is a roster row now
   ({id:'damp'}, a CRUST in this tint). The filter tinted the CHIP, which in
   3D is a transparent host with the die on a canvas - so it browned nothing;
   the ::before wash and the ::after poof both never painted, because 2812's
   display:none!important on .d3on pseudo-elements is a property neither of
   them declared. The long comment that used to sit here warned against
   putting `animation:` on .die because it overrides .rolling; that hazard is
   real and now moot, since nothing here animates the element any more. */""",
    '4 the sawdust rules')

# ══ 5. the card reroll trio ═════════════════════════════════════════
sub(u""".die.card-reroll{
  box-shadow:0 0 14px 4px rgba(255,180,40,.7),0 0 6px rgba(255,220,80,.4)!important;
  filter:brightness(1.25)!important;
  animation:dRoll .4s linear infinite,cardRerollPulse .6s ease-in-out infinite!important;
  z-index:6;
}
@keyframes cardRerollPulse{
  0%,100%{box-shadow:0 0 14px 4px rgba(255,180,40,.7),0 0 6px rgba(255,220,80,.4)}
  50%{box-shadow:0 0 20px 6px rgba(255,180,40,.9),0 0 10px rgba(255,220,80,.6)}
}
/* P828: encore's shimmer is STARSTONE BLUE - the spec's contrast with
   powder keg's explosion. The modifier swaps the animation, not just
   the static shadow: keyframe box-shadows beat any static override. */
.die.card-reroll.crr-blue{
  box-shadow:0 0 14px 4px rgba(143,168,255,.7),0 0 6px rgba(190,205,255,.4)!important;
  animation:dRoll .4s linear infinite,cardRerollPulseBlue .6s ease-in-out infinite!important;
}
@keyframes cardRerollPulseBlue{
  0%,100%{box-shadow:0 0 14px 4px rgba(143,168,255,.7),0 0 6px rgba(190,205,255,.4)}
  50%{box-shadow:0 0 20px 6px rgba(143,168,255,.9),0 0 10px rgba(190,205,255,.6)}
}
.die.card-reroll-settle{
  animation:cardRerollSettle .4s ease-out forwards!important;
}
@keyframes cardRerollSettle{
  0%{box-shadow:0 0 18px 5px rgba(255,180,40,.8);filter:brightness(1.3)}
  100%{box-shadow:0 0 0 0 transparent;filter:brightness(1)}
}""",
    u"""/* P895: .die.card-reroll, its blue modifier and the settle deleted - three
   more box-shadow squares around a cube. They also drove `dRoll` on the chip,
   which is the flat path's spin and does nothing to a mesh; the dRoll
   keyframes themselves stay, they have seventeen other references. P828's
   point stands and is worth keeping in view if these come back through
   _fxMark: encore is starstone blue against powder keg's gold, and the
   modifier has to swap the whole animation, because keyframe box-shadows beat
   any static override. The classes are still added and removed; inert now. */""",
    '5 the card reroll rules')

# ══ 6. blind ════════════════════════════════════════════════════════
sub(u""".die.die-blind{background:#1a1a2a!important;color:transparent!important;border-color:#333!important;box-shadow:0 0 8px rgba(0,0,0,.6)!important;position:relative}
.die.die-blind::after{content:'?';position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:1.3em;font-weight:bold;color:rgba(180,180,200,.7);text-shadow:0 0 6px rgba(100,100,150,.4)}
.die.die-blind .pip{visibility:hidden!important}
.die.die-blind .inner-die{visibility:hidden!important}""",
    u"""/* P895: the blind rules deleted; blind is a roster row now ({id:'blind'}, a
   VEIL over the dice in this rule's own #1a1a2a). The background painted a
   dark square BEHIND the mesh rather than over the face, so it dimmed the gap
   between dice instead of the die; the '?' never painted (2812); and the two
   visibility rules hid pips that 2814 has already hidden in 3D. */""",
    '6 the blind rules')

# ══ 7. frozen ═══════════════════════════════════════════════════════
sub(u""".die.die-frozen{box-shadow:0 0 14px 4px rgba(100,180,255,.5),0 0 4px rgba(60,140,220,.3)!important;border-color:rgba(100,180,255,.7)!important;position:relative}
.die.die-frozen::before{content:'❄';position:absolute;top:-6px;right:-4px;font-size:10px;z-index:2;filter:drop-shadow(0 0 3px rgba(100,180,255,.8))}""",
    u"""/* P895: the frozen rules deleted; frozen is a roster row now ({id:'frozen'},
   a CRUST in this rule's own blue). The box-shadow was a square, and the ❄
   corner badge never painted (2812) - which §13 would have retired anyway: a
   glyph is centred on the hull at 40% of the die's width or it does not
   exist. The -mark and -entry rules below are different classes and stay. */""",
    '7 the frozen rules')

# ══ 8. kindred ══════════════════════════════════════════════════════
sub(u""".die.die-kindred{position:relative}
.die.die-kindred::after{
  content:'💀';position:absolute;top:-2px;right:-2px;font-size:10px;
  filter:drop-shadow(0 0 3px rgba(180,80,200,.8));pointer-events:none;
  animation:cfSkullFloat 2.6s ease-in-out infinite;
}
.die.die-kindred::before{
  content:'';position:absolute;inset:-4px;pointer-events:none;
  background:radial-gradient(circle at 50% 60%, rgba(180,80,220,.35) 0%, rgba(120,40,160,.18) 35%, transparent 70%);
  filter:blur(2px);
  animation:cfSmoke 3s ease-in-out infinite;
}
@keyframes cfSmoke{
  0%,100%{opacity:.5;transform:translateY(0) scale(1)}
  50%{opacity:.85;transform:translateY(-3px) scale(1.06)}
}
@keyframes cfSkullFloat{
  0%,100%{transform:translateY(0) rotate(-3deg)}
  50%{transform:translateY(-2px) rotate(3deg)}
}""",
    u"""/* P895: the kindred rules and their two keyframes deleted. Both pseudo
   elements were dead twice over - killed by 2812, and on a class no
   classList.add anywhere in the file ever writes. That second fact is the
   half of brief step 14 this settles: there was nothing to wire, only a
   decision to delete. cfSmoke and cfSkullFloat had no other user; cfBankPuff
   below does and stays, as does .die.die-palmed. */""",
    '8 the kindred rules')

# ── post-asserts. Comments stripped, so a tombstone cannot satisfy one ──
code = re.sub(r'/\*.*?\*/', '', s, flags=re.S)

# the roster: five rows, each new id exactly once
mk = code.index('MARKS:[')
roster = code[mk:code.index('\n  ],', mk)]
if roster.count("{id:'") != 5:
    sys.exit('the roster has %d rows, expected 5 (nothing written)'
             % roster.count("{id:'"))
for rid in ("frozen", "damp", "blind"):
    if roster.count("{id:'" + rid + "'") != 1:
        sys.exit('row %s is not present exactly once (nothing written)' % rid)
# and the predicate must read the chip, not a record field that does not exist
if '_frozen' in roster:
    sys.exit('a roster predicate reads d._frozen, which is undefined on a D3X '
             'record - it would paint nothing (nothing written)')

# every deleted selector is gone
for sel in ('.die.combo-glow', '.die.eff-glow-gold', '.die.eff-glow-green',
            '.die.eff-glow-red', '.die.eff-glow-blue', '.die.card-reroll',
            '.die.card-reroll-settle', '.die.die-frozen{', '.die.die-blind',
            '.die.die-dampened', '.die.die-kindred'):
    if sel in code:
        sys.exit('%s survived the deletion (nothing written)' % sel)
for kf in ('comboGlow', 'comboSheen', 'sawdustPoof', 'cardRerollPulse',
           'cardRerollSettle', 'cfSmoke', 'cfSkullFloat'):
    if '@keyframes ' + kf in code:
        sys.exit('@keyframes %s survived (nothing written)' % kf)

# NEIGHBOURS THAT MUST SURVIVE - each sits within a few lines of a deletion
for keep in ('.die.die-frozen-mark', '.die.die-frozen-entry', '.die-reveal',
             ':not(.die-frozen)', '@keyframes dRoll', '.die.die-palmed',
             '@keyframes cfBankPuff'):
    if keep not in code:
        sys.exit('%s was deleted and must not have been (nothing written)' % keep)

# the whole point of step 8 is that the file gets smaller
if len(s) >= before_len:
    sys.exit('the file did not shrink (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
print('file shrank by %d bytes' % (before_len - len(s)))
