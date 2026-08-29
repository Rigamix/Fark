# -*- coding: utf-8 -*-
u"""P866 (BOSS REWARD BRIEF section 5, PASS A ONLY): one word on screen.

Denis: "let's ensure it's all one name for Badges. Because it's just too
confusing right now. Bosses have badges, you win them, you can use them,
that's it."

PASS A AND NOTHING ELSE. No code identifiers, no save keys, no CSS class
names. G._tell, _tellById, _SEAL_POOL, PARKED_TELLS, .tell-badge and the
--tell-badge-* custom properties are all untouched, and S.run.tells and
S.run.sleeve keep their names - renaming a PERSISTED key without a migration
orphans every existing save's won badges, which is Pass B and is only worth
doing if it buys something. Internal names are invisible to the player.

THE CENSUS SAID SIXTEEN AND THE VOCABULARY WAS ALREADY HALF-MOVED. The shelf
screen has said "badge" since P8xx ("'s badge", "The house badge"), and the
seal/sealed-seat noun was retired for the patron mechanic by an explicit
in-file ruling ("THE CURSE, not SEALED SEAT - the word is retired for this
meaning"). One string still contradicted that ruling and is fixed here.

WHAT IS DELIBERATELY NOT TOUCHED: seventeen strings where these are ordinary
English rather than jargon - twelve uses of the VERB "tell", two of a garment
sleeve, an idiomatic "sealed", a wax-seal card name, and two poker-sense uses
("a tell", "your tells") where the word means what it says. A vocabulary pass
that rewrites those makes the game worse, not more consistent.

RELIC BECOMES TROPHY, NOT BADGE. It is not a badge - it is a die on a shelf,
and "trophy" is already the shipped word for it everywhere else (P834's own
ruling and the spoils message both use it). The brief's list is "retire tell,
sleeve, seal and relic from anything on screen", not "call everything badge".

ONE CORRECTNESS FIX RIDES ALONG, because leaving it would be shipping a lie
the same patch walked past: the boss peek sheet said his die "win spoils may
offer it", and P864 stopped offering it - it is granted automatically now. The
sentence had to change anyway to lose the word "relic"; it may as well be
true.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0


def sub(old, new, label):
    global s, n
    if s.count(old) == 1:
        s = s.replace(old, new); n += 1; return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    n += 1


# ── the boss peek sheet: the densest surface, four strings ───────────
sub(u"""    +'<h2>his tell \u2014 binds you only</h2>'""",
    u"""    +'<h2>his badge \u2014 binds you only</h2>'""",
    'peek: his badge')

sub(u"""  if(relic)h+='<h2>relic on display</h2><div class="gbx-box sub" style="height:40px;font-size:12px">'
    +relic.icon+' '+relic.name+' \u2014 win spoils may offer it</div>';""",
    u"""  /* P866: "trophy", not "relic" - it is a die on a shelf, and trophy is
     already the shipped word for it everywhere else. And the second half was
     no longer TRUE: P864 stopped offering the die as a spoils pick and grants
     it on the win instead, so "win spoils may offer it" described a screen
     that no longer exists. */
  if(relic)h+='<h2>his trophy</h2><div class="gbx-box sub" style="height:40px;font-size:12px">'
    +relic.icon+' '+relic.name+' \u2014 yours for the shelf when you beat him</div>';""",
    'peek: trophy + the claim it makes')

sub(u"""  h+='<h2>your sleeve \u2014 one claimed tell, binds both sides</h2>';""",
    u"""  h+='<h2>your badge \u2014 one you have claimed, binds both sides</h2>';""",
    'peek: your badge')

sub(u"""  else h+='<div class="gbx-box sub" style="height:38px;font-size:11px">no tells claimed yet \u2014 beat a boss, choose his tell as spoils</div>';""",
    u"""  else h+='<div class="gbx-box sub" style="height:38px;font-size:11px">no badges claimed yet \u2014 beat a boss and take his badge as spoils</div>';""",
    'peek: empty state')

# ── the match HUD chip, the only in-match surface a worn rule gets ───
sub(u"""border:1px dashed #365">SLEEVED: '""",
    u"""border:1px dashed #365">BADGE: '""",
    'hud chip')

