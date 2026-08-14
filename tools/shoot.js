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
const { spawn, execFileSync } = require('child_process');
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

/* ── startup sweep — the backstop ──────────────────────────────────
   Signal handlers cannot run on SIGKILL, Task Manager "End task", or the
   harness timeout's TerminateProcess, so a sweep at launch is the only
   thing that ever collects those. Two passes, in this order:

   1. PROCESSES. cleanup()'s tree-kill never ran, so the whole browser
      tree is still alive — ~30 orphaned headless msedge.exe accumulated
      this way (2026-08-14). A live orphan also keeps its profile dir
      locked, which starved the directory pass below. Ours are picked out
      by the [\/]shoot- user-data-dir marker ALONE - not --headless, because
      Edge's crashpad-handler and utility children carry the profile path
      but NOT the headless flag, and a crashpad orphan sat at 45% CPU after
      its parent died (2026-08-14, second incident). The marker matches the
      current layout (tmp/shoot-profiles/shoot-*) AND legacy tmp/shoot-*
      leftovers, and nothing else. Whether the run that made
      a candidate is still alive comes from its profile's .shoot-owner
      marker, so a concurrent shoot and a --keep browser are skipped.

   2. DIRECTORIES, now unlockable.

   Age-gated / owner-gated so a concurrently running shoot is never killed
   out from under itself, and fully guarded: a failure to sweep must never
   stop a run from starting. */
var PROFILE_ROOT = path.join(os.tmpdir(), 'shoot-profiles');

(function sweepOrphanBrowsers(){
  if (process.platform !== 'win32') return;
  var rows;
  try {
    /* -EncodedCommand sidesteps the cmd/PS double-quoting swamp entirely */
    var ps = 'Get-CimInstance Win32_Process -Filter "Name=\'msedge.exe\' or Name=\'chrome.exe\'" | ' +
             "Where-Object { $_.CommandLine -match '[\\\\/]shoot-' } | " +
             'ForEach-Object { "$($_.ProcessId)`t$($_.CommandLine)" }';
    rows = execFileSync('powershell.exe',
      ['-NoProfile', '-NonInteractive', '-EncodedCommand',
       Buffer.from(ps, 'utf16le').toString('base64')],
      { encoding: 'utf8', timeout: 20000 }).split(/\r?\n/).filter(Boolean);
  } catch (e) { return; }                       /* no PowerShell, no sweep */
  var killed = 0;
  for (var i = 0; i < rows.length; i++) {
    var tab = rows[i].indexOf('\t');
    if (tab < 0) continue;
    var pid = parseInt(rows[i].slice(0, tab), 10);
    if (!pid) continue;
    var m = /--user-data-dir=(?:"([^"]+)"|(\S+))/.exec(rows[i].slice(tab + 1));
    var udd = m && (m[1] || m[2]);
    var owner = null;
    if (udd) {
      try { owner = parseInt(fs.readFileSync(path.join(udd, '.shoot-owner'), 'utf8').trim(), 10); }
      catch (e) {}                /* profile already swept - orphan for sure */
    }
    if (owner) {
      var alive = true;
      /* sends no signal - throws if the process is gone. PID reuse reads as
         "alive", which fails SAFE: the browser lives until that pid frees. */
      try { process.kill(owner, 0); } catch (e) { alive = false; }
      if (alive) continue;           /* a concurrent run, or a --keep browser */
    }
    try { execFileSync('taskkill', ['/F', '/T', '/PID', String(pid)], { stdio: 'ignore' }); killed++; }
    catch (e) { /* already collapsed with an earlier row's tree-kill */ }
  }
  if (killed) console.log('swept ' + killed + ' orphaned headless browser(s)');
})();

