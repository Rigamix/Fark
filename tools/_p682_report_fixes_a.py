# -*- coding: utf-8 -*-
"""P682: the behaviour half of the seventeen-notes findings.

Every change here implements a MEASURED finding from the investigation pass
(eleven parallel probes, reports in the workflow journal), not a guess.

1. GROG SPOKE PATRON LINES - confirmed live: the getLine wrapper routes
   bosses through the patron/trait layer, and window._lastSeatArt/_lastSeatTrait
   are written only by launchSeat and never cleared, so a boss match speaks
   the PREVIOUS PATRON's lines (probe: Mudge's gossip out of GROG's mouth,
   and the absent patron's story arc advanced and saved). Bosses now return
   to their own bespoke barks (_orig) before the lore layer runs, and
   launchBossMatch clears the stale seat globals.

2. SHORT LINES WRAPPED - "Small bank's still a bank." set on two lines
   because scrollWidth rounds a fractional 190.4px UP (191) while clientWidth
   rounds it DOWN (190), so the single-line early-return never fired. One px
   of rounding slack ends the coin-flip for every short line.

3. BUBBLE ANIMATION - the fade (.5s, on the box) and the scale (.34s, on the
   scroll) were on different elements with mismatched durations - the scale
   completes while the box is still 30% transparent and the tail is a pure
   crossfade, exactly what Denis described. One duration (.34s) for both, a
   deeper start (.72 -> .55) so motion carries the entrance, and the dead
   `opacity .3s` term (nothing ever changes scroll opacity) goes.

4. PHONE TEXT SAT LOW - the scroll's padding was fixed px (25/26/19) while
   the text is container-relative, so on a phone the padding is over half the
   bubble and the 6px deliberate sink reads huge. Padding goes container-
   relative (same numbers at the 430 design width) and the sink drops to ~2px.

5. MUSIC DROPPED "FOR NO REASON" - Dead Air: when either side reaches 85% of
   target the music ducks to 22% and NEVER restores until the match ends.
   Measured 0.07 -> 0.0154. The duck goes; the vignette and drone stay - they
   are legible tension, a permanent volume cut is not. Also: entering a boss
   match when the boss track's gain never attached (autoplay refusal) faded
   the tavern to zero with nothing ramping up - total dropout; the fade-out
   now only runs when the boss layer can actually come up.

6. OLD DICE SHOWED FIRST - D3X (the real dice) boots lazily and nothing
   boots it until the FIRST MATCH ROLL; the new-run offer never boots it at
   all, so the first dice a player ever sees are the old CSS cubes. A warm
   boot at load (idle callback; boot is idempotent and its failure path is
   the deliberate DOM-dice fallback) plus a boot at the offer builder.

7. WIN-SCREEN BOTTOM UI - measured ~2.0-2.2s from winning tap to actionable
   bottom UI: 700-900ms bank->endMatch defer + _DRAFT_DELAY 1300/1800. The
   draft delay drops to 500/500/900 - the bottom lands right after the
   scores fade instead of half a second later. (Third complaint; P635 and
   P659 each halved it, this one puts the bottom inside the same breath as
   the scores.)
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
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:130]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ── 1. bosses speak only their own lines ────────────────────────────────
sub(u"    var _orig=DLG.getLine.bind(DLG);\n"
    u"    DLG.getLine=function(cat){\n"
    u"      try{",
    u"    var _orig=DLG.getLine.bind(DLG);\n"
    u"    DLG.getLine=function(cat){\n"
    u"      /* P682: A BOSS IS NOT A PATRON. Measured: in a GROG match this wrapper\n"
    u"         served the PREVIOUS patron's lines - _lastSeatArt/_lastSeatTrait are\n"
    u"         written only by launchSeat and were never cleared - and the\n"
    u"         _DLG_PERSONAL branch even advanced that absent patron's story arc\n"
    u"         and saved it. Bosses go straight to their own bespoke barks. */\n"
    u"      if(typeof G!=='undefined'&&G&&G._isBoss)return _orig(cat);\n"
    u"      try{",
    'P682 boss guard')

sub(u"function launchBossMatch(){\n"
    u"  _getS();",
    u"function launchBossMatch(){\n"
    u"  _getS();\n"
    u"  /* P682: the stale-seat hygiene half of the same fix */\n"
    u"  window._lastSeatArt=null;window._lastSeatTrait=null;",
    'P682 boss clears seat globals')

# ── 2. the rounding slack ───────────────────────────────────────────────
sub(u"  if (natural <= maxW) return natural;",
    u"  /* P682: scrollWidth rounds a fractional width UP and clientWidth rounds\n"
    u"     it DOWN, so a 190.4px line read as 191>190 and wrapped. One px of\n"
    u"     slack ends the coin-flip for every short line. */\n"
    u"  if (natural <= maxW + 1) return natural;",
    'P682 fit rounding slack')

# ── 3. one animation, not scale-then-crossfade ──────────────────────────
sub(u"  pointer-events:none;opacity:0;transition:opacity .5s ease;",
    u"  /* P682: .5s -> .34s, matching the scroll's scale - they were mismatched\n"
    u"     durations on different elements, which is the scale-stops-then-\n"
    u"     crossfade wonk Denis described */\n"
    u"  pointer-events:none;opacity:0;transition:opacity .34s ease;",
    'P682 fade matches scale')

sub(u"#screen-match .dlg-scroll{scale:.72;transition:scale .34s cubic-bezier(.2,1.3,.35,1),opacity .3s ease}",
    u"/* P682: .72 -> .55 so the motion carries the entrance; the dead `opacity\n"
    u"   .3s` term went with it (nothing ever changes the scroll's own opacity) */\n"
    u"#screen-match .dlg-scroll{scale:.55;transition:scale .34s cubic-bezier(.2,1.3,.35,1)}",
    'P682 deeper scale, dead term gone')

# ── 4. the padding scales with the phone ────────────────────────────────
sub(u"  box-shadow:none;padding:25px 26px 19px;max-width:99%;margin:0 0 0 3cqw;flex:0 1 auto;",
    u"  /* P682: container-relative - the fixed 25/26/19px was over HALF the\n"
    u"     bubble on a phone while everything else scaled, which is why the text\n"
    u"     sat low there and not on desktop. Same numbers at the 430 design width,\n"
    u"     sink trimmed to ~2px. */\n"
    u"  box-shadow:none;padding:5.4cqw 6cqw 4.6cqw;max-width:99%;margin:0 0 0 3cqw;flex:0 1 auto;",
    'P682 padding goes cqw')

# ── 5. the music stops vanishing ────────────────────────────────────────
sub(u"    var duck=on?0.22:1;",
    u"    /* P682: NO MUSIC DUCK. The 22% cut fired when EITHER side hit 85% of\n"
    u"       target and never restored until the match ended - measured 0.07 ->\n"
    u"       0.0154 for the rest of the match, which is Denis's \"volume drops for\n"
    u"       no reason\". The vignette and the drone stay; they read as tension.\n"
    u"       A permanent volume cut does not. */\n"
    u"    var duck=1;",
    'P682 dead-air duck goes')

sub(u"    try{if(BG_BOSS.audio){BG_BOSS.audio.currentTime=0;}}catch(e){}\n"
    u"    _fadeGain(BG_TAVERN.gain,0,BG_FADE_MS);\n"
    u"    _fadeGain(BG_BOSS.gain,BG_BOSS_VOL,BG_FADE_MS);",
    u"    try{if(BG_BOSS.audio){BG_BOSS.audio.currentTime=0;}}catch(e){}\n"
    u"    /* P682: fade the tavern out ONLY if the boss layer can come up - with\n"
    u"       BG_BOSS.gain unattached (autoplay refusal) the old order faded the\n"
    u"       tavern to zero against silence: total music dropout at boss entry. */\n"
    u"    if(BG_BOSS.gain){\n"
    u"      _fadeGain(BG_TAVERN.gain,0,BG_FADE_MS);\n"
    u"      _fadeGain(BG_BOSS.gain,BG_BOSS_VOL,BG_FADE_MS);\n"
    u"    }",
    'P682 no boss-entry dropout')

# ── 6. the real dice wake up early ──────────────────────────────────────
sub(u"      if(window.D3X&&D3X.chipAnim)D3X.chipAnim(hd,{delay:i*200+330,dur:1000,roll:20,breathe:true});",
    u"      /* P682: the offer is the one dice surface that could never boot D3X -\n"
    u"         the first dice a player ever sees were the old CSS cubes every time */\n"
    u"      try{if(window.D3X&&D3X.boot)D3X.boot();}catch(e){}\n"
    u"      if(window.D3X&&D3X.chipAnim)D3X.chipAnim(hd,{delay:i*200+330,dur:1000,roll:20,breathe:true});",
    'P682 offer boots D3X')

sub(u"  window.DLG=DLG;\n"
    u"})();",
    u"  window.DLG=DLG;\n"
    u"})();\n"
    u"/* P682: WARM BOOT for the real dice. D3X loaded lazily and nothing booted it\n"
    u"   until the first match roll, so the old CSS cubes always rendered first and\n"
    u"   the swap popped mid-roll. boot() is idempotent, and its failure path is\n"
    u"   the deliberate DOM-dice fallback, so a bad device loses nothing. */\n"
    u"(function(){\n"
    u"  function warm(){try{if(window.D3X&&D3X.boot)D3X.boot();}catch(e){}}\n"
    u"  window.addEventListener('load',function(){\n"
    u"    if(window.requestIdleCallback)requestIdleCallback(warm,{timeout:2500});\n"
    u"    else setTimeout(warm,600);\n"
    u"  });\n"
    u"})();",
    'P682 load-time warm boot')

# ── 7. the bottom UI lands with the scores ──────────────────────────────
sub(u"var _DRAFT_DELAY={bossWin:1300,patronWin:1300,loss:1800};",
    u"/* P682: third complaint about this number. Measured end-to-end: 700-900ms\n"
    u"   bank beat + this = 2.0-2.2s to an actionable bottom. 500 puts the cards\n"
    u"   inside the same breath as the scores fading in. */\n"
    u"var _DRAFT_DELAY={bossWin:500,patronWin:500,loss:900};",
    'P682 draft delay drops')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
