# Dialogue bubble — procedural implementation brief

A working prototype exists (`speech_bubble_lab.html`, attached alongside
this brief) — every function below is pulled directly from it, tested and
verified, not retyped from memory. This brief is the spec to implement in
the actual game, not the prototype itself.

## Font — explicit instruction, read this first

The prototype uses MedievalSharp, Metamorphous, and Inter for its own lab
chrome (control panel labels, headings) and for the bubble text itself.
**None of that is part of the spec.** Use whatever font the game's
dialogue already renders in today. The prototype's fonts were picked for
a standalone test page with no existing game context to match — they were
never meant to ship.

## The texture

The prototype embeds a specific parchment PNG as a base64 data URI inside
one file, since it had no other way to stay self-contained. In-game, use
the game's own parchment/UI texture asset through whatever the normal
asset-loading path is — don't port the embedded base64, and don't treat
the specific texture in the prototype as the intended final look if the
game already has its own paper texture established elsewhere.

## Core algorithm — ported directly, tested

This is real, working logic, not pseudocode. Port it as-is; adapt only the
rendering layer (see below) to whatever the game's actual draw path is —
canvas, a different SVG setup, or something else entirely. Read the
existing dialogue-bubble rendering code first to know what that adaptation
needs to look like; this brief doesn't know that shape.

```javascript
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
```

**What each piece does, briefly:**
- `mulberry32` — seeded PRNG so a given seed always reproduces the same
  bubble shape, letting the game re-render identically on resize without
  the shape jumping around.
- `walkRoundedRect` — samples points evenly around a rounded rectangle's
  perimeter as the base shape before any deformation.
- `inwardNormalAt` — the direction pointing into the shape at any point,
  used by jitter, notches, and the tail to know which way is "in."
- `jitterPoints` — per-point random offset for the hand-drawn wobble, with
  `deformScale` spatially averaging neighboring offsets so higher values
  produce broader, correlated undulation instead of tight independent
  noise (these are genuinely different axes — don't collapse them into
  one parameter).
- `addNotches` — the small triangular weathered-edge bites, built as three
  inserted points (two shoulders on the original edge, one pulled-in tip)
  so width and depth are fully independent of each other. Takes an
  exclusion zone so it can't place a notch too close to wherever the tail
  attaches.
- `insertTail` — the pointer, built from the local outward direction at
  its attachment point (not a fixed world-space offset), so it works
  correctly no matter which side of the bubble it's on. Curvature bows
  both edges through a midpoint each; the tip itself has to be marked
  non-sharp too when curvature is active, or the curve gets straightened
  back out through its own middle — this was a real bug caught during
  the build, not a hypothetical to watch for.
- `applyTaperSkew` — two independent axes (vertical width taper,
  horizontal height taper) plus skew, so combinations can produce genuine
  one-corner-vs-another asymmetry, not just uniform top/bottom width.
- `pointsToPath` — converts the point list to an SVG path, using smooth
  curves by default and straight lines only where a point is flagged
  "sharp" (notch tips/shoulders, tail shoulders) so those stay crisp
  against the otherwise organic outline.
- `orphanSafe` — replaces the last space in the text with a non-breaking
  space, guaranteeing the last line of wrapped text never ends up with a
  single orphaned word. Pair with CSS `text-wrap: balance` (or the
  game's equivalent line-balancing approach if the renderer isn't
  browser CSS) for better line-length distribution generally — the nbsp
  is the guarantee, balance is the improvement on top of it.

## Bugs found during the build — don't reintroduce these

**Tail index must wrap with modulo, not clamp.** At `tailPos` values near
1.0, a naive `Math.floor(n * tailPos)` can equal `n` exactly — one past
the last valid index. The perimeter is a closed loop, so position 0 and
position 1 are the same point; wrap with `((i % n) + n) % n`, don't clamp.

