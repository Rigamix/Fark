/* PNG -> WebP with no toolchain, for any art folder.
 *
 * There is no cwebp or ImageMagick on this machine, but there is a headless
 * browser, and a browser is a very good image encoder: draw the PNG to a canvas
 * and ask for image/webp. Returns data URLs; the caller decodes them to disk, so
 * the bytes never travel any further than the pipe.
 *
 * Output goes to <that folder>/optimized/ as <Name>_opt.webp, which is
 * this project's established art pipeline - every other art folder has one and
 * the game loads from them directly. The masters beside it are never touched.
 * Re-run this whenever the source art changes.
 *
 *   node tools/shoot.js --eval-file tools/webp_gameover.js --out /dev/null \
 *     | python <decode the setup: line>
 */
const JOBS = [
  /* the two family cards that had no art. The masters are camelCase
     (card_face_steadyHand.png) where every other card is snake_case, so the
     output name is stated explicitly rather than derived - the GAME loads
     assets/cards/<card id>.webp, and the ids are steady_hand and fair_trade. */
  { dir: 'Art/Assets/Cards/Silver/', files: [
    ['card_face_steadyHand.png', 0.88],
    ['card_face_FairTrade.png', 0.88] ] },
];

const load = src => new Promise((res, rej) => {
  const im = new Image();
  im.onload = () => res(im);
  im.onerror = () => rej(new Error('load failed: ' + src));
  im.src = src;
});

const out = { files: [], errors: [] };
for (const job of JOBS) {
  for (const [name, q] of job.files) {
    try {
      const im = await load('/' + job.dir + name);
      const cv = document.createElement('canvas');
      cv.width = im.naturalWidth; cv.height = im.naturalHeight;
      /* alpha must survive - these are cut-outs, and jpeg would fill the
         transparent corners in with a rectangle */
      cv.getContext('2d').drawImage(im, 0, 0);
      const url = cv.toDataURL('image/webp', q);
      if (url.indexOf('data:image/webp') !== 0)
        throw new Error('engine refused webp, produced ' + url.slice(0, 24));
      out.files.push({ dir: job.dir + 'optimized/',
                       out: name.replace(/\.png$/, '_opt.webp'),
                       w: im.naturalWidth, h: im.naturalHeight, q: q,
                       b64: url.split(',')[1] });
    } catch (e) { out.errors.push(job.dir + name + ': ' + String(e && e.message || e)); }
  }
}
return out;
