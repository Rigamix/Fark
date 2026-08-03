/* apv_font_metrics — did the face swap break any type?
 *
 * P441 moved 159 declarations from Alagard (a pixel font) to JMH Beda (a
 * blackletter). Every size and letter-spacing in the game was tuned against
 * Alagard's metrics. A different face does not occupy the same box at the same
 * numbers, so somewhere in the game text now overflows its container or clips.
 *
 * EYEBALLING SIX SCREENSHOTS WOULD NOT FIND THIS RELIABLY. Clipped text looks
 * like short text, and a one-pixel overflow looks like nothing at all. So this
 * MEASURES: for every element rendering in the new face, scrollWidth against
 * clientWidth and scrollHeight against clientHeight. Overflow is arithmetic,
 * not a judgement call.
 *
 * WHY IT WALKS THE SCREENS. Inactive screens are display:none, and a hidden
 * element reports zero for every box metric — measuring the page as loaded
 * would return a clean sheet having looked at one screen. So it activates each
 * screen in turn and measures what is actually laid out.
 *
 * WHAT IT CANNOT SEE, stated so the PASS is not read as more than it is:
 * overlays and modals that only exist mid-match (the rules sheet, the pause
 * card, the win banner) are not reachable from a cold menu, and text that is
 * merely UGLY at the new metrics — too tight, too loose, sitting wrong against
 * its frame — overflows nothing and will not appear here. Those need eyes.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));

const SCREENS = ['menu', 'gauntlet', 'shop', 'draft', 'bossreward', 'gameover'];
const rows = [];
const errs = [];

function measure(where) {
  const out = [];
  document.querySelectorAll('.screen.active *').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) return;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return;
    /* THE ELEMENT THAT RENDERS THE GLYPHS, not everything that inherits the
       family. The first run of this probe asked only "does this compute to
       Beda", which is true of every descendant of <body> - so it returned
       .d3die, .d3slot and .die, dice with no text at all, whose overflow is 3D
       transform work and was there before the font existed. It also returned
       #stStage and #goGameOver, whole-screen containers whose scroll height is
       page layout. Neither can be damaged by a typeface.
       An element is only a type-damage candidate if it has its OWN text nodes:
       that is the box the glyphs are actually laid into, and the only box a
       font change can overflow. */
    const own = [].slice.call(el.childNodes)
      .filter(n => n.nodeType === 3)
      .map(n => n.textContent.trim()).join(' ').trim();
    if (!own) return;
    /* BOTH FACES, because this probe has to run against the PRE-PATCH file too.
       Filtering on /Beda/ would return an empty set on the baseline and make
       the diff meaningless - zero hits before, some hits after, "the font
       broke it". The population has to be the same on both sides: everything
       that sits on the migrated variable, whichever face it currently holds. */
    if (!/Beda|Alagard|Press Start/i.test(cs.fontFamily)) return;
    /* a scrollable container overflowing is its JOB, not damage */
    if (cs.overflowX === 'auto' || cs.overflowX === 'scroll' ||
        cs.overflowY === 'auto' || cs.overflowY === 'scroll') return;
    const ox = el.scrollWidth - el.clientWidth;
    const oy = el.scrollHeight - el.clientHeight;
    /* 1px is rounding, not overflow */
    if (ox > 1 || oy > 1) {
      const txt = own.replace(/\s+/g, ' ').slice(0, 38);
      out.push({
        where: where,
        sel: el.id ? '#' + el.id : '.' + (el.className || '').split(' ')[0],
        ox: ox, oy: oy,
        size: cs.fontSize, ls: cs.letterSpacing,
        face: /Beda/i.test(cs.fontFamily) ? 'beda' : 'old',
        clipped: cs.overflow === 'hidden' || cs.overflowX === 'hidden' ||
                 cs.textOverflow === 'ellipsis',
        txt: txt
      });
    }
  });
  return out;
}

for (const name of SCREENS) {
  try {
    showScreen(name);
    await sleep(700);
    const hits = measure(name);
    rows.push({ screen: name, overflow: hits.length });
    hits.forEach(h => errs.push(h));
  } catch (e) {
    rows.push({ screen: name, overflow: -1, err: String(e).slice(0, 70) });
  }
}

/* how much of the game is even in the new face? a PASS on a screen that never
   adopted the font is not a pass on anything. */
showScreen('menu');
await sleep(300);
let beda = 0, other = 0;
document.querySelectorAll('*').forEach(el => {
  const f = getComputedStyle(el).fontFamily || '';
  if (/Beda/i.test(f)) beda++;
  else if (/Alagard|Press Start/i.test(f)) other++;
});

/* RETURN, do not console.log. shoot.js prints the eval's RETURN VALUE as
   `setup:`; console.log goes to the page's own console, which shoot.js only
   surfaces for errors. The first run of this probe logged everything and
   printed nothing, and an empty result reads exactly like a clean sheet. */
return {
  rows: rows, bedaEls: beda, oldFontEls: other,
  overflow: errs.slice(0, 40),
  /* THE VERDICT IS ABOUT CHANGE, NOT ABOUT ZERO. Five elements overflow by
     2-3px: .nm on the gauntlet and four .golo-val on game over. All five were
     measured on the PRE-PATCH file too and all five were already JMH Beda
     before the migration - they are a Beda ascender sitting 2px proud of a
     fixed-height box, not damage this pass caused. A probe that goes red on a
     known, measured, non-regressing condition is a probe the next person
     learns to ignore, which costs more than the 2px.
     EXACT, not a ceiling: 5 is what the baseline had, so a sixth trips it. A
     `<= 5` would pass a genuinely new overflow the moment an old one was
     fixed. */
  verdict: {
    overflowUnchanged: errs.length === 5,
    noClipped: errs.filter(e => e.clipped).length === 0,
    oldFontGone: other === 0,
    screensMeasured: rows.filter(r => r.overflow >= 0).length === SCREENS.length
  }
};
