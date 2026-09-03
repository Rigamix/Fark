/* A STANDING CHECK THAT THE TWO PRICE HOMES AGREE.
 *
 * Silver's price lived in three places and P931 moved one, so the shop sold at
 * 120 while the die def and the economy model both said 320 - and the file had
 * a comment two lines above the one I missed saying all three had to move
 * together. A note asking future authors to keep copies in step is the thing
 * that fails; P939 collapsed the model's table into a read of DICE_STORE, and
 * this asserts the remaining two agree.
 *
 * TWO HOMES REMAIN BECAUSE THEY HOLD DIFFERENT THINGS - a shop row is price,
 * stock and label, a die definition is faces, effect and cost. Merging them is a
 * bigger refactor than a price ruling should carry. So the duplication stays and
 * the check fails the day one moves alone.
 *
 * Node only, no browser: it reads the file.
 */
const fs = require('fs'), path = require('path');
const src = fs.readFileSync(path.join(__dirname, '..', 'fark_proto.html'), 'utf8');

const store = {};
const storeBlock = src.slice(src.indexOf('var DICE_STORE=['));
for (const m of storeBlock.slice(0, storeBlock.indexOf('\n];')).matchAll(
       /\{mat:'(\w+)',\s*price:(\d+),/g)) store[m[1]] = +m[2];

const defs = {};
for (const m of src.matchAll(/\{id:'(\w+)',name:'[^']*',icon:'[^']*',cost:(\d+),/g))
  defs[m[1]] = +m[2];

let bad = 0, checked = 0;
for (const mat of Object.keys(store)) {
  if (!(mat in defs)) continue;           /* not every shop row is a die def */
  checked++;
  if (store[mat] !== defs[mat]) {
    bad++;
    console.log('  MISMATCH %s: DICE_STORE price %d vs DICE_TYPES cost %d',
      mat, store[mat], defs[mat]);
  }
}
/* AND THE MODEL MUST NOT HOLD ITS OWN COPY. P939 made FAM_PRICE read
   DICE_STORE; a literal reappearing there is the third home coming back. */
const fp = src.slice(src.indexOf('var FAM_PRICE='), src.indexOf('var FAM_PRICE=') + 400);
const relit = /\b(amber|silver|obsidian|starstone|jade2?|vagabond)\s*:\s*\d/.test(fp);
if (relit) { bad++; console.log('  FAM_PRICE has price literals again - the third home is back'); }

console.log('%s  %d shop rows checked against die defs, %d mismatched%s',
  bad ? 'FAILED' : 'PASS', checked, bad, relit ? ', FAM_PRICE re-literalised' : '');
process.exit(bad ? 1 : 0);
