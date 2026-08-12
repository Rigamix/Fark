# -*- coding: utf-8 -*-
"""P649: the procedural dialogue bubble, from Denis's brief and prototype.

WHAT THE BRIEF SAYS TO DECIDE BY READING THE GAME FIRST, and what reading it
decided:

  THE FONT. The prototype's MedievalSharp/Metamorphous/Inter are lab chrome.
  The match bubble already renders in 'JMH Beda' at 3.4cqw in var(--patCol) -
  the SPEAKER'S own colour - so none of that moves. The brief's #4a2f1a is a
  correction away from near-black; --patCol's fallback is #3a2812, which is
  already a warm dark brown, so the game's is kept.

  THE TEXTURE. Art/Assets/parchment_texture.png, which Denis dropped beside the
  brief, through this project's optimized/ pipeline (tools/webp_parchment.js,
  97.6KB -> 9.3KB). Not the prototype's embedded base64. It is 500x155, which is
  exactly the pattern tile size the prototype uses, so the tiling is native.

  THE RENDERING MECHANISM. The prototype puts the text in a <foreignObject>
  because it had no DOM to work with. THIS GAME ALREADY HAS ONE: #dlgText is a
  real element, DLG.show writes jitterText() into it, and jitterText emits a
  per-character <span> with its own transform. Those spans are the game's
  handwriting effect and they measure and wrap correctly in normal DOM flow.
  So the SVG goes BEHIND the existing text rather than swallowing it - the
  bubble is painted, the text stays where every caller already expects it.
  This is the brief's own instruction ("don't assume SVG/foreignObject is
  available or appropriate without checking") answered by checking.

THE ALGORITHM IS PORTED VERBATIM. All ten function names were free in this file
(checked, not assumed), so nothing is renamed and nothing is paraphrased -
mulberry32, walkRoundedRect, inwardNormalAt, jitterPoints, addNotches,
insertTail, applyTaperSkew, orphanSafe, pointsToPath, buildBubblePoints are the
brief's code as written, including the winding-order and modulo-wrap decisions
its bug list warns about.

TWO THINGS THE BRIEF'S BUG LIST DEMANDS AND THIS DOES:
  * the bubble is sized from the REAL bounding box of the built points, tail
    included, wherever the tail ended up - not from a fixed margin
  * the text gets a genuine shrink-to-fit search, not a flat cap: measure the
    height at the width CSS allows, then binary-search downward for the
    narrowest width that still holds that same line count

AND THE ORPHAN GUARANTEE IS STRUCTURAL HERE, not an nbsp. The brief's
orphanSafe swaps the last space in plain text; our text is HTML by the time it
is laid out, and jitterText joins its per-word spans with a literal space. So
the last of those joins becomes U+00A0, which binds the final two words into one
unbreakable run - the same guarantee, applied to the string that actually wraps.
orphanSafe itself is still ported, for whatever uses plain text later.

THE SEED IS THE LINE. mulberry32 exists so a shape reproduces; hashing the text
means a given line always wears the same bubble, and a redraw on resize gets the
same one back instead of reshuffling under the player.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:130]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


ALGO = r"""
/* ═══════ PROCEDURAL DIALOGUE BUBBLE ═══════
   From Denis's brief + speech_bubble_lab.html. The ten functions below are the
   brief's code VERBATIM - every name was free in this file, so nothing is
   renamed and nothing is paraphrased. That includes the three decisions its bug
   list calls out as having been real bugs during the prototype build:
     - the tail index WRAPS with modulo, never clamps
     - the perimeter is walked clockwise in a y-down space, which makes
       (-ty, tx) the INWARD normal: notches add it, the tail subtracts it
     - the tail's tip is flagged non-sharp when curvature is on, or the curve
       gets straightened back out through its own middle
   Do not "tidy" any of those. */