# ── the announce log ─────────────────────────────────────────────────
sub(u"""  famLog('SLEEVED RULE: '+G._sleeve.toUpperCase().replace('_',' ')+' \u2014 BINDS BOTH SIDES');""",
    u"""  famLog('BADGE WORN: '+G._sleeve.toUpperCase().replace('_',' ')+' \u2014 BINDS BOTH SIDES');""",
    'announce log')

# ── the shelf tooltip that contradicted the file's own retirement ────
sub(u"""a patron wearing it plays a SEALED match""",
    u"""a patron wearing it plays a CURSED match""",
    'shelf tooltip: the retired word')

# ── the feat description ─────────────────────────────────────────────
sub(u"""desc:'Win a match under your own Reckoning sleeve'""",
    u"""desc:'Win a match wearing your own Reckoning badge'""",
    'feat desc')

# ── the spoils tile and its message ──────────────────────────────────
sub(u"""+(_spTell?_spTell.name:'TELL')+'</div>'
      +'<div style="font-size:10px;color:#6bc;margin:2px 0">HIS RULE \u2014 TO THE SHELF</div>'""",
    u"""+(_spTell?_spTell.name:'BADGE')+'</div>'
      +'<div style="font-size:10px;color:#6bc;margin:2px 0">HIS BADGE \u2014 TO THE SHELF</div>'""",
    'spoils tile')

sub(u"""msg='HIS RULE GOES TO YOUR SHELF: '+sp.tellName;}""",
    u"""msg='HIS BADGE GOES TO YOUR SHELF: '+sp.tellName;}""",
    'spoils message')

# ── the two dead surfaces, updated anyway ────────────────────────────
# _gbRenderSleeve's host element is never created, so these cannot render.
# They are corrected regardless: if the surface is ever revived it must not
# come back carrying vocabulary the game retired two passes earlier.
sub(u"""  var h='<div style="color:#999;font-size:11px;margin:16px 0 4px">THE SLEEVE \u2014 one claimed tell, a rule for the whole table</div>';""",
    u"""  /* P866: this surface is DEAD - its host element gbSleeveZone is never
     created anywhere in the file, so _gbRenderSleeve returns on line one. The
     wording is corrected anyway, so a revival cannot bring retired vocabulary
     back with it. */
  var h='<div style="color:#999;font-size:11px;margin:16px 0 4px">THE BADGE YOU WEAR \u2014 one you have claimed, a rule for the whole table</div>';""",
    'dead sleeve panel')

sub(u"""    h+='<div style="color:#555;font-size:11px;border:1px dashed #444;padding:10px;text-align:center">no tells claimed yet \u2014 beat a boss and choose his tell as spoils</div>';""",
    u"""    h+='<div style="color:#555;font-size:11px;border:1px dashed #444;padding:10px;text-align:center">no badges claimed yet \u2014 beat a boss and take his badge as spoils</div>';""",
    'dead sleeve panel empty state')

# ── post-asserts ─────────────────────────────────────────────────────
# THE IDENTIFIERS MUST SURVIVE. This is the assertion that keeps Pass A from
# quietly becoming Pass B or C.
for keeper in ['G._tell', '_tellById', '_SEAL_POOL', 'PARKED_TELLS',
               'S.run.tells', 'S.run.sleeve', 'tell-badge', '_ruleActive']:
    if keeper not in s:
        sys.exit('PASS A TOUCHED AN IDENTIFIER: %s missing (nothing written)' % keeper)
# and the load-bearing English must survive too
if "Reckoning badge" not in s:
    sys.exit('FEAT DESC NOT REWRITTEN (nothing written)')
for gone in ['his tell \u2014 binds', 'your sleeve \u2014 one claimed',
             'SLEEVED: ', 'SLEEVED RULE:', 'relic on display', 'SEALED match']:
    if gone in s:
        sys.exit('PLAYER-FACING JARGON SURVIVES: %r (nothing written)' % gone)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d player-facing strings' % n)
