/* THE LOSS SCREEN'S THREE LAYERS, PNG -> WebP. Same method as tools/webp_art.js:
 * there is no cwebp on this machine, but a headless browser is a good encoder.
 * Masters in Art/Assets/Loss/ are never touched; output goes to that folder's
 * optimized/ as <name>_opt.webp, which is this project's established pipeline.
 *
 * ITS OWN FILE RATHER THAN A FOURTH JOB IN webp_art.js: that one re-encodes
 * every art set it lists on each run, including a 1536x2720 background, and
 * this needs to be re-runnable on its own while Denis iterates on the painting.
 *
 * NO BACKGROUND HERE, DELIBERATELY. Denis supplied banner, hands and panel; the
 * mockup's room is the SAME tavern as the win screen's (same flags, same tables,
 * same stools, and win_standard_bg.png is that painting), so the loss screen
 * reuses assets/win/bg.webp rather than shipping a second copy of one image.
 *
 * 0.92 across the board, the same quality the win cut-outs got: all three are
 * alpha cut-outs whose edges sit against a dark room, and banding on a rope or
 * a banner edge is exactly where it would show.
 *
 *   node tools/shoot.js --eval-file tools/webp_loss.js --out <scratch>/x.png
 */
const JOBS = [
  { dir: 'Art/Assets/Loss/', files: [
    ['loss_standard_banner.png', 0.92],
    ['loss_standard_hands.png', 0.92],
    ['loss_standard_panel.png', 0.92] ] },
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
      /* alpha must survive - these are cut-outs over a painted room */
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
