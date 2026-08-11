# -*- coding: utf-8 -*-
"""P619: the activation gets a sound of its own.

Denis's brief asked for "stronger glow, particles, sound" and the third was still
SFX.nav() - the generic UI click every button in the game uses. So the biggest
moment in the card system sounded exactly like tapping a menu.

BUILT FROM THE EXISTING PRIMITIVES, _tone and _click, like every other cue in
SFX. Both are already gated on _sfxOn(), so a muted player stays muted without
this having to know anything about settings.

THE SHAPE, and why each part is there:
  BODY   a short filtered noise push plus a low G - without it the sound is all
         sparkle and reads as thin rather than satisfying. This is the part that
         makes it land.
  BLOOM  G5 / D6 / G6 staggered 35ms apart. Stacked fifths and an octave, close
         enough together to read as ONE chord rather than an arpeggio - the
         "magical" half. It follows the file's own synergy() idiom, which builds
         its chord the same way.
  TAIL   seven detuned sparkles scattered over ~0.4s, which is the plume in
         sound: the particles are still in the air while these play. Kept under
         ~2.6kHz on purpose - _tone runs a 2400Hz lowpass, so anything higher is
         rolled off and would just be wasted voices.

TIMED AHEAD OF THE EFFECT. activateCard often calls triggerCard, which plays
cardTrigger() - so this deliberately front-loads its attack and lets the bloom
ring UNDER that, giving cast-then-effect rather than two clicks on top of each
other.
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


sub(u"  cardTrigger(){this._tone(540,'sine',0.05,0.005,0.12);"
    u"this._tone(810,'sine',0.03,0.003,0.09,0.03);this._click(1400,0.025,0.03,0.01);},",
    u"  cardTrigger(){this._tone(540,'sine',0.05,0.005,0.12);"
    u"this._tone(810,'sine',0.03,0.003,0.09,0.03);this._click(1400,0.025,0.03,0.01);},\n"
    u"  /* P619: THE CARD FIRES. The release beat had only SFX.nav() - the same\n"
    u"     click as every menu button - so the biggest moment in the card system\n"
    u"     sounded like navigation.\n"
    u"     BODY so it lands, BLOOM so it is magical, TAIL so it matches the plume\n"
    u"     still in the air. The bloom is a stacked fifth and octave 35ms apart,\n"
    u"     close enough to read as one chord rather than an arpeggio - the same way\n"
    u"     synergy() builds its. Sparkles stay under ~2.6kHz because _tone runs a\n"
    u"     2400Hz lowpass and anything above it is only wasted voices.\n"
    u"     Front-loaded on purpose: activateCard usually calls triggerCard right\n"
    u"     after, so this attacks first and rings underneath rather than colliding. */\n"
    u"  cardFire(){\n"
    u"    /* body - the push that makes it satisfying rather than thin */\n"
    u"    this._click(300,0.075,0.055);\n"
    u"    this._tone(196,'sine',0.055,0.006,0.22);\n"
    u"    /* bloom - G5 / D6 / G6, one chord */\n"
    u"    this._tone(784,'sine',0.075,0.004,0.28);\n"
    u"    this._tone(1175,'sine',0.048,0.003,0.26,0.035);\n"
    u"    this._tone(1568,'sine',0.032,0.003,0.24,0.07);\n"
    u"    /* tail - the particles, in sound */\n"
    u"    for(let i=0;i<7;i++){\n"
    u"      const t=0.09+i*0.05+Math.random()*0.03;\n"
    u"      this._tone(1500+Math.random()*1000,'sine',0.019,0.002,0.10,t);\n"
    u"      if(i%2===0)this._click(2200+Math.random()*700,0.012,0.028,t);\n"
    u"    }\n"
    u"  },",
    'P619 SFX.cardFire')

sub(u"function _commitActivation(mcardEl,cardId,savedState){\n"
    u"  SFX.nav();",
    u"function _commitActivation(mcardEl,cardId,savedState){\n"
    u"  /* P619: the card's own sound, not the menu click this used to borrow */\n"
    u"  try{SFX.cardFire();}catch(e){try{SFX.nav();}catch(e2){}}",
    'P619 wire it to the release')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits applied' % n)
