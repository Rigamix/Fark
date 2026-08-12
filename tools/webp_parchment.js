/* THE DIALOGUE BUBBLE'S PARCHMENT, PNG -> WebP. Same method as tools/webp_art.js.
 *
 * The brief is explicit that the prototype's embedded base64 copy is not the
 * asset to ship - "use the game's own parchment/UI texture asset through
 * whatever the normal asset-loading path is". Denis dropped
 * Art/Assets/parchment_texture.png beside the brief; this is that file going
 * through the pipeline every other art folder here uses.
 *
 * 0.90. It TILES - the SVG pattern repeats it at 500x155, which is its native
 * size - so a compression artefact does not appear once, it appears on every
 * repeat and lines up with itself. Higher than a background, lower than a
 * cut-out.
 *
 *   node tools/shoot.js --eval-file tools/webp_parchment.js --out <scratch>/x.png
 */
const JOBS = [
  { dir: 'Art/Assets/', files: [ ['parchment_texture.png', 0.90] ] },
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
