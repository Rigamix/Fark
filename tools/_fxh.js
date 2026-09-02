/* THE FX HARNESS — state-polled, forced-draw, one copy.
 *
 * WHY THIS EXISTS. The headless probe renders the 3D layer at about ONE FRAME
 * PER SECOND. Measured: D3X._rolling() takes ~19s to clear against ~700ms in a
 * real browser, and _drawGlow refuses to run the whole pass while it is true -
 * so the glow canvas is not even CREATED inside a normal probe window. Every
 * wall-clock wait in an FX probe is therefore a coin flip, and a probe that
 * loses the flip reports a clean zero for a reason that has nothing to do with
 * the code under test. That has already happened three times.
 *
 * THE RULE THIS ENCODES: poll the STATE, never the clock; then force the draw.
 * Nothing is stubbed - the real painter runs on the real dice. Only the wait
 * is made honest.
 *
 * THE SECOND RULE, and it is the one that makes the first worth having: every
 * helper reports whether it ACTUALLY GOT THERE. A probe cannot pass because a
 * canvas was missing, because a roll never landed, or because a pixel counter
 * looked at nothing. `exists` is separate from `px` for exactly that reason -
 * testing px===0 alone is a control that cannot fail.
 *
 * USAGE, from any probe (the server serves the repo root):
 *     eval(await (await fetch('/tools/_fxh.js')).text());
 *     const r = await FXH.rollAndSettle();
 *     if(!r.ok) return {err:'never got to the dice', r};
 *     FXH.draw();
 *     const a = FXH.ink('dgCanvas');
 */
