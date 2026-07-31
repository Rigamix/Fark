/* EVERY PROP'S REAL ASPECT, and how wrong the shadow angle is without it.
 *
 * The shadow direction is computed from the prop's CENTRE minus the light
 * centre. The centre is estimated as q.y + w*(a[1]/a[0])*0.26, where `a` comes
 * from a hand-written ASPECT table - and any prop missing from that table falls
 * back to [1,1]. A wrong assumed centre rotates the shadow off the radial line,
 * which is exactly the rule it is supposed to obey.
 *
 * So: measure every prop's true pixel size, then compute the angle the shadow
 * is drawn at today versus the angle it should be drawn at, for the props
 * actually on the table. */
const PP = 'Art/Assets/Match/Commoner/Props/';
const NAMES = ['bag','bottle','bottle01','bottle02','bowl_dirty','bowl_full','bread','candle',
  'cauldron','cheese','coins','cork','fork','grapes','jug','key','knife','lantern','loaf',
  'mug01','mug_empty','olives','package','plank','plateMetal','plateWood','pouch','pouch02',
  'pouch03','sausages','singleCoin','singleCoin_02','spoon','towel','towel01','towel02',
  'ustensils','wine'];

const size = {}, missing = [];
for (const n of NAMES){
  try{
    const im = new Image();
    await new Promise((res, rej) => { im.onload = res; im.onerror = () => rej(new Error('404')); im.src = PP + n + '.png?v=2'; });
    size[n] = [im.naturalWidth, im.naturalHeight];
  }catch(e){ missing.push(n); }
}

/* the two things the game needs */
const out = { count: Object.keys(size).length, missing };
out.aspectTable = Object.keys(size).sort().map(n => n + ':[' + size[n][0] + ',' + size[n][1] + ']').join(',');

/* how wrong is today's angle, for the props on the current table? */
const LIGHT = window.FK_LIGHT || {cx:0.50, cy:0.52};
/* FK_PROP_PIN is only assigned while a match renders, so asking for it here
   silently fell back to template [0] - which is 001, every prop of which
   happens to BE in the old ASPECT table. That is why this never showed up:
   the old dressing could not trigger the bug. Measure every template. */
const ALL_TPL = (window.FK_PROP_TEMPLATES||[]);
const OLD_ASPECT = {bottle:[349,483],bread:[440,312],candle:[379,400],cheese:[432,344],
    coins:[359,277],jug:[329,413],mug01:[365,368],mug_empty:[396,357],
    olives:[388,361],package:[446,368],pouch:[302,381],pouch02:[447,384],
    singleCoin:[247,206],spoon:[431,283],towel:[491,372]};

function dirFor(q, aspect){
  const a = aspect[q.n] || [1,1];
  const cx = q.x + q.w/2, cy = q.y + q.w*(a[1]/a[0])*0.26;
  const dx = cx - LIGHT.cx*100, dy = (cy - LIGHT.cy*100)*1.9;
  const len = Math.hypot(dx, dy) || 1;
  return { ux: dx/len, uy: dy/len, deg: Math.atan2(dy/len, dx/len)*180/Math.PI, cy: cy };
}

function anglesFor(tpl){ return (tpl ? tpl.props : []).map(q => {
  const now = dirFor(q, OLD_ASPECT);
  const real = dirFor(q, size);
  let d = now.deg - real.deg;
  while (d > 180) d -= 360; while (d < -180) d += 360;
  return { n: q.n, inTable: !!OLD_ASPECT[q.n],
           nowDeg: +now.deg.toFixed(1), trueDeg: +real.deg.toFixed(1),
           errDeg: +d.toFixed(1) };
}); }
out.byTemplate = ALL_TPL.map(t => {
  const A = anglesFor(t);
  const bad = A.filter(x => Math.abs(x.errDeg) >= 1);
  return { name: t.name, props: A.length,
           missingFromTable: A.filter(x => !x.inTable).length,
           offRadial: bad.length,
           maxErrDeg: A.reduce((m,x) => Math.max(m, Math.abs(x.errDeg)), 0).toFixed(1),
           worst: bad.sort((a,b)=>Math.abs(b.errDeg)-Math.abs(a.errDeg)).slice(0,6)
                     .map(x => x.n+' '+x.errDeg+'°') };
});
return out;
