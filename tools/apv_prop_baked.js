/* BAKED SHADOWS IN THE PROP ART.
 *
 * The code-drawn shadows measure radially correct to 0.2 degrees, so a prop
 * whose shadow visibly disobeys the rule is carrying one PAINTED INTO ITS PNG -
 * which no code can steer, because it rotates with the sprite and points
 * wherever the artist put it.
 *
 * Detection: split each sprite's pixels into BODY (opaque) and SHADOW
 * (semi-transparent AND dark - a contact shadow is both). The vector from the
 * body's centroid to the shadow's centroid is the direction the baked shadow
 * falls, and its length relative to the sprite says how pronounced it is.
 *
 * A sprite with no baked shadow returns a tiny magnitude and a meaningless
 * angle; that is the signal to ignore the angle, not a failure. */
const PP = 'Art/Assets/Match/Commoner/Props/';
const NAMES = ['bag','bottle','bottle01','bottle02','bowl_dirty','bowl_full','bread','candle',
  'cauldron','cheese','coins','cork','fork','grapes','jug','key','knife','lantern','loaf',
  'mug01','mug_empty','olives','package','plank','plateMetal','plateWood','pouch','pouch02',
  'pouch03','sausages','singleCoin','singleCoin_02','spoon','towel','towel01','towel02',
  'ustensils','wine'];

const rows = [], errs = [];
for (const n of NAMES){
  try{
    const im = new Image();
    await new Promise((res, rej) => { im.onload = res; im.onerror = () => rej(new Error('404')); im.src = PP + n + '.png?v=2'; });
    const W = im.naturalWidth, H = im.naturalHeight;
    const c = document.createElement('canvas'); c.width = W; c.height = H;
    const ctx = c.getContext('2d', {willReadFrequently:true});
    ctx.drawImage(im, 0, 0);
    const d = ctx.getImageData(0, 0, W, H).data;

    let bx=0, by=0, bn=0, sx=0, sy=0, sn=0;
    for (let y = 0; y < H; y++){
      for (let x = 0; x < W; x++){
        const i = (y*W + x)*4, A = d[i+3];
        if (A < 12) continue;
        const lum = 0.299*d[i] + 0.587*d[i+1] + 0.114*d[i+2];
        /* a contact shadow is translucent AND dark; the body is what is left */
        if (A < 205 && lum < 62){ sx += x; sy += y; sn++; }
        else if (A >= 205){ bx += x; by += y; bn++; }
      }
    }
    if (!bn || !sn){ rows.push({n, shadowPx:sn, bodyPx:bn, note:'no separable shadow'}); continue; }
    bx/=bn; by/=bn; sx/=sn; sy/=sn;
    const dx = sx-bx, dy = sy-by;
    const mag = Math.hypot(dx, dy);
    rows.push({ n, W, H, bodyPx:bn, shadowPx:sn,
      shadowFrac: +(sn/(sn+bn)).toFixed(3),
      /* screen degrees: atan2 with y down, same convention as the shadow code */
      deg: +(Math.atan2(dy, dx)*180/Math.PI).toFixed(1),
      /* how far the shadow sits from the body, as a fraction of sprite width */
      offW: +(mag/W).toFixed(3) });
  }catch(e){ errs.push(n + ': ' + String(e.message||e)); }
}

const out = { errs };
/* only sprites with a real, separable shadow mass are worth an angle */
const real = rows.filter(r => r.shadowFrac >= 0.04 && r.offW >= 0.02);
out.baked = real.sort((a,b) => b.offW - a.offW)
  .map(r => r.n + '  ' + r.deg + '°  off=' + r.offW + '  frac=' + r.shadowFrac);
out.noBaked = rows.filter(r => real.indexOf(r) < 0).map(r => r.n);
/* if these were painted to a single house direction, the angles cluster */
if (real.length){
  const rad = real.map(r => r.deg*Math.PI/180);
  const mx = rad.reduce((a,t)=>a+Math.cos(t),0)/rad.length;
  const my = rad.reduce((a,t)=>a+Math.sin(t),0)/rad.length;
  out.meanDeg = +(Math.atan2(my,mx)*180/Math.PI).toFixed(1);
  /* 1 = all painted the same way, 0 = scattered */
  out.agreement = +Math.hypot(mx,my).toFixed(3);
}
return out;
