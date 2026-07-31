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
  /* the eight enchant icons: small, high-contrast plaques that get scaled DOWN
     hard, so quality stays high - artefacts on a 40px icon are very visible. */
  { dir: 'Art/Assets/Enchants/', files: [
    ['break.png', 0.92],
    ['fog.png', 0.92],
    ['quicksilver.png', 0.92],
    ['snare.png', 0.92],
    ['snuff.png', 0.92],
    ['tithe.png', 0.92],
    ['trade.png', 0.92],
    ['ward.png', 0.92] ] },
  /* the patron busts: large cut-outs behind a frame, the biggest art on the
     night screen and the most worth shrinking. */
  { dir: 'Art/Assets/Frames/Patrons/Characters/', files: [
    ['Corbin.png', 0.86],
    ['Dunstan.png', 0.86],
    ['Eira.png', 0.86],
    ['Golgoth.png', 0.86],
    ['Krox.png', 0.86],
    ['Mudge.png', 0.86],
    ['Nebb.png', 0.86],
    ['Nell.png', 0.86],
    ['Nix.png', 0.86],
    ['Osgood.png', 0.86],
    ['Pell.png', 0.86],
    ['Poll.png', 0.86],
    ['Rask.png', 0.86],
    ['Regis.png', 0.86],
    ['Remny.png', 0.86],
    ['Rilla.png', 0.86],
    ['Roan.png', 0.86],
    ['Sil.png', 0.86],
    ['Sparr.png', 0.86],
    ['Squib.png', 0.86],
    ['Thorne.png', 0.86],
    ['Tuck.png', 0.86],
    ['Twill.png', 0.86],
    ['Vess.png', 0.86] ] },
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