window.FXH = (function(){
  const sleep = ms => new Promise(r => setTimeout(r, ms));

  /* poll a predicate. Returns how long it took, or null - a caller that wants
     to know "did this happen" must be able to tell it from "I gave up". */
  async function until(fn, ms){
    const t0 = Date.now();
    while (Date.now() - t0 < ms){
      try { if (fn()) return Date.now() - t0; } catch(e){}
      await sleep(120);
    }
    return null;
  }

  const tap = el => {
    if (!el) return false;
    const r = el.getBoundingClientRect();
    const o = {bubbles:true, cancelable:true, clientX:r.left+r.width/2, clientY:r.top+r.height/2};
    el.dispatchEvent(new PointerEvent('pointerdown', o));
    el.dispatchEvent(new PointerEvent('pointerup', o));
    el.dispatchEvent(new MouseEvent('click', o));
    return true;
  };

  /* THE PHYSICS TAPE, not a timer. D3X._rolling() is true while any die still
     has a tape to play, and the tape advances per FRAME - so at 1fps this is
     the only honest way to know the dice have stopped. */
  const settled = (ms) => until(() => typeof D3X !== 'undefined' && D3X.dice
    && D3X.dice.some(d => d.match) && !D3X._rolling(), ms || 45000);

  /* start a match and stop when the player can actually act */
  async function match(tier, ms){
    if (typeof launchBossMatch !== 'function') return {ok:false, why:'no boot'};
    _getS(); window._fkDiscardOk = true;
    S.run.tier = tier == null ? 1 : tier; S.run.gold = 500;
    try { delete S.pendingMatch; } catch(e){}
    try { showScreen('gauntlet'); } catch(e){}
    launchBossMatch();
    const t = await until(() => typeof G !== 'undefined' && G && G.phase === 'idle', ms || 25000);
    if (t == null) return {ok:false, why:'match never became idle'};
    await sleep(1200);
    return {ok:true, tookMs:t};
  }

  /* force every face to score, so a probe about MARKS is never derailed by a
     bust it did not ask for */
  function loadDice(vals){
    const Q = (vals && vals.slice()) || (function(){const a=[];for(let i=0;i<24;i++)a.push(i%2?5:1);return a;})();
    const real = window._enchRollM;
    window._enchRollM = (m,e) => Q.length ? Q.shift() : real(m,e);
    return () => { window._enchRollM = real; };
  }

  /* roll, wait for the player's turn to come back, THEN wait for the tape.
     Both are reported: a probe that only checks the second can pass while the
     roll never happened. */
  async function rollAndSettle(opt){
    opt = opt || {};
    const restore = opt.noLoad ? null : loadDice(opt.vals);
    const btn = document.getElementById('btnRoll');
    if (!btn) return {ok:false, why:'no roll button'};
    tap(btn);
    const chose = await until(() => G && G.phase === 'choosing', opt.chooseMs || 40000);
    const drained = await settled(opt.settleMs);
    const free = ((G && G.pool) || []).filter(d => !d.committed);
    if (restore) restore();
    return {
      ok: chose != null && drained != null && free.length > 0,
      reachedChoosing: chose != null, tapeDrained: drained != null,
      freeDice: free.length, free: free,
      why: chose == null ? 'never reached choosing'
         : drained == null ? 'tape never drained'
         : free.length === 0 ? 'no free dice' : null,
    };
  }

  /* THE FORCED DRAW. _drawGlow is only called from D3X's frame pass, which at
     1fps may not run inside any reasonable window. Calling it directly runs
     the real painter on the real dice - it is the wait that is skipped, not
     the work. */
  function draw(){
    let threw = null;
    try { D3X._drawGlow(); } catch(e){ threw = e.message; }
    return threw;
  }

  /* WHAT THE PAINTERS SIZE THEIR CANVASES TO. Every surface in this layer
     computes the same thing - the match screen's rect at min(dpr, the glow
     cap) - so `sized` can be checked against it rather than against zero.
     Returns null when the screen is not up, so "cannot tell" stays distinct
     from "wrong size". */
  function expectedSize(){
    const el = document.getElementById('screen-match');
    if (!el) return null;
    const r = el.getBoundingClientRect();
    if (r.width < 10) return null;
    const dpr = Math.min(devicePixelRatio || 1,
                         (window.D3X && D3X.GLOW_DPR_MAX) || 3);
    return {w: Math.round(r.width * dpr), h: Math.round(r.height * dpr)};
  }

  /* alpha-coverage of a canvas. `exists` is deliberately separate from `px`:
     a missing canvas and an empty one are different findings, and conflating
     them turns "the canvas is clean" into an assertion that cannot fail.
     P899a: and `sized` is separate from both. _glowCv creates the element,
     _drawGlow sizes the backing store, and the sleep path returns before that
     - so a canvas can exist at its 300x150 default while the painter draws at
     a dpr transform, putting the subject off the surface. That reads 0 lit
     with no error anywhere. 300x150 is not zero, so a width check cannot see
     it; only a comparison with what the painters use can. null when there is
     no canvas to size, because absence is not mis-sizing. */
  function sizedOf(cv){
    if (!cv) return null;
    const e = expectedSize();
    if (!e) return null;
    return cv.width === e.w && cv.height === e.h;
  }

  function ink(id){
    const cv = document.getElementById(id || 'dgCanvas');
    if (!cv) return {exists:false, sized:null, px:0, why:'no canvas'};
    if (!cv.width) return {exists:true, sized:false, px:0, why:'zero-width canvas'};
    const d = cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data;
    let n = 0;
    for (let i = 3; i < d.length; i += 4) if (d[i] > 8) n++;
    const e = expectedSize();
    return {exists:true, sized:sizedOf(cv), px:n, w:cv.width, h:cv.height,
            expected:e, why:(sizedOf(cv) === false
              ? 'canvas is ' + cv.width + 'x' + cv.height + ', painters use ' +
                (e ? e.w + 'x' + e.h : '?') + ' - a reading from this surface '
                + 'cannot be trusted'
              : undefined)};
  }

  /* paint one configuration and read it back, in one call, so a probe cannot
     accidentally read a canvas from before its own change */
  function paintWith(fn){
    try { fn(); } catch(e){ return {threw:e.message}; }
    const t = draw();
    return Object.assign(ink('dgCanvas'), t ? {drawThrew:t} : {});
  }

  /* THE INK, not just the coverage. ink() counts alpha, and two states that
     share a silhouette come out byte-identical under it - the card mark and
     the keep glow paint the SAME _hullOf projection and differ only in
     colour. So an alpha probe scores "the mark painted" identically whether
     it painted the mark's red or the selection's gold, and the regression it
     cannot see (a state wearing another state's colour) is exactly the one
     the state layer is about to make possible four more ways.
     Returns the dominant opaque-ish colour, quantised, plus how dominant it
     is - a probe that gets a 3% plurality has not measured a colour. */
  function hue(id, minA){
    const cv = document.getElementById(id || 'dgCanvas');
    if (!cv) return {exists:false, sized:null, why:'no canvas'};
    if (!cv.width) return {exists:true, sized:false, why:'zero-width canvas'};
    const d = cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data;
    const A = minA == null ? 40 : minA, bin = {};
    let n = 0;
    for (let i = 0; i < d.length; i += 4){
      if (d[i+3] < A) continue;
      n++;
      const k = (d[i]>>4<<8) | (d[i+1]>>4<<4) | (d[i+2]>>4);
      bin[k] = (bin[k]||0) + 1;
    }
    if (!n) return {exists:true, sized:sizedOf(cv), lit:0,
                    why:'nothing above alpha floor'};
    let best = -1, bk = 0;
    for (const k in bin) if (bin[k] > best){ best = bin[k]; bk = +k; }
    const r = (bk>>8&15)*17, g = (bk>>4&15)*17, b = (bk&15)*17;
    const hex = '#' + [r,g,b].map(v => v.toString(16).padStart(2,'0')).join('');
    return {exists:true, sized:sizedOf(cv), lit:n, hex, rgb:[r,g,b],
            share:+(best/n).toFixed(3),
            reddish: r > g + 24 && r > b + 24,
            goldish: r > b + 40 && g > b + 40 && Math.abs(r-g) < 90};
  }

  const clearMarks = () => ((G && G.pool) || []).forEach(d => {
    if (d.el) d.el.classList.remove('selected','cardmark');
    d.sel = false;
  });

  return {sleep, until, tap, settled, match, loadDice, rollAndSettle,
          draw, ink, hue, paintWith, clearMarks, expectedSize, sizedOf};
})();