(function sweepStaleProfiles(){
  var STALE_MS = 30 * 60 * 1000, n = 0;
  var roots = [os.tmpdir(), PROFILE_ROOT];
  for (var r = 0; r < roots.length; r++) {
    try {
      for (var _i = 0, names = fs.readdirSync(roots[r]); _i < names.length; _i++) {
        var name = names[_i];
        if (!/^shoot-/.test(name)) continue;
        if (name === 'shoot-profiles') continue;  /* the parent, not a profile */
        var p = path.join(roots[r], name);
        try {
          var st = fs.statSync(p);
          if (!st.isDirectory()) continue;

          /* WHO OWNS THIS? A dir whose owner process is gone is an orphan and
             can go immediately - waiting on an age gate is what let a week of
             runs pile up. Measured: a terminate on Windows is not catchable,
             so cleanup() does not always get to run and this is the real bound. */
          var owner = null;
          try { owner = parseInt(fs.readFileSync(path.join(p, '.shoot-owner'), 'utf8').trim(), 10); }
          catch (e) { owner = null; }

          if (owner) {
            var alive = true;
            /* sends no signal - throws ESRCH if the process is gone. PID reuse
               reads as "alive", which fails SAFE: the age gate gets it later. */
            try { process.kill(owner, 0); } catch (e) { alive = false; }
            if (alive) continue;                                 /* in use */
          } else if (Date.now() - st.mtimeMs < STALE_MS) {
            continue;                        /* no marker - fall back to age */
          }

          fs.rmSync(p, { recursive: true, force: true });
          n++;
        } catch (e) { /* locked or vanished - the next run will get it */ }
      }
    } catch (e) {}
  }
  if (n) console.log('swept ' + n + ' stale shoot-* profile(s)');
})();

/* A FIXED root, not the per-session scratchpad: the sweep above has to be
   able to recognise last week's orphans, and a path that changes every
   session cannot be a marker. */
try { fs.mkdirSync(PROFILE_ROOT, { recursive: true }); } catch (e) {}
const PROFILE = fs.mkdtempSync(path.join(PROFILE_ROOT, 'shoot-'));
/* claim it, so a later run can tell "still running" from "abandoned" without
   guessing from a timestamp */
try { fs.writeFileSync(path.join(PROFILE, '.shoot-owner'), String(process.pid)); } catch (e) {}
const FLAGS = [
  '--headless=new',
  '--remote-debugging-port=' + PORT,
  '--user-data-dir=' + PROFILE,
  '--no-first-run', '--no-default-browser-check',
  '--disable-extensions', '--mute-audio',
  /* WebGL in headless falls back to SwiftShader; without these the dice
     canvas comes back as a blank rectangle and the shot lies by omission. */
  '--enable-unsafe-swiftshader',
  /* headless counts as hidden: without these, page setTimeouts get batched
     to ~1s+ alignment and every timing measurement measures the throttle,
     not the game (seen 2026-08-13: five timers due 500-1300ms all fired at
     6851ms). */
  '--disable-background-timer-throttling',
  '--disable-renderer-backgrounding',
  '--disable-backgrounding-occluded-windows',
  '--use-gl=angle', '--use-angle=swiftshader',
  '--window-size=' + VW + ',' + VH,
  'about:blank',
];
const proc = spawn(EDGE, FLAGS, { stdio: ['ignore', 'pipe', 'pipe'] });
let browserErr = '';
proc.stderr.on('data', d => { browserErr += d.toString(); });

/* ── cleanup — EVERY exit path, not just the happy one ─────────────
   This file leaked ~270GB of Edge profiles because nothing here ever
   removed PROFILE, on any path, and because proc.kill() on Windows reaches
   only the top msedge.exe while its renderer/GPU children keep running and
   keep the directory locked.

   Registered on 'exit', so process.exit(0) and the exit(3) dead-server path
   are both covered without either having to remember to call it. */
