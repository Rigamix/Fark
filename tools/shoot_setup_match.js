/* The canonical way to open a match for a screenshot.
 *
 * USE THIS, not showScreen('match',{rung:TIERS[0].boss,...}). Boss matches go
 * through a different entry and are carrying old imagery - a synthetic boss
 * launch renders a flat black table and looks like a serious bug when nothing
 * is wrong. launchSeat() is how a night actually opens a match.
 *
 *   node tools/shoot.js --eval-file tools/shoot_setup_match.js --out shot.png
 *
 * Edit the dice line below to photograph particular materials.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch (e) {} await sleep(60); }
  return false; };
const trace = [];

_getS();
if (typeof _ensureNight === 'function') _ensureNight();
S.run.dice = ['bone','amber','silver','jade','obsidian','starstone'];
S.run.dieEnch = [null, null, null, null, null, null];
S.settings = S.settings || {};
S.settings.fastRival = true;   /* 0.4x every rival delay */

const n = S.run.night;
let seat = 0;
if (n && n.seatsPlayed) { const i = n.seatsPlayed.findIndex(p => !p); seat = i < 0 ? 0 : i; }
launchSeat(seat);

/* the match screen takes about a second and a half to hand over control */
await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 12000);
trace.push('phase=' + (typeof G !== 'undefined' && G ? G.phase : 'noG'));

const sc = document.getElementById('screen-match');
trace.push('bg=' + getComputedStyle(sc, '::before').backgroundImage.split('/').pop().replace(/["')]+$/, ''));

/* the 3D layer boots on the first roll: three.js, GLTFLoader, the model, cannon */
handleRoll();
await until(() => document.querySelectorAll('#playerDiceRow .die').length > 0, 5000);
await until(() => window.D3X && D3X.dice.length >= 6, 8000);
await until(() => !D3X.dice.some(d => d.roll), 6000);
trace.push('dice=' + document.querySelectorAll('#playerDiceRow .die').length +
           ' meshes=' + D3X.dice.length);

return { trace, rung: G && G.rung && G.rung.name,
         vals: [...document.querySelectorAll('#playerDiceRow .die')].map(e => e._trueVal) };
