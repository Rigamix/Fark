/* THE NEW PAUSE ICON, PNG -> WebP. Same browser-encoder method as
 * tools/webp_loss.js; master in Art/Assets/Match/ untouched, output to that
 * folder's optimized/ as pause_new_opt.webp. 0.92, an alpha cut-out like the
 * rest of the match chrome.
 *
 *   node tools/shoot.js --eval-file tools/webp_pause.js --out <scratch>/x.png
 * then feed the printed b64 to a writer.
 */
const load = src => new Promise((res, rej) => {
  const im = new Image();
  im.onload = () => res(im);
  im.onerror = () => rej(new Error('load failed: ' + src));
  im.src = src;
});
const im = await load('/Art/Assets/Match/pause_new.png');
const cv = document.createElement('canvas');
cv.width = im.naturalWidth; cv.height = im.naturalHeight;
cv.getContext('2d').drawImage(im, 0, 0);
const url = cv.toDataURL('image/webp', 0.92);
if (url.indexOf('data:image/webp') !== 0) throw new Error('engine refused webp');
return { dir: 'Art/Assets/Match/optimized/', out: 'pause_new_opt.webp',
         w: im.naturalWidth, h: im.naturalHeight, b64: url.split(',')[1] };
