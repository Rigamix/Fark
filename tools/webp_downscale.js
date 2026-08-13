/* DOWNSCALE THE OVERSIZED OPTIMIZED COPIES to phone-max resolution.
 * Denis: "when you optimize the graphics you scale them down to the maximum
 * size they need to be to display ok on a phone screen."
 *
 * Conservative cap, never risks blur: width <= 430*3 = 1290px (the design
 * viewport at dpr 3 / desktop headroom, per tools/art_targets.json's rule),
 * height <= 2700 for full-screen art. Only files OVER the cap are touched;
 * masters in Art/ are never modified - these are the optimized/ copies and
 * the assets/ derivatives, re-encoded smaller from themselves (a reduction
 * never needs the master).
 *
 *   node tools/shoot.js --eval-file tools/webp_downscale.js --out <x>.png
 */
const FILES = [
  'Art/Assets/Shelf/optimized/shelf_bg_opt.webp',
  'assets/win/hands.webp',
  'assets/win/banner.webp',
  'assets/win/bg.webp',
  'Art/Assets/Match/optimized/ScoreBar_new_portraits_opt.webp',
  'Art/Assets/Match/optimized/ScoreBar_opt.webp',
  'Art/Assets/Match/optimized/ScoreBar_overlay_opt.webp',
  'Art/Assets/Match/optimized/ScoreBar_new_portraits_left_opt.webp',
  'Art/Assets/Match/optimized/ScoreBar_new_opt.webp',
  'Art/Assets/Match/optimized/ScoreBar_new_centre_opt.webp',
  'Art/Assets/Match/optimized/ScoreBar_new_fill_opt.webp',
  'Art/Assets/Match/optimized/turn_number_opt.webp',
];
const MAXW = 1290, MAXH = 2700;
const load = src => new Promise((res, rej) => {
  const im = new Image();
  im.onload = () => res(im); im.onerror = () => rej(new Error('load: ' + src));
  im.src = '/' + src + '?cb=' + Math.floor(performance.now());
});
const out = { files: [], skipped: [], errors: [] };
for (const f of FILES) {
  try {
    const im = await load(f);
    const k = Math.min(1, MAXW / im.naturalWidth, MAXH / im.naturalHeight);
    if (k >= 1) { out.skipped.push(f + ' (' + im.naturalWidth + 'px, under cap)'); continue; }
    const w = Math.round(im.naturalWidth * k), h = Math.round(im.naturalHeight * k);
    const cv = document.createElement('canvas');
    cv.width = w; cv.height = h;
    const cx = cv.getContext('2d');
    cx.imageSmoothingQuality = 'high';
    cx.drawImage(im, 0, 0, w, h);
    const url = cv.toDataURL('image/webp', 0.92);
    if (url.indexOf('data:image/webp') !== 0) throw new Error('engine refused webp');
    out.files.push({ path: f, from: im.naturalWidth + 'x' + im.naturalHeight,
                     to: w + 'x' + h, b64: url.split(',')[1] });
  } catch (e) { out.errors.push(f + ': ' + String(e && e.message || e)); }
}
return out;
