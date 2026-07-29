/* shoot.js — photograph the game, without a browser pane.
 *
 * The in-app preview does not composite frames unless its pane is on screen,
 * so nothing that lives on the WebGL canvas can be looked at from here: no
 * dice, no throw, no shatter. Every claim about how the table LOOKS has had to
 * be inferred from measured geometry.
 *
 * This drives a real headless browser over the DevTools Protocol instead, so
 * the page actually renders and the frames can be read back as PNGs.
 * No dependencies: Node 24 has a WebSocket client built in.
 *
 *   node tools/shoot.js --url http://localhost:8084/fark_proto.html --out shot.png
 *   node tools/shoot.js --url https://rigamix.github.io/Fark/ --out live.png
 *   node tools/shoot.js --eval-file setup.js --burst 8 --every 90 --out throw.png
 *
 * --url        page to load (default: the local dev server)
 * --out        PNG path; a burst writes out-1.png, out-2.png, ...
 * --eval-file  JS run after load, before the first shot. Return a promise to
 *              make the shooter wait for it.
 * --wait       ms to settle after the eval before shooting (default 1200)
 * --burst N    take N shots instead of one
 * --every MS   gap between burst shots (default 100) — 100ms at 60fps is
 *              every sixth frame, which is enough to read a throw
 * --w --h      viewport (default 430x900, the design phone)
 * --dpr        device pixel ratio (default 2)
 * --keep       leave the browser running (for poking at by hand)
 */
'use strict';
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

/* ── args ─────────────────────────────────────────────────────────── */
const argv = process.argv.slice(2);
function arg(name, dflt) {
  const i = argv.indexOf('--' + name);
  if (i < 0) return dflt;
  const v = argv[i + 1];
  return (v === undefined || v.startsWith('--')) ? true : v;
}
const URL_    = arg('url', 'http://localhost:8084/fark_proto.html');
const OUT     = path.resolve(String(arg('out', 'shot.png')));
const EVALF   = arg('eval-file', null);
const WAIT    = +arg('wait', 1200);
const BURST   = +arg('burst', 1);
const EVERY   = +arg('every', 100);
const VW      = +arg('w', 430);
const VH      = +arg('h', 900);
const DPR     = +arg('dpr', 2);
const KEEP    = !!arg('keep', false);
const PORT    = 9333 + (process.pid % 200);

/* ── the browser ──────────────────────────────────────────────────── */
const EDGE = [
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
].find(p => fs.existsSync(p));
if (!EDGE) { console.error('no Edge/Chrome found'); process.exit(2); }

const PROFILE = fs.mkdtempSync(path.join(os.tmpdir(), 'shoot-'));
const FLAGS = [
  '--headless=new',
  '--remote-debugging-port=' + PORT,
  '--user-data-dir=' + PROFILE,
  '--no-first-run', '--no-default-browser-check',
  '--disable-extensions', '--mute-audio',
  /* WebGL in headless falls back to SwiftShader; without these the dice
     canvas comes back as a blank rectangle and the shot lies by omission. */
  '--enable-unsafe-swiftshader',
  '--use-gl=angle', '--use-angle=swiftshader',
  '--window-size=' + VW + ',' + VH,
  'about:blank',
];
const proc = spawn(EDGE, FLAGS, { stdio: ['ignore', 'pipe', 'pipe'] });
let browserErr = '';
proc.stderr.on('data', d => { browserErr += d.toString(); });

/* ── CDP, hand-rolled ─────────────────────────────────────────────── */
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function findTarget() {
  for (let i = 0; i < 100; i++) {
    try {
      const r = await fetch('http://127.0.0.1:' + PORT + '/json/list');
      const list = await r.json();
      const pg = list.find(t => t.type === 'page');
      if (pg && pg.webSocketDebuggerUrl) return pg.webSocketDebuggerUrl;
    } catch (e) { /* not up yet */ }
    await sleep(100);
  }
  throw new Error('browser never opened a debug port\n' + browserErr.slice(-800));
}

function connect(wsUrl) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(wsUrl);
    let id = 0;
    const pending = new Map();
    const events = [];
    ws.addEventListener('message', ev => {
      const m = JSON.parse(ev.data);
      if (m.id !== undefined && pending.has(m.id)) {
        const { res, rej } = pending.get(m.id);
        pending.delete(m.id);
        m.error ? rej(new Error(m.error.message)) : res(m.result);
      } else if (m.method) events.push(m);
    });
    ws.addEventListener('error', e => reject(new Error('ws error')));
    ws.addEventListener('open', () => resolve({
      send(method, params) {
        return new Promise((res, rej) => {
          const myId = ++id;
          pending.set(myId, { res, rej });
          ws.send(JSON.stringify({ id: myId, method, params: params || {} }));
        });
      },
      events,
      close() { try { ws.close(); } catch (e) {} },
    }));
  });
}

