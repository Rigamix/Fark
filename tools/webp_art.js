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
  /* THE WIN SCREEN, four layers. The background is 1536x2720 and 5.5 MB as a
     PNG - far too heavy for a screen that appears after every won match, and
     the alpha layers above it (banner, hands, panel) are cut-outs, so quality
     is kept high on those and the background carries the compression. */
  { dir: 'Art/Assets/Win/Standard/', files: [
    ['win_standard_bg.png', 0.86],
    ['win_standard_banner.png', 0.92],
    ['win_standard_hands.png', 0.92],
    ['win_standard_panel.png', 0.92] ] },
  /* THE MATCH TABLE. The game has been rendering assets/Environment_ART/
     match.png - 1064x1920, dated 07-11, from the previous version's asset
     folder - while the current master is Table_new.png at 1080x2011 (07-27).
     Quality is high (0.92) because this one is full-screen behind everything
     and any banding in the wood grain is visible for the whole match, unlike a
     card face at thumbnail size. It has no transparency, but webp is still the
     right container - the alpha path costs nothing when there is none. */
  { dir: 'Art/Assets/Match/Commoner/', files: [
    ['Table_new.png', 0.92] ] },
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
