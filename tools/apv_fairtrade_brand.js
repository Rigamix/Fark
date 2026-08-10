/* D10(a) - Fair Trade lends a die and neither brand travels.
 *
 * `use` writes `G.matchDice[p.lane]=p.borrowed` and never touches G._enchArr, so
 * for the length of the loan:
 *   - the HOST's brand stays on the seat, worn by the visiting die
 *   - the LENDER's brand (S.run.dieEnchInv, index-parallel to S.run.diceInv)
 *     stays inert in the stash
 * Denis ruled in OPEN section 9 that a brand travels WITH ITS DIE. A loan is the
 * same ruling with a return leg, so this needs a ledger like Trade's rather than
 * _dieLeftSeat's one-line clear - the host's brand has to come home.
 *
 * AND IT NEEDS D10(b) FIRST, which is why they land together: the loan record is
 * {lane, was, borrowed} and `borrowed` is a MATERIAL STRING. It cannot name
 * WHICH jade was lent, so there is no way to look up that die's brand. The fix
 * carries the stash INDEX.
 *
 * ARMS
 *   A  CONTROL - the loan actually happened (matchDice[lane] is the stash die).
 *      Everything below is a statement about brands on a seat that changed
 *      hands; if the trade silently refused, all of it reads clean.
 *   B  the lender's brand arrives with its die
 *   C  the host's brand is ledgered, not left on the seat
 *   D  the loan EXPIRES through the real startPTurn - the host's brand comes
 *      home with the host's die
 *   E  CONTROL - a lane the loan never touched keeps its brand throughout
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch(e){} await sleep(60); } return false; };
const vis = el => { if (!el || !el.isConnected) return false;
  const s = getComputedStyle(el), r = el.getBoundingClientRect();
  return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05 && r.width > 1 && r.height > 1; };
const tap = el => { if (!vis(el)) return false; const r = el.getBoundingClientRect();
  const o = {bubbles:true, cancelable:true, clientX:r.left+r.width/2, clientY:r.top+r.height/2};
  el.dispatchEvent(new PointerEvent('pointerdown',o)); el.dispatchEvent(new PointerEvent('pointerup',o));
  el.dispatchEvent(new MouseEvent('click',o)); return true; };

tap(document.getElementById('hsBtnBottom')); await sleep(1800);
await until(() => { const d = document.querySelector('.nrdie'); return d && d._floatDone; }, 9000);
tap(document.querySelector('.nrdie')); await sleep(1300);
tap(document.getElementById('nrTakeBtn')); await sleep(2200);
await until(() => [...document.querySelectorAll('.ptcard')].filter(vis).length > 0, 9000);
const pc = [...document.querySelectorAll('.ptcard')].filter(vis)[0]; if (pc) { tap(pc); await sleep(1700); }
const sit = [...document.querySelectorAll('span,div,button')].filter(e => vis(e) && e.children.length <= 1
  && /^SIT\s*DOWN$/i.test((e.textContent || '').trim()))[0];
if (sit) { tap(sit); if (sit.parentElement) tap(sit.parentElement); }
if (!(await until(() => vis(document.getElementById('screen-match')), 9000))
 || !(await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', 30000))) {
  return { skip: 'setup did not reach an idle match' };
}

const v = {}, notes = {};
const HOST = { t: 'ward', face: 5 }, LENT = { t: 'tithe', face: 1 }, OTHER = { t: 'seal', face: 3 };
const brandOf = e => (e && e.t) || null;

/* lane 0 is the weakest seat (bone) and therefore the one the picker takes;
   lane 5 is untouched throughout and is control E. */
G.matchDice = ['bone','flint','flint','flint','flint','flint'];
G._enchArr  = [HOST, null, null, null, null, OTHER];
G._fairTrade = null; G._ftDead = [];
G.phase = 'idle'; G.turnRollCount = 0;
try { S.run.diceInv = ['bone', 'starstone']; S.run.dieEnchInv = [null, LENT]; }
catch (e) { return { skip: 'no S.run to seed a stash' }; }

const picked = (CFX.fair_trade._pick && CFX.fair_trade._pick()) || null;
notes._pick = picked;
let used = false;
try { used = CFX.fair_trade.use({ id: 'fair_trade', tier: 1, state: {} }); }
catch (e) { notes._useErr = String(e).slice(0, 90); }

notes._afterUse = { used: used, matchDice: (G.matchDice || []).slice(0, 6),
                    brands: (G._enchArr || []).slice(0, 6).map(brandOf),
                    record: G._fairTrade ? Object.keys(G._fairTrade).reduce(function (o, k) {
                      o[k] = (G._fairTrade[k] && G._fairTrade[k].t) || G._fairTrade[k]; return o; }, {}) : null };

/* A - CONTROL: the loan happened at all */
v.theLoanActuallyHappened = used === true && G.matchDice[0] === 'starstone';

/* B - the lender's brand arrives with its die */
v.lentBrandArrivesWithTheDie = brandOf((G._enchArr || [])[0]) === 'tithe';

/* C - the host's brand is ledgered rather than left on the seat */
v.hostBrandIsLedgered = !!(G._fairTrade && G._fairTrade.hostEn && G._fairTrade.hostEn.t === 'ward');

/* D - expiry through the real startPTurn: the host's die and brand both return */
try { startPTurn(); } catch (e) { notes._expireErr = String(e).slice(0, 90); }
await sleep(900);
notes._afterExpiry = { matchDice: (G.matchDice || []).slice(0, 6),
                       brands: (G._enchArr || []).slice(0, 6).map(brandOf),
                       fairTrade: G._fairTrade };
v.loanExpiredAndTheDieCameBack = G.matchDice[0] === 'bone' && !G._fairTrade;   /* control */
/* WEAK ON ITS OWN, and flagged as such rather than trusted: pre-fix this key
   PASSES, because the host's ward never left the seat in the first place. A
   brand that never moved and a brand that made a correct round trip look
   identical at this instant. */
v.hostBrandComesHomeWithItsDie = brandOf((G._enchArr || [])[0]) === 'ward';
/* THE KEY THAT CANNOT PASS FOR THE WRONG REASON. It reads the seat at BOTH
   moments, so it is only true if the brand actually left with the lender's die
   and actually came back with the host's. */
v.brandMakesTheWholeRoundTrip = notes._afterUse.brands[0] === 'tithe'
                             && notes._afterExpiry.brands[0] === 'ward';

/* E - CONTROL: a lane the loan never touched, before and after */
v.untouchedLaneKeepsItsBrand = notes._afterUse.brands[5] === 'seal'
                            && notes._afterExpiry.brands[5] === 'seal';

for (const k of Object.keys(v)) { if (k[0] === '_') { notes[k] = v[k]; delete v[k]; } }
return { verdict: v, notes: notes };