/* Runtime.evaluate that actually reports failures. A silent throw inside the
   page is the difference between "the feature is broken" and "my setup script
   had a typo", and those must never look the same. */
async function evaluate(cdp, expr, awaitPromise) {
  const r = await cdp.send('Runtime.evaluate', {
    expression: expr,
    awaitPromise: !!awaitPromise,
    returnByValue: true,
    userGesture: true,
  });
  if (r.exceptionDetails) {
    const d = r.exceptionDetails;
    throw new Error('page threw: ' + (d.exception && (d.exception.description || d.exception.value) || d.text));
  }
  return r.result && r.result.value;
}

(async () => {
  const cdp = await connect(await findTarget());
  await cdp.send('Page.enable');
  await cdp.send('Runtime.enable');
  await cdp.send('Emulation.setDeviceMetricsOverride', {
    width: VW, height: VH, deviceScaleFactor: DPR, mobile: true,
  });

  await cdp.send('Log.enable').catch(() => {});
  /* which files did NOT arrive. A missing background is a black table, and a
     black table looks like a design decision rather than a 404. */
  await cdp.send('Network.enable').catch(() => {});

  await cdp.send('Page.navigate', { url: URL_ });
  /* Page.loadEventFired is not enough for a single-file game that boots three
     scripts of its own; wait for the document AND give the boot a moment. */
  for (let i = 0; i < 200; i++) {
    const st = await evaluate(cdp, 'document.readyState').catch(() => null);
    if (st === 'complete') break;
    await sleep(50);
  }
  await sleep(300);

  /* is WebGL real here, or did it silently fall back to nothing? */
  const gl = await evaluate(cdp, `(()=>{try{
    const c=document.createElement('canvas');
    const g=c.getContext('webgl2')||c.getContext('webgl');
    if(!g)return 'NO WEBGL';
    const dbg=g.getExtension('WEBGL_debug_renderer_info');
    return dbg?g.getParameter(dbg.UNMASKED_RENDERER_WEBGL):'webgl ok';
  }catch(e){return 'ERR '+e.message;}})()`);
  console.log('webgl:', gl);
  if (gl === 'NO WEBGL') console.error('!! no WebGL — the dice will not draw');

  if (EVALF) {
    const src = fs.readFileSync(String(EVALF), 'utf8');
    const out = await evaluate(cdp, '(async()=>{' + src + '})()', true);
    if (out !== undefined) console.log('setup:', JSON.stringify(out));
  }
  await sleep(WAIT);

  const shots = [];
  for (let i = 0; i < BURST; i++) {
    const { data } = await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
    const file = BURST === 1 ? OUT : OUT.replace(/\.png$/i, '') + '-' + (i + 1) + '.png';
    fs.writeFileSync(file, Buffer.from(data, 'base64'));
    shots.push(file);
    if (i < BURST - 1) await sleep(EVERY);
  }

  /* anything the PAGE shouted while we were watching. A screenshot of a
     broken page looks a lot like a screenshot of a working one. */
  const shouted = cdp.events
    .filter(e => e.method === 'Runtime.exceptionThrown' ||
                (e.method === 'Runtime.consoleAPICalled' && e.params.type === 'error') ||
                (e.method === 'Log.entryAdded' && e.params.entry.level === 'error'))
    .map(e => e.method === 'Runtime.exceptionThrown'
      ? (e.params.exceptionDetails.exception || {}).description || e.params.exceptionDetails.text
      : e.method === 'Log.entryAdded' ? e.params.entry.text
      : (e.params.args || []).map(a => a.value || a.description).join(' '))
    .filter(Boolean);
  if (shouted.length) console.log('page errors:\n  ' + shouted.slice(0, 8).join('\n  '));

  const missing = cdp.events
    .filter(e => (e.method === 'Network.responseReceived' && e.params.response.status >= 400) ||
                  e.method === 'Network.loadingFailed')
    .map(e => e.method === 'Network.loadingFailed'
      ? 'FAILED ' + (e.params.errorText || '') + ' ' + (e.params.requestId || '')
      : e.params.response.status + ' ' + e.params.response.url);
  if (missing.length) console.log('missing (' + missing.length + '):\n  ' + missing.slice(0, 12).join('\n  '));
  console.log('wrote:\n' + shots.join('\n'));

  if (!KEEP) { cdp.close(); proc.kill(); }
  else console.log('browser left running on port ' + PORT);
  process.exit(0);
})().catch(err => {
  console.error('FAILED:', err.message);
  try { proc.kill(); } catch (e) {}
  process.exit(1);
});
