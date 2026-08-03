/* apv_runscope_arm — the run-scoped arm, and the handlers the gate cannot see.
 *
 * P448 put Double Stakes and For Keeps on _rsToggle/_rsArmed/_rsTake. The
 * toggles live inside `onclick="…"` attributes that are built as single-quoted
 * JS strings, and the first version of the patch wrote _rsToggle('_dsArmed')
 * straight into one - terminating the string it was inside.
 *
 * THE PARSE GATE CAUGHT THAT ONE AND WOULD NOT CATCH THE NEXT. It parses the
 * <script> blocks; an onclick attribute is a STRING to those blocks and only
 * becomes code when the browser compiles it at click time. A handler can be
 * syntactically broken while every script in the file parses cleanly - it fails
 * silently, on click, in front of a player.
 *
 * So this compiles every inline handler the Room actually renders, via
 * new Function(), and reports the ones that throw. It checks ALL of them, not
 * just the four this patch touched: the same gap covers every inline handler in
 * the game, and a probe that only knows about today's edit is a probe that
 * needs rewriting for tomorrow's.
 */
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms) => { const t0 = Date.now();
  while (Date.now() - t0 < ms) { try { if (fn()) return true; } catch(e){} await sleep(60); } return false; };

await until(() => typeof _rsToggle === 'function', 8000);
if (typeof _rsToggle !== 'function') return { err: 'the run-scoped arm is not defined' };
_getS();
S.run = S.run || {};

const out = {};

/* ── the three verbs ── */
S.run._dsArmed = false;
_rsToggle('_dsArmed'); out.afterFirstToggle = _rsArmed('_dsArmed');
_rsToggle('_dsArmed'); out.afterSecondToggle = _rsArmed('_dsArmed');

/* take: reports armed AND disarms, in one call */
S.run._fkArmed = true;
out.takeArmed = _rsTake('_fkArmed');
out.armedAfterTake = _rsArmed('_fkArmed');
/* THE FAILURE MODE THE ONE-VERB DESIGN EXISTS FOR: taking twice must not
   report armed twice, or a one-shot card spends on every match. */
out.takeAgain = _rsTake('_fkArmed');

/* an unarmed take is false and harmless */
S.run._dsArmed = false;
out.takeUnarmed = _rsTake('_dsArmed');

/* ── every inline handler the Room renders must COMPILE ── */
/* the Room is built by _gbRenderRoom into a host; render it and read the DOM
   rather than regexing the source, so what is checked is what ships */
let rendered = 0, broken = [];
try {
  S.run.fcards = S.run.fcards || [];
  const host = document.createElement('div');
  host.style.cssText = 'position:absolute;left:-9999px;top:0;width:400px';
  document.body.appendChild(host);
  /* arm both so their chips are in the DOM at all */
  S.run._dsArmed = true; S.run._fkArmed = true; S.run._tabOwed = 400;
  if (typeof _gbRenderRoom === 'function') { try { _gbRenderRoom(); } catch (e) {} }
  const ATTRS = ['onclick', 'onchange', 'oninput', 'onpointerdown', 'onpointerup'];
  document.querySelectorAll('*').forEach(el => {
    ATTRS.forEach(a => {
      const src = el.getAttribute && el.getAttribute(a);
      if (!src) return;
      rendered++;
      try { new Function(src); }
      catch (e) { broken.push({ attr: a, src: src.slice(0, 70), err: String(e).slice(0, 50) }); }
    });
  });
  host.remove();
} catch (e) { out.renderErr = String(e).slice(0, 90); }
out.handlersChecked = rendered;
out.brokenHandlers = broken.slice(0, 6);

S.run._dsArmed = false; S.run._fkArmed = false; S.run._tabOwed = 0;

return {
  ...out,
  verdict: {
    toggleOn:        out.afterFirstToggle === true,
    toggleOff:       out.afterSecondToggle === false,
    takeReportsArmed: out.takeArmed === true,
    takeDisarms:     out.armedAfterTake === false,
    takeIsOneShot:   out.takeAgain === false,
    takeUnarmedFalse: out.takeUnarmed === false,
    /* the gap the parse gate structurally cannot cover */
    everyInlineHandlerCompiles: broken.length === 0,
    /* and a zero here would mean the check found nothing to check */
    handlersActuallyFound: rendered > 0
  }
};
