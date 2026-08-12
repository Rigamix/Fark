/* THE SHELF BACKGROUND, PNG -> WebP. Same method as tools/webp_art.js.
 *
 * WHY THIS EXISTS AS ITS OWN FILE: Denis repainted shelf_bg.png (2026-08-12) to
 * remove the three painted card slots, and the optimized copy the game actually
 * loads was still the 2026-07-29 encode - so the game kept showing slots that
 * were no longer in the master. A stale optimized copy is invisible: the master
 * is right, the screen is wrong, and nothing in between says so. Re-run this
 * whenever shelf_bg.png changes.
 *
 * 0.86, matching the win screen's background rather than the 0.92 its cut-outs
 * get: this is a full-screen photograph-like image with no alpha, where the
 * compression has the most room and the least to give away.
 *
 *   node tools/shoot.js --eval-file tools/webp_shelf.js --out <scratch>/x.png
 */
const JOBS = [
  { dir: 'Art/Assets/Shelf/', files: [ ['shelf_bg.png', 0.86] ] },
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
