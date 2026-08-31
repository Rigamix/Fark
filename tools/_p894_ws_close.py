# -*- coding: utf-8 -*-
u"""P894: a dropped debug connection must fail loudly, not exit silently.

WHAT IT COST. A ladder cell ran for two and a half hours across both seats and
wrote nothing at all - no result, no error, no screenshot, just the headers the
shell echoed around it. The node processes exited mid-eval without a word.

WHY. connect() registered 'message', 'error' and 'open' on the CDP websocket
and no 'close'. When the connection dropped, every pending call stayed
unsettled, node's event loop emptied, and the process exited 0. A dead run and
a good one produced identical output. That is the failure mode this project
keeps writing down: an instrument whose silence is indistinguishable from a
clean result.

THE FIX IS TWO-SIDED because a close can land in two states:
  - a call in flight -> reject it, and the awaiting `evaluate` throws into the
    existing top-level catch, which already prints FAILED and exits 1;
  - nothing in flight (we were inside a sleep) -> nobody is listening, so say
    it here and exit 4.
RUN_DONE distinguishes "closed because we finished" from "closed underneath
us", so the happy path stays silent.

AND THE EVENT BUFFER. cdp.events grew for the whole run with nothing trimming
it, holding every network and console message the page produced - hours of
traffic in a long batch, of which the reports below read at most a dozen. It
keeps a window now. That is not the proven cause of the silent exit, and it is
not claimed to be; it is an unbounded array in a process that is meant to run
for hours.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'tools', 'shoot.js')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


# 1. the flag, declared beside the thing it describes
sub(u"""function connect(wsUrl) {""",
    u"""/* Set on the one path that closes the socket deliberately. Without it the
   close handler below cannot tell "we finished" from "it died under us". */
var RUN_DONE = false;

function connect(wsUrl) {""",
    '1 RUN_DONE')

# 2. the event window
sub(u"""      } else if (m.method) events.push(m);
    });""",
    u"""      } else if (m.method) {
        /* A WINDOW, not a hoard. This array grew for the whole run with nothing
           trimming it; the reports at the end read at most a dozen entries, and
           a multi-hour batch put hours of network and console traffic in a
           node process that has no reason to hold it. */
        events.push(m);
        if (events.length > 4000) events.splice(0, events.length - 4000);
      }
    });
    /* A CLOSE IS A FAILURE AND IT MUST SAY SO. There was no close handler here,
       so a dropped connection left every pending call unsettled: the event loop
       emptied and node exited 0 having printed nothing. That is how a 2h30m
       ladder cell came back as an empty file - the run's silence looked exactly
       like a run that had gone fine.
       Two states, because a close can land in either:
         something in flight -> reject it, and the awaiting evaluate() throws
           into the top-level catch, which reports and exits 1 already;
         nothing in flight (we were inside a sleep) -> nobody is listening, so
           it gets said here. */
    ws.addEventListener('close', () => {
      const inFlight = pending.size;
      pending.forEach(p => p.rej(new Error(
        'the browser closed the debug connection mid-run')));
      pending.clear();
      if (inFlight || RUN_DONE) return;
      console.error('FAILED: the browser closed the debug connection with ' +
                    'nothing in flight - the run is over and produced no result');
      process.exit(4);
    });""",
    '2 the close handler and the event window')

# 3. mark the deliberate close
sub(u"""  /* the kill itself belongs to cleanup(), which process.exit reaches */
  if (!KEEP) cdp.close();""",
    u"""  /* the kill itself belongs to cleanup(), which process.exit reaches */
  RUN_DONE = true;                /* so the close handler stays quiet below */
  if (!KEEP) cdp.close();""",
    '3 the deliberate close')

# ── post-asserts, comments stripped so a comment cannot satisfy one ──
code = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
if code.count("addEventListener('close'") != 1:
    sys.exit('the close handler is not present exactly once (nothing written)')
if code.count('RUN_DONE') != 3:
    sys.exit('RUN_DONE must be declared, set once and read once (nothing written)')
# the flag has to be SET before the deliberate close, or the handler shouts on
# the happy path
_set = code.index('RUN_DONE = true')
_close = code.index('cdp.close()')
if _set > _close:
    sys.exit('RUN_DONE is set after the socket closes (nothing written)')
# and DECLARED before the handler reads it
if code.index('var RUN_DONE') > code.index("addEventListener('close'"):
    sys.exit('RUN_DONE is declared after its reader (nothing written)')
if 'events.splice(0, events.length - 4000)' not in code:
    sys.exit('the event window is missing (nothing written)')
if 'process.exit(4)' not in code:
    sys.exit('the silent-death path has no distinct exit code (nothing written)')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
