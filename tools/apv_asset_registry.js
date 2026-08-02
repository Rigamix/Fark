/* FK_ART — EVERY ENTRY MUST RESOLVE, AND THE CONSTANTS MUST COME FROM IT.
 *
 * The registry's whole value is being trustworthy enough that someone writes
 * `FK_ART.coin` instead of guessing a path. Two ways that fails silently:
 *
 *   1. AN ENTRY ROTS. Art gets reorganised, the registry keeps the old path,
 *      and now the one place people trust is the one place that lies. Every
 *      entry is fetched — directories included — rather than eyeballed.
 *   2. IT DRIFTS OUT OF USE. A registry the code does not read is a comment.
 *      The thirteen prefix constants were rewired to read from it; this checks
 *      they still do, by comparing the live constant to the live entry. If
 *      someone re-hardcodes `var PT_P='Art/Assets/...'`, the values still match
 *      and this would pass — so it also greps the served source for the
 *      re-hardcoding, which is the actual failure mode.
 *
 * The font entry is not a path and is checked as a font: declared, and
 * reachable as some element's first-choice family. */
const out = { entries: {}, dead: [], notes: [] };

if (typeof FK_ART === 'undefined') { return { err: 'FK_ART is not defined' }; }

const keys = Object.keys(FK_ART);
out.entryCount = keys.length;

await Promise.all(keys.map(async k => {
  const v = FK_ART[k];
  if (k === 'font') return;                       /* checked separately below */
  try {
    /* Directories are fetched too. A dev server answers a directory with a
       listing and a missing one with 404, so the check is the same shape for
       both and a deleted folder cannot hide behind "it's only a prefix". */
    const r = await fetch(v, { method: 'GET' });
    out.entries[k] = { path: v, status: r.status, ok: r.ok };
    if (!r.ok) out.dead.push(k + ' -> ' + v + ' (' + r.status + ')');
  } catch (e) {
    out.entries[k] = { path: v, status: 'ERR', ok: false };
    out.dead.push(k + ' -> ' + v + ' (' + e.message + ')');
  }
}));

/* ── the font entry ── */
out.font = { declared: FK_ART.font };
try {
  const fam = String(FK_ART.font).replace(/['"]/g, '').trim();
  await document.fonts.ready;
  out.font.family = fam;
  out.font.faceDeclared = [...document.fonts].some(f => f.family === fam);
  /* reachable = some element resolves to it FIRST, which is the claim that
     matters: a declared face nothing uses is the Metamorphous case */
  let reach = 0;
  for (const el of document.querySelectorAll('*')) {
    let ff = ''; try { ff = getComputedStyle(el).fontFamily || ''; } catch (e) { continue; }
    if (ff.split(',')[0].replace(/['"]/g, '').trim() === fam) reach++;
  }
  out.font.elementsUsingIt = reach;
} catch (e) { out.notes.push('font: ' + e.message); }

/* ── are the constants still fed by the registry? ── */
/* ONLY THE TOP-LEVEL ONES. Seven of the thirteen rewired constants are `var`s
   inside a function (NR, BG, HS/BT/IC, PP, ST, LO/HRT, BTP) and simply are not
   in scope here — the first run of this check reported NR as "not reading the
   registry" when the real answer was "cannot be seen from page scope", which
   is a different fact and would have sent someone looking for a bug that is
   not there. The source-grep below is what covers those seven: it catches a
   re-hardcoded `var NR='Art/...'` wherever it lives. */
const WIRED = { PT_P:'patronFrames', PT_CHAR:'patronChars',
                PT_TRAITDIR:'traits', PT_A:'mockups', ENCH_ICON_DIR:'enchIcons' };
const WIRED_SCOPED = ['NR','BG','HS','BT','IC','PP','ST','LO','HRT','BTP'];
out.constants = {};
Object.keys(WIRED).forEach(name => {
  let live; try { live = eval(name); } catch (e) { live = '(not in scope)'; }
  out.constants[name] = { value: live, expects: FK_ART[WIRED[name]],
                          matches: live === FK_ART[WIRED[name]] };
});

/* and nobody has quietly re-hardcoded one */
out.rehardcoded = [];
try {
  const src = document.documentElement.outerHTML;
  Object.keys(WIRED).concat(WIRED_SCOPED).forEach(name => {
    /* a literal on the right-hand side is the re-hardcoding; `=FK_ART.x` is not */
    if (new RegExp('var\\s+' + name + "\\s*=\\s*['\"]").test(src)) out.rehardcoded.push(name);
  });
} catch (e) { out.notes.push('source scan: ' + e.message); }

out.verdict = {
  everyEntryResolves:   out.dead.length === 0,
  fontFaceDeclared:     out.font.faceDeclared === true,
  fontActuallyUsed:     (out.font.elementsUsingIt || 0) > 0,
  constantsReadRegistry: Object.keys(out.constants).every(k => out.constants[k].matches),
  noneRehardcoded:      out.rehardcoded.length === 0
};
return out;
