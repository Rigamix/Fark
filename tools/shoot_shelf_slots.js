/* PHOTOGRAPH THE SHELF'S THREE CARD SLOTS AGAINST THE CARDS SITTING IN THEM.
 *
 * Denis: "In the Shelf screen, there are 3 areas for the cards to sit in. If you
 * look at the art you can see those are drawn with a perspective, but the cards
 * are sitting straight with no perspective on them. Fix that."
 *
 * The slots are painted into FK_ART.shelfBg; the cards are .loCard, absolutely
 * placed at three hard-coded points with `transform:translate(-50%,-50%)` and
 * nothing else. So there is no perspective on them by construction - but WHAT
 * perspective the painting asks for cannot be read out of the CSS, only off the
 * image. Hence a photograph rather than a measurement.
 *
 * THE HAND IS FORCED to three cards. S.run.fcards is empty on a fresh save and
 * an empty shelf shows the slots with nothing in them - which is half the
 * comparison Denis is making. Three real cards, through the real renderer.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch(e){} await sleep(60); } return false; };

if (typeof famLoadoutShow !== 'function') return { err: 'famLoadoutShow missing' };
try { _getS(); } catch (e) { return { err: '_getS threw: ' + e }; }
if (!S || !S.run) return { err: 'no run' };

const ids = FAM_CARDS.filter(c => c.fam !== 'tavern').slice(0, 3).map(c => c.id);
S.run.fcards = ids.map(id => ({ id, tier: 1 }));
famLoadoutShow();
if (!await until(() => document.querySelectorAll('#loStage .loCard').length === 3, 8000))
  return { err: 'shelf cards never rendered' };
await sleep(1400);

const stage = document.getElementById('loStage');
const sr = stage.getBoundingClientRect();
const cards = [...document.querySelectorAll('#loStage .loCard')].map(el => {
  const r = el.getBoundingClientRect();
  return { cid: el.dataset.cid,
           /* as a % of the stage, so the numbers survive a viewport change */
           leftPct: +(((r.left - sr.left) / sr.width) * 100).toFixed(2),
           topPct:  +(((r.top  - sr.top ) / sr.height) * 100).toFixed(2),
           wPct:    +((r.width / sr.width) * 100).toFixed(2),
           hPct:    +((r.height / sr.height) * 100).toFixed(2),
           transform: getComputedStyle(el).transform };
});

return {
  arm: 'photo',
  control: { cardsRendered: cards.length },
  stage: { w: +sr.width.toFixed(1), h: +sr.height.toFixed(1) },
  shelfBg: (typeof FK_ART !== 'undefined' && FK_ART.shelfBg) || null,
  /* the three placements, as authored */
  cards,
  /* every card wears the identical matrix today — that is the finding, stated
     as data rather than as a claim about the CSS */
  distinctTransforms: [...new Set(cards.map(c => c.transform))],
};
