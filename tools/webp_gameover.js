/* GAME OVER art, PNG -> WebP. Same browser-encoder pipeline; masters in
 * Art/Assets/GameOver/ untouched, output to optimized/. The bg gets 0.85 (a
 * painted street, 2.7MB master); the cut-outs 0.92. All are already at or
 * under the 1290 phone-max cap, so no downscale needed.
 *   node tools/shoot.js --url .../ftv_verify.html --eval-file tools/webp_gameover.js --out <x>.png
 */
const FILES = [
  ['Art/Assets/GameOver/GameOver_bg.png', 0.85],
  ['Art/Assets/GameOver/GameOver_banner.png', 0.92],
  ['Art/Assets/GameOver/GameOver_stat01.png', 0.92],
  ['Art/Assets/GameOver/GameOver_stat02.png', 0.92],
  ['Art/Assets/GameOver/GameOver_stat03.png', 0.92],
  ['Art/Assets/GameOver/GameOver_stat04.png', 0.92],
];
const load = src => new Promise((res, rej) => {
  const im = new Image();
  im.onload = () => res(im); im.onerror = () => rej(new Error('load: ' + src));
  im.src = '/' + src;
});
const out = { files: [], errors: [] };
for (const [f, q] of FILES) {
  try {
    const im = await load(f);
    const cv = document.createElement('canvas');
    cv.width = im.naturalWidth; cv.height = im.naturalHeight;
    cv.getContext('2d').drawImage(im, 0, 0);
    const url = cv.toDataURL('image/webp', q);
    if (url.indexOf('data:image/webp') !== 0) throw new Error('refused webp');
    out.files.push({ path: f.replace('/GameOver_', '/optimized/GameOver_').replace(/\.png$/, '_opt.webp'),
                     w: im.naturalWidth, h: im.naturalHeight, b64: url.split(',')[1] });
  } catch (e) { out.errors.push(f + ': ' + String(e && e.message || e)); }
}
return out;
