/* PNG -> WebP with no toolchain.
 *
 * There is no cwebp or ImageMagick on this machine, but there is a headless
 * browser, and a browser is a very good image encoder: draw the PNG to a canvas
 * and ask for image/webp. Returns data URLs; the caller decodes them to disk, so
 * the bytes never travel any further than the pipe.
 *
 * Art/ is the author's source folder and is never touched - these are derived
 * copies for the game to load.
 *
 *   node tools/shoot.js --eval-file tools/webp_gameover.js --out /dev/null \
 *     | python <decode the setup: line>
 */
const SRC = 'Art/Assets/LastOrders/';
const FILES = [
  { in: 'LastOrders_bg.png',     out: 'gameover_bg.webp',     q: 0.82 },
  { in: 'LastOrders_banner.png', out: 'gameover_banner.webp', q: 0.90 },
  { in: 'LastOrders_stat01.png', out: 'gameover_flag1.webp',  q: 0.92 },
  { in: 'LastOrders_stat02.png', out: 'gameover_flag2.webp',  q: 0.92 },
  { in: 'LastOrders_stat03.png', out: 'gameover_flag3.webp',  q: 0.92 },
  { in: 'LastOrders_stat04.png', out: 'gameover_flag4.webp',  q: 0.92 },
];

const load = src => new Promise((res, rej) => {
  const im = new Image();
  im.onload = () => res(im);
  im.onerror = () => rej(new Error('load failed: ' + src));
  im.src = src;
});

const out = { files: [], errors: [] };
for (const f of FILES) {
  try {
    const im = await load('/' + SRC + f.in);
    const cv = document.createElement('canvas');
    cv.width = im.naturalWidth; cv.height = im.naturalHeight;
    /* the flags and banner have transparency - alpha must survive, which webp
       does and jpeg would not */
    cv.getContext('2d').drawImage(im, 0, 0);
    const url = cv.toDataURL('image/webp', f.q);
    if (url.indexOf('data:image/webp') !== 0)
      throw new Error('engine refused webp, produced ' + url.slice(0, 24));
    out.files.push({ out: f.out, w: im.naturalWidth, h: im.naturalHeight,
                     q: f.q, b64: url.split(',')[1] });
  } catch (e) { out.errors.push(f.in + ': ' + String(e && e.message || e)); }
}
return out;