var _cleanedUp = false;
function cleanup(){
  if (_cleanedUp) return;
  _cleanedUp = true;
  /* --keep exists so a browser can be inspected after the run; killing it
     here would defeat the flag. */
  if (KEEP) {
    /* HAND THE CLAIM TO THE BROWSER. The marker currently names this node
       process, which is about to exit - so the next sweep would read "owner
       dead", call the profile an orphan and delete it while the kept browser
       is still using it. The browser is the process that still needs the
       directory, so it becomes the owner. When it is finally closed, its pid
       dies and the profile is collected normally. */
    try {
      if (proc && proc.pid) fs.writeFileSync(path.join(PROFILE, '.shoot-owner'), String(proc.pid));
    } catch (e) {}
    return;
  }
  try {
    if (proc && proc.pid) {
      if (process.platform === 'win32') {
        /* /T = whole tree. Without it the children outlive the run - which
           is exactly what showed up as runaway Edge processes. */
        try { execFileSync('taskkill', ['/F', '/T', '/PID', String(proc.pid)], { stdio: 'ignore' }); }
        catch (e) { try { proc.kill('SIGKILL'); } catch (e2) {} }
      } else {
        try { proc.kill('SIGKILL'); } catch (e) {}
      }
    }
  } catch (e) {}
  /* PARENTAGE-IMMUNE second pass. Edge can re-exec past the pid node
     spawned, so the tree-kill above can hit a corpse while the real browser
     lives on - a NORMAL completed run left a 10-process tree exactly this
     way (2026-08-14, third incident; the startup sweep only collects it on
     the NEXT run, which is the gap the user kept seeing). Everything
     wearing THIS run's profile path dies here, whatever its ancestry. */
  if (process.platform === 'win32') {
    try {
      var _psk = "Get-CimInstance Win32_Process -Filter \"Name='msedge.exe' or Name='chrome.exe'\" | " +
                 "Where-Object { $_.CommandLine -like '*" + PROFILE + "*' } | " +
                 "ForEach-Object { taskkill /F /T /PID $_.ProcessId } | Out-Null";
      execFileSync('powershell.exe',
        ['-NoProfile', '-NonInteractive', '-EncodedCommand',
         Buffer.from(_psk, 'utf16le').toString('base64')],
        { stdio: 'ignore', timeout: 15000 });
    } catch (e) {}
  }
  /* The directory only unlocks once those children are actually gone, so
     retry. process.on('exit') must be synchronous - Atomics.wait is a real
     blocking sleep, not a busy-wait that would burn the CPU this patch is
     here to stop. */
  var _sab = new Int32Array(new SharedArrayBuffer(4));
  for (var i = 0; i < 12; i++) {
    try { fs.rmSync(PROFILE, { recursive: true, force: true }); break; }
    catch (e) { try { Atomics.wait(_sab, 0, 0, 150); } catch (e2) {} }
  }
}
process.on('exit', cleanup);
['SIGINT', 'SIGTERM', 'SIGHUP', 'SIGBREAK'].forEach(function(sig){
  try { process.on(sig, function(){ cleanup(); process.exit(130); }); } catch (e) {}
});
process.on('uncaughtException', function(e){
  console.error('FAILED:', e && e.message); cleanup(); process.exit(1);
});
process.on('unhandledRejection', function(e){
  console.error('FAILED:', e && (e.message || e)); cleanup(); process.exit(1);
});

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

  /* ══ DID THE PAGE ACTUALLY LOAD? ═════════════════════════════════════════
     A dead server does not produce an error here. Chrome serves its own error
     document, readyState goes to 'complete', and every eval runs against it
     perfectly happily - reporting whatever a page with none of the game in it
     reports. On 2026-08-03 that cost five wrong measurements in a row: every
     game global came back `undefined` and the honest reading of that is "the
     patch broke everything", which is not what happened.

     THIS IS A DIFFERENT FAILURE FROM EVERY OTHER INSTRUMENT BUG THIS PROJECT
     HAS HAD. The string verdict, the prose-counting assert, the mangled regex,
     the zero-overlap check - each RAN AGAINST THE REAL GAME and misjudged what
     it saw. There was signal underneath the mistake. This one runs against
     NOTHING and returns a verdict anyway, and no probe can tell "verified
     absent" from "never actually looked".

     run_probes has had a pre-flight for this and it works - it refuses the
     whole suite. But every ad-hoc `shoot.js --eval-file` bypassed it, which is
     how all five happened. The check belongs HERE, where the eval is, so it
     covers the suite, the one-off, and a server that dies mid-run.

     URL-based, not game-based, on purpose: shoot.js is aimed at the live Pages
     build and at scratch files too, so "is this the game" is the wrong
     question. "Did the browser end up somewhere other than where it was sent"
     is right, and chrome-error:// is exactly that. */
  const landed = await evaluate(cdp, 'location.href').catch(() => null);
  if (!landed || /^chrome-error:/.test(landed)) {
    console.error('PAGE DID NOT LOAD: ' + URL_);
    console.error('the browser is on ' + (landed || '(unknown)') + ' — almost');
    console.error('always a dead dev server. Nothing was evaluated: a result');
    console.error('from an error page is not a result, it is a description of');
    console.error('the error page.');
    process.exit(3);
  }

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

  /* the kill itself belongs to cleanup(), which process.exit reaches */
  if (!KEEP) cdp.close();
  else console.log('browser asked to stay on port ' + PORT +
                   '\n  profile at ' + PROFILE +
                   '\n  NOTE: measured - the browser is spawned as a child of this' +
                   '\n  process and does NOT reliably outlive it, so this port may' +
                   '\n  already be dead. Pre-existing --keep behaviour, not the' +
                   '\n  cleanup. If it did exit, the profile is collected on the' +
                   '\n  next run (dead owner), not on a timer.');
  process.exit(0);
})().catch(err => {
  console.error('FAILED:', err.message);
  process.exit(1);                       /* cleanup() runs on 'exit' */
});