**Notch and tail direction depend on winding order.** The perimeter here
is walked clockwise in a y-down coordinate space, which makes
`(-ty, tx)` (rotate the tangent 90° counter-clockwise) the *inward*
normal. Notches need to go inward (add this vector); the tail needs to
go outward (subtract it). Getting either sign backwards was an actual
bug in this build — if the rendering layer uses a different winding
order or a y-up space, re-derive which sign means which direction rather
than assuming these signs port unchanged.

**Bubble sizing must come from the real bounding box, not a fixed
margin.** An earlier version reserved a fixed strip of space assuming
the tail always pointed down. The moment tail position became a full
0-1 slider around the whole perimeter, that assumption broke — build the
full point set (including the tail, wherever it ends up), measure the
actual min/max x and y across all of it, and size the canvas to that.

**Text width needs a real shrink-to-fit search, not a flat cap.** An
earlier version always used the full max-width the moment text needed
to wrap at all, leaving short wrapped lines with excess space on both
sides. Correct approach: measure the height at max-width first (the
minimum possible line count for that text), then binary-search downward
for the narrowest width that still holds that same line count.

## Final parameter defaults, as tuned

**Shape**

| Parameter | Value |
|---|---|
| Outline jitter | 1px |
| Deformation scale | 2 |
| Notch count | 3 |
| Notch depth | 4px |
| Notch width | 3.5px |
| Outline thickness | 2.5px |
| Corner radius | 37px |
| Taper vertical | 0px |
| Taper horizontal | -2px |
| Skew | -3px |
| Grain scale | 3.1 |
| Grain frequency | 0.2 |
| Grain smoothing | 1.9 |
| Tail length | 21px |
| Tail width | 17px |
| Tail curvature | -2px |
| Tail position | 0.99 |

**Lighting**

| Parameter | Value |
|---|---|
| Light angle | 25deg |
| Light intensity | 0.48 |
| Shadow intensity | 0.22 |
| Gradient balance | 35% |
| Blend mode | Overlay |
| Emboss depth | 0.25px |
| Emboss highlight | 0.5 |
| Emboss shadow | 0.3 |

Colors: light stop `#d9bd90` (beige, not white), shadow stop `#4a2f18`
(dark brown, not near-black), body text `#4a2f1a` (dark brown, not
black) — all three were originally near-white/near-black and were
corrected during the build specifically because they read as flat
white/black rather than warm parchment tones. Keep the corrected values,
not near-white/near-black ones.

## Lighting effect, what it actually is

Two layers on top of the parchment fill, not baked into the texture
itself:

1. A second copy of the exact same bubble path, filled with a linear
   gradient (angle, both intensity stops, and the balance point where
   light transitions to shadow are all tunable) and composited with a
   blend mode (Overlay, per the tuned default) so it tints the real
   texture underneath rather than sitting as a flat wash on top of it.
2. A genuine two-shadow emboss on the text itself — a faint light-colored
   offset one direction, a faint dark-colored offset the other — not a
   single flat drop shadow. Depth, highlight opacity, and shadow opacity
   are independently tunable.

## What's not decided here — needs a read of the existing code first

- **Actual rendering mechanism.** The prototype uses SVG with a
  `<foreignObject>` for text (so real CSS text-wrapping and the
  shrink-to-fit search both work via normal DOM measurement). Whatever
  the game currently uses to draw dialogue bubbles and text needs to be
  read before deciding how this ports — don't assume SVG/foreignObject
  is available or appropriate without checking.
- **Performance at real frequency.** This runs a binary search (a
  handful of DOM measurements) plus SVG filter effects (turbulence,
  displacement, blur) per bubble. Fine for a prototype re-rendering on
  input change; worth profiling against however often dialogue actually
  fires in real play before assuming it's free.
- **Where the exact parchment texture comes from and at what
  resolution/tiling the game expects it**, since the prototype's
  embedded copy was provided specifically for this prototype, not
  necessarily the asset the game should ship with.