function mulberry32(seed) {
  let s = seed >>> 0;
  return function() {
    s = (s + 0x6D2B79F5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function walkRoundedRect(x, y, w, h, r, spacing) {
  r = Math.min(r, w / 2 - 2, h / 2 - 2);
  const segs = [];
  segs.push({ type: 'line', x1: x + r, y1: y, x2: x + w - r, y2: y });
  segs.push({ type: 'arc', cx: x + w - r, cy: y + r, r, a1: -90, a2: 0 });
  segs.push({ type: 'line', x1: x + w, y1: y + r, x2: x + w, y2: y + h - r });
  segs.push({ type: 'arc', cx: x + w - r, cy: y + h - r, r, a1: 0, a2: 90 });
  segs.push({ type: 'line', x1: x + w - r, y1: y + h, x2: x + r, y2: y + h });
  segs.push({ type: 'arc', cx: x + r, cy: y + h - r, r, a1: 90, a2: 180 });
  segs.push({ type: 'line', x1: x, y1: y + h - r, x2: x, y2: y + r });
  segs.push({ type: 'arc', cx: x + r, cy: y + r, r, a1: 180, a2: 270 });
  const points = [];
  for (const seg of segs) {
    if (seg.type === 'line') {
      const len = Math.hypot(seg.x2 - seg.x1, seg.y2 - seg.y1);
      const n = Math.max(1, Math.round(len / spacing));
      for (let i = 0; i < n; i++) {
        const t = i / n;
        points.push([seg.x1 + (seg.x2 - seg.x1) * t, seg.y1 + (seg.y2 - seg.y1) * t]);
      }
    } else {
      const arcLen = (Math.abs(seg.a2 - seg.a1) / 360) * 2 * Math.PI * seg.r;
      const n = Math.max(2, Math.round(arcLen / spacing));
      for (let i = 0; i < n; i++) {
        const t = i / n;
        const ang = ((seg.a1 + (seg.a2 - seg.a1) * t) * Math.PI) / 180;
        points.push([seg.cx + Math.cos(ang) * seg.r, seg.cy + Math.sin(ang) * seg.r]);
      }
    }
  }
  return points;
}
function inwardNormalAt(points, i) {
  const n = points.length;
  const prev = points[(i - 1 + n) % n];
  const next = points[(i + 1) % n];
  const tx = next[0] - prev[0], ty = next[1] - prev[1];
  const len = Math.hypot(tx, ty) || 1;
  return [-ty / len, tx / len];
}
function jitterPoints(points, amount, rng, deformScale) {
  const n = points.length;
  const raw = points.map(function() { return (rng() * 2 - 1) * amount; });
  const win = Math.max(0, Math.round(deformScale || 0));
  const smoothed = raw.map(function(v, i) {
    if (win === 0) return v;
    let sum = 0, cnt = 0;
    for (let k = -win; k <= win; k++) {
      sum += raw[((i + k) % n + n) % n];
      cnt++;
    }
    return sum / cnt;
  });
  return points.map(function(p, i) {
    const norm = inwardNormalAt(points, i);
    return [p[0] + norm[0] * smoothed[i], p[1] + norm[1] * smoothed[i]];
  });
}
function addNotches(points, count, depth, width, rng, excludeIndex, excludeRadius) {
  const n = points.length;
  const chosen = new Set();
  const isExcluded = function(idx) {
    if (excludeIndex === undefined) return false;
    let d = Math.abs(idx - excludeIndex);
    d = Math.min(d, n - d);
    return d <= excludeRadius;
  };
  for (let k = 0; k < count; k++) {
    let idx, tries = 0;
    do { idx = Math.floor(rng() * n); tries++; } while ((chosen.has(idx) || isExcluded(idx)) && tries < 40);
    if (isExcluded(idx)) continue;
    chosen.add(idx);
  }
  const notchSet = new Set(chosen);
  const outPoints = [];
  const outFlags = [];
  for (let i = 0; i < n; i++) {
    if (notchSet.has(i)) {
      const p = points[i];
      const prev = points[(i - 1 + n) % n];
      const next = points[(i + 1) % n];
      const tx = next[0] - prev[0], ty = next[1] - prev[1];
      const tlen = Math.hypot(tx, ty) || 1;
      const utx = tx / tlen, uty = ty / tlen;
      const [nx, ny] = inwardNormalAt(points, i);
      const d = depth * (0.75 + rng() * 0.5);
      const w = width * (0.75 + rng() * 0.5);
      const shoulderL = [p[0] - utx * w, p[1] - uty * w];
      const tip = [p[0] + nx * d, p[1] + ny * d];
      const shoulderR = [p[0] + utx * w, p[1] + uty * w];
      outPoints.push(shoulderL, tip, shoulderR);
      outFlags.push(true, true, true);
    } else {
      outPoints.push(points[i]);
      outFlags.push(false);
    }
  }
  return { points: outPoints, flags: outFlags };
}
function insertTail(points, flags, tailIndex, length, width, curvature, rng) {
  const n = points.length;
  tailIndex = ((tailIndex % n) + n) % n;
  const base = points[tailIndex];
  const [inx, iny] = inwardNormalAt(points, tailIndex);
  const outx = -inx, outy = -iny;
  const prev = points[(tailIndex - 1 + n) % n];
  const next = points[(tailIndex + 1) % n];
  let tanx = next[0] - prev[0], tany = next[1] - prev[1];
  const tanLen = Math.hypot(tanx, tany) || 1;
  tanx /= tanLen; tany /= tanLen;
  const wobble = (rng() * 2 - 1) * (length * 0.18);
  const spread = width;
  const tipX = base[0] + outx * length + tanx * wobble;
  const tipY = base[1] + outy * length + tany * wobble;
  const leftAnchor = [base[0] - tanx * spread * 0.5, base[1] - tany * spread * 0.5];
  const rightAnchor = [base[0] + tanx * spread * 0.5, base[1] + tany * spread * 0.5];
  const newPoints = points.slice(0, tailIndex);
  const newFlags = flags.slice(0, tailIndex);
  if (curvature && curvature !== 0) {
    const bowx = tanx * curvature, bowy = tany * curvature;
    const leftMid = [(leftAnchor[0] + tipX) / 2 + bowx, (leftAnchor[1] + tipY) / 2 + bowy];
    const rightMid = [(tipX + rightAnchor[0]) / 2 + bowx, (tipY + rightAnchor[1]) / 2 + bowy];
    newPoints.push(leftAnchor, leftMid, [tipX, tipY], rightMid, rightAnchor);
    newFlags.push(true, false, false, false, true);
  } else {
    newPoints.push(leftAnchor, [tipX, tipY], rightAnchor);
    newFlags.push(true, true, true);
  }
  for (let i = tailIndex + 1; i < points.length; i++) {
    newPoints.push(points[i]);
    newFlags.push(flags[i]);
  }
  return { points: newPoints, flags: newFlags };
}
function applyTaperSkew(points, taperV, taperH, skew, w, h) {
  const cx = points.reduce((s, p) => s + p[0], 0) / points.length;
  const cy = points.reduce((s, p) => s + p[1], 0) / points.length;
  return points.map(([x, y]) => {
    const ty = h > 0 ? (y - cy) / (h / 2) : 0;
    const tx = w > 0 ? (x - cx) / (w / 2) : 0;
    let newX = cx + (x - cx) * (1 + taperV * ty * 0.01);
    let newY = cy + (y - cy) * (1 + taperH * tx * 0.01);
    newX += skew * ty;
    return [newX, newY];
  });
}
function orphanSafe(text) {
  const lastSpace = text.lastIndexOf(' ');
  if (lastSpace === -1) return text;
  return text.slice(0, lastSpace) + '\u00A0' + text.slice(lastSpace + 1);
}
function pointsToPath(points, flags) {
  const n = points.length;
  let d = 'M ' + points[0][0].toFixed(2) + ' ' + points[0][1].toFixed(2) + ' ';
  for (let i = 0; i < n; i++) {
    const p1 = points[i];
    const p2 = points[(i + 1) % n];
    if (flags[i] || flags[(i + 1) % n]) {
      d += 'L ' + p2[0].toFixed(2) + ' ' + p2[1].toFixed(2) + ' ';
    } else {
      const p0 = points[(i - 1 + n) % n];
      const p3 = points[(i + 2) % n];
      const c1x = p1[0] + (p2[0] - p0[0]) / 6;
      const c1y = p1[1] + (p2[1] - p0[1]) / 6;
      const c2x = p2[0] - (p3[0] - p1[0]) / 6;
      const c2y = p2[1] - (p3[1] - p1[1]) / 6;
      d += 'C ' + c1x.toFixed(2) + ' ' + c1y.toFixed(2) + ', ' + c2x.toFixed(2) + ' ' + c2y.toFixed(2) + ', ' + p2[0].toFixed(2) + ' ' + p2[1].toFixed(2) + ' ';
    }
  }
  d += 'Z';
  return d;
}
function buildBubblePoints(w, h, opts) {
  const rng = mulberry32(opts.seed);
  let points = walkRoundedRect(6, 6, w - 12, h - 12, opts.cornerRadius, 13);
  points = jitterPoints(points, opts.jitter, rng, opts.deformScale);
  const n0 = points.length;
  const rawTailIndex = ((Math.floor(n0 * opts.tailPos) % n0) + n0) % n0;
  const exclusionRadius = Math.max(1, Math.ceil((opts.tailWidth / 2 + opts.notchWidth + 8) / 13));
  const notched = addNotches(points, opts.notchCount, opts.notchDepth, opts.notchWidth, rng, rawTailIndex, exclusionRadius);
  const n = notched.points.length;
  const tailIndex = ((Math.floor(n * opts.tailPos) % n) + n) % n;
  const withTail = insertTail(notched.points, notched.flags, tailIndex, opts.tailLength, opts.tailWidth, opts.tailCurvature, rng);
  const finalPoints = applyTaperSkew(withTail.points, opts.taperV, opts.taperH, opts.skew, w, h);
  return { points: finalPoints, flags: withTail.flags };
}

/* THE BRIEF'S TUNED DEFAULTS, as one table so Denis can turn any of them.
   A NOTE ON SCALE, stated rather than discovered later: these were tuned on a
   prototype whose bubbles run to 560px wide. The match bubble is capped at 66%
   of the shell, nearer 280px, and every value here is in absolute px - so the
   notches, jitter and tail read proportionally LARGER in game than in the lab.
   Shipped as tuned; this is the first thing to retune if it reads too busy. */
var DLG_BUBBLE = {
  jitter: 1, deformScale: 2,
  notchCount: 3, notchDepth: 4, notchWidth: 3.5,
  strokeW: 2.5, cornerRadius: 37,
  taperV: 0, taperH: -2, skew: -3,
  grainScale: 3.1, grainFreq: 0.2, grainSmooth: 1.9,
  tailLength: 21, tailWidth: 17, tailCurvature: -2, tailPos: 0.99,
  lightAngle: 25, lightIntensity: 0.48, shadowIntensity: 0.22,
  lightBalance: 35, lightBlend: 'overlay',
  embossDepth: 0.25, embossHighlight: 0.5, embossShadow: 0.3,
  /* the brief's corrected stops - beige and dark brown, NOT white and black */
  lightStop: '#d9bd90', shadowStop: '#4a2f18', ink: '#1c140c'
};

/* THE SEED IS THE LINE. mulberry32 exists so a shape reproduces; hashing the
   text means a given line always wears the same bubble and a redraw at a new
   size gets the same one back instead of reshuffling under the player. */
function _bbSeed(str) {
  var h = 2166136261 >>> 0;
  for (var i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); }
  return h >>> 0;
}

/* THE ORPHAN GUARANTEE, ON THE STRING THAT ACTUALLY WRAPS. The brief's
   orphanSafe swaps the last space of PLAIN text; by the time this text is laid
   out it is HTML - jitterText has wrapped every word in its own nowrap span and
   joined them with a literal space. So the LAST of those joins becomes U+00A0,
   which binds the final two words into one unbreakable run. Same guarantee,
   applied where the line breaks are actually decided. */
function _bbOrphanHtml(html) {
  var i = html.lastIndexOf('</span> <span');
  if (i < 0) return html;
  return html.slice(0, i + 7) + '\u00A0' + html.slice(i + 8);
}

/* SHRINK-TO-FIT, per the brief's bug list: not a flat cap. Measure the height
   at the width CSS already allows - the minimum line count this text can have -
   then binary-search downward for the NARROWEST width that still holds it, so a
   two-line bubble is as tight as two lines can be rather than as wide as the
   cap. Returns the width to pin the text at. */
function _bbFitWidth(textEl) {
  textEl.style.width = '';
  textEl.style.whiteSpace = 'nowrap';
  var natural = textEl.scrollWidth;
  textEl.style.whiteSpace = '';
  var maxW = textEl.clientWidth;
  if (!(maxW > 0)) return 0;
  if (natural <= maxW) return natural;
  var minH = textEl.scrollHeight;
  var lo = Math.max(60, maxW * 0.3), hi = maxW;
  for (var i = 0; i < 10 && hi - lo > 3; i++) {
    var mid = (lo + hi) / 2;
    textEl.style.width = mid + 'px';
    if (textEl.scrollHeight <= minH) hi = mid; else lo = mid;
  }
  return hi;
}

/* PAINT THE BUBBLE BEHIND THE TEXT. The SVG is a sibling of #dlgText inside the
   scroll, absolutely placed so the scroll's own border box is the bubble's CORE
   and the tail hangs outside it - which is why .dlg-scroll keeps
   overflow:visible.
   SIZED FROM THE REAL BOUNDING BOX of the built points, tail included, wherever
   the tail ended up. The brief's list calls a fixed margin here out as a bug it
   already made once: the tail is a full 0-1 position around the perimeter, so
   there is no side it can be assumed to be on. */
function dlgBubblePaint(scrollEl, textEl, seed) {
  if (!scrollEl || !textEl) return;
  var w = _bbFitWidth(textEl);
  if (w > 0) textEl.style.width = Math.ceil(w) + 'px';
  var coreW = Math.round(scrollEl.offsetWidth), coreH = Math.round(scrollEl.offsetHeight);
  if (!(coreW > 20 && coreH > 20)) return;

  var o = DLG_BUBBLE;
  var built = buildBubblePoints(coreW, coreH, {
    seed: seed, jitter: o.jitter, deformScale: o.deformScale,
    notchCount: o.notchCount, notchDepth: o.notchDepth, notchWidth: o.notchWidth,
    cornerRadius: o.cornerRadius, taperV: o.taperV, taperH: o.taperH, skew: o.skew,
    tailLength: o.tailLength, tailWidth: o.tailWidth,
    tailCurvature: o.tailCurvature, tailPos: o.tailPos });

  var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  built.points.forEach(function(p) {
    if (p[0] < minX) minX = p[0];
    if (p[0] > maxX) maxX = p[0];
    if (p[1] < minY) minY = p[1];
    if (p[1] > maxY) maxY = p[1];
  });
  var margin = o.strokeW + 4;
  var offX = margin - minX, offY = margin - minY;
  var svgW = (maxX - minX) + margin * 2, svgH = (maxY - minY) + margin * 2;
  var pathD = pointsToPath(built.points.map(function(p) { return [p[0] + offX, p[1] + offY]; }), built.flags);

  var uid = 'b' + (seed >>> 0).toString(36);
  var rad = o.lightAngle * Math.PI / 180;
  var gx1 = (0.5 - Math.sin(rad) * 0.5).toFixed(3), gy1 = (0.5 - Math.cos(rad) * 0.5).toFixed(3);
  var gx2 = (0.5 + Math.sin(rad) * 0.5).toFixed(3), gy2 = (0.5 + Math.cos(rad) * 0.5).toFixed(3);
  var balLow = Math.max(0, o.lightBalance - 15), balHigh = Math.min(100, o.lightBalance + 15);

  var svg = '<svg class="dlg-bubble" width="' + svgW.toFixed(1) + '" height="' + svgH.toFixed(1) + '"'
    + ' viewBox="0 0 ' + svgW.toFixed(1) + ' ' + svgH.toFixed(1) + '" aria-hidden="true"'
    + ' style="left:' + (-offX).toFixed(1) + 'px;top:' + (-offY).toFixed(1) + 'px">'
    + '<defs>'
      + '<pattern id="par-' + uid + '" patternUnits="userSpaceOnUse" width="500" height="155">'
        + '<image href="Art/Assets/optimized/parchment_texture_opt.webp" width="500" height="155"/>'
      + '</pattern>'
      + '<filter id="gr-' + uid + '" x="-20%" y="-20%" width="140%" height="140%">'
        + '<feTurbulence type="fractalNoise" baseFrequency="' + o.grainFreq + '" numOctaves="2" seed="' + (seed % 9999) + '" result="noise"/>'
        + (o.grainSmooth > 0 ? '<feGaussianBlur in="noise" stdDeviation="' + o.grainSmooth + '" result="noise"/>' : '')
        + '<feDisplacementMap in="SourceGraphic" in2="noise" scale="' + o.grainScale + '" xChannelSelector="R" yChannelSelector="G"/>'
      + '</filter>'
      + '<linearGradient id="li-' + uid + '" x1="' + gx1 + '" y1="' + gy1 + '" x2="' + gx2 + '" y2="' + gy2 + '">'
        + '<stop offset="0%" stop-color="' + o.lightStop + '" stop-opacity="' + o.lightIntensity + '"/>'
        + '<stop offset="' + balLow + '%" stop-color="' + o.lightStop + '" stop-opacity="0"/>'
        + '<stop offset="' + balHigh + '%" stop-color="' + o.shadowStop + '" stop-opacity="0"/>'
        + '<stop offset="100%" stop-color="' + o.shadowStop + '" stop-opacity="' + o.shadowIntensity + '"/>'
      + '</linearGradient>'
    + '</defs>'
    /* the parchment, then a SECOND copy of the same path carrying the light as
       a blended tint - the brief is specific that the lighting is a layer over
       the real texture, not baked into it */
    + '<path d="' + pathD + '" fill="url(#par-' + uid + ')" stroke="' + o.ink + '" stroke-width="' + o.strokeW + '" stroke-linejoin="round" stroke-linecap="round" filter="url(#gr-' + uid + ')"/>'
    + '<path d="' + pathD + '" fill="url(#li-' + uid + ')" stroke="none" style="mix-blend-mode:' + o.lightBlend + '" filter="url(#gr-' + uid + ')"/>'
    + '</svg>';

  var old = scrollEl.querySelector('svg.dlg-bubble');
  if (old) old.remove();
  scrollEl.insertAdjacentHTML('afterbegin', svg);
  /* the emboss is on the TEXT, two offset shadows and not one drop shadow */
  textEl.style.textShadow = (-o.embossDepth) + 'px ' + (-o.embossDepth) + 'px 0 rgba(217,189,144,' + o.embossHighlight + '),'
    + o.embossDepth + 'px ' + o.embossDepth + 'px .4px rgba(74,47,24,' + o.embossShadow + ')';
}
"""

# ── 1. the algorithm + renderer, beside jitterText which feeds it ────────
sub(u"function jitterText(text,scale){",
    ALGO.lstrip('\n') + u"\nfunction jitterText(text,scale){",
    'P649 the bubble algorithm and renderer')

# ── 2. DLG.show paints it ────────────────────────────────────────────────
sub(u"      const full='\\u201c'+text+'\\u201d';\n"
    u"      textEl.innerHTML=jitterText(full);",
    u"      const full='\\u201c'+text+'\\u201d';\n"
    u"      /* P649: the orphan guarantee goes on the JITTERED html, because that is\n"
    u"         the string whose line breaks the browser decides - see _bbOrphanHtml. */\n"
    u"      textEl.innerHTML=_bbOrphanHtml(jitterText(full));\n"
    u"      textEl.style.width='';",
    'P649 orphan-proof the line')

sub(u"      box.classList.remove('hiding');box.classList.add('show');this.active=true;",
    u"      box.classList.remove('hiding');box.classList.add('show');this.active=true;\n"
    u"      /* P649: paint the procedural bubble behind the text. Seeded on the LINE,\n"
    u"         so the same words always wear the same bubble and a resize redraw gets\n"
    u"         it back rather than reshuffling. Runs after .show so the box has a\n"
    u"         layout to measure. */\n"
    u"      try{dlgBubblePaint(document.getElementById('dlgScroll'),textEl,_bbSeed(text));}catch(e){}",
    'P649 paint it from DLG.show')

# ── 3. the CSS: the flat panel goes, the SVG takes its place ─────────────
sub(u"#screen-match .dlg-scroll{background:#e8dcc0;border:1px solid #8a734d;border-radius:2cqw;\n"
    u"  box-shadow:none;padding:1.6cqw 3cqw;max-width:66%;margin:0 auto}",
    u"/* P649: THE FLAT PANEL IS GONE - background, border and radius all came off,\n"
    u"   because the bubble is painted now (see dlgBubblePaint). What stays is the\n"
    u"   BOX: this element's border box is the bubble's core, and the tail hangs\n"
    u"   outside it, which is why .dlg-scroll keeps overflow:visible.\n"
    u"   flex:0 1 auto rather than the base rule's flex:1 - the bubble has to hug\n"
    u"   the text for the shrink-to-fit search to mean anything, and flex:1 made it\n"
    u"   fill the row regardless. */\n"
    u"#screen-match .dlg-scroll{background:none;border:0;border-radius:0;\n"
    u"  box-shadow:none;padding:1.6cqw 3cqw;max-width:66%;margin:0 auto;flex:0 1 auto}\n"
    u"/* behind the text, and allowed out of the box: the tail lives out here. */\n"
    u"#screen-match .dlg-scroll svg.dlg-bubble{position:absolute;z-index:0;\n"
    u"  pointer-events:none;overflow:visible}",
    'P649 drop the flat panel, place the SVG')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
