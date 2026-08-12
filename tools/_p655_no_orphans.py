# -*- coding: utf-8 -*-
"""P655: no orphan word at the end of a line, as a global rule.

Denis: "Also be careful that you don't have an orphan word at the end of a line,
global rule."

P649 did this for the dialogue bubble alone, with a helper that knew what
jitterText's markup looks like. A global rule cannot be per-surface, so this is
one function applied at the two places the game already funnels prose through.

_noOrphan BINDS THE LAST TWO WORDS with a non-breaking space, and the whole
difficulty is that by the time these strings exist they are HTML. A plain
"replace the last space" lands inside `style="white-space:nowrap"` as often as
not, which does not prevent an orphan - it corrupts an attribute. So it walks
backwards to the last space that is in TEXT rather than inside a tag, by asking
whether the nearest angle bracket behind it was an opening or a closing one.

APPLIED AT THE FUNNELS, NOT AT THE CALL SITES, which is what makes it global
rather than seven separate fixes waiting for an eighth surface to be written:
  _accG   every card rule and focus-panel description - 3 call sites today
  _wnHtml every die tooltip and effect label - 6 call sites today
  #resDlg the end screen's outcome line, which is built inline
  #dlgText the match bubble, which had its own copy and now shares this one

WHAT IT IS NOT: a substitute for text-wrap:balance. Balance distributes the
lines; this guarantees the last one is never a single word. The brief that
introduced the bubble said the same thing - "the nbsp is the guarantee, balance
is the improvement on top of it" - and both are now in place everywhere.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
n = 0

NBSP = '\\u00A0'


def sub(old, new, label):
    global s, n
    c = s.count(old)
    if c != 1:
        sys.exit('ANCHOR x%d (need 1) for %s:\n  %r' % (c, label, old[:130]))
    s = s.replace(old, new)
    n += 1
    print('  ok  %s' % label)


# ── 1. the one function, replacing the bubble's private copy ─────────────
sub(u"/* THE ORPHAN GUARANTEE, ON THE STRING THAT ACTUALLY WRAPS. The brief's\n"
    u"   orphanSafe swaps the last space of PLAIN text; by the time this text is laid\n"
    u"   out it is HTML - jitterText has wrapped every word in its own nowrap span and\n"
    u"   joined them with a literal space. So the LAST of those joins becomes U+00A0,\n"
    u"   which binds the final two words into one unbreakable run. Same guarantee,\n"
    u"   applied where the line breaks are actually decided. */\n"
    u"function _bbOrphanHtml(html) {\n"
    u"  var i = html.lastIndexOf('</span> <span');\n"
    u"  if (i < 0) return html;\n"
    u"  return html.slice(0, i + 7) + '\\u00A0' + html.slice(i + 8);\n"
    u"}",
    u"/* P655: NO ORPHAN WORD AT THE END OF A LINE. Denis's rule, and global - so\n"
    u"   this is one function applied at the funnels every surface's prose already\n"
    u"   passes through (_accG, _wnHtml, the two dialogue boxes) rather than a fix\n"
    u"   per surface waiting for an eighth surface to be written.\n"
    u"   THE WHOLE DIFFICULTY IS THAT THESE STRINGS ARE HTML by the time they exist.\n"
    u"   A plain \"replace the last space\" lands inside style=\"white-space:nowrap\"\n"
    u"   as often as not, which does not prevent an orphan - it corrupts an\n"
    u"   attribute. So it walks back to the last space that is in TEXT, by asking\n"
    u"   whether the nearest angle bracket behind it opened a tag or closed one.\n"
    u"   NOT a substitute for text-wrap:balance: balance distributes the lines, this\n"
    u"   guarantees the last one is never a lone word. Both, everywhere. */\n"
    u"function _noOrphan(html) {\n"
    u"  if (typeof html !== 'string') return html;\n"
    u"  var i = html.lastIndexOf(' ');\n"
    u"  while (i > 0) {\n"
    u"    var lt = html.lastIndexOf('<', i), gt = html.lastIndexOf('>', i);\n"
    u"    if (lt <= gt) return html.slice(0, i) + '\\u00A0' + html.slice(i + 1);\n"
    u"    i = html.lastIndexOf(' ', i - 1);\n"
    u"  }\n"
    u"  return html;\n"
    u"}",
    'P655 the one orphan function')

sub(u"      textEl.innerHTML=_bbOrphanHtml(jitterText(full));",
    u"      textEl.innerHTML=_noOrphan(jitterText(full));",
    'P655 the match bubble uses it')

# ── 2. the two prose funnels ─────────────────────────────────────────────
sub(u"function _accG(t){\n"
    u"  t=String(t).replace(/(\\d[\\d,]*)/g,'<span class=\"num\">$1</span>');\n"
    u"  return t.replace(/\\b(once per match|twice per match|three times per match|hot dice|sudden death|bust(?:s|ed)?|bank(?:s|ed|ing)?|reroll(?:s|ed)?|triple(?:s)?|straight(?:s)?|wild(?:s)?|shatter(?:s|ed)?|kept)\\b/gi,\n"
    u"    '<span class=\"kw\">$1</span>');\n"
    u"}",
    u"function _accG(t){\n"
    u"  t=String(t).replace(/(\\d[\\d,]*)/g,'<span class=\"num\">$1</span>');\n"
    u"  /* P655: every card rule and focus-panel description comes through here, so\n"
    u"     the orphan rule is applied once rather than at each of them. */\n"
    u"  return _noOrphan(t.replace(/\\b(once per match|twice per match|three times per match|hot dice|sudden death|bust(?:s|ed)?|bank(?:s|ed|ing)?|reroll(?:s|ed)?|triple(?:s)?|straight(?:s)?|wild(?:s)?|shatter(?:s|ed)?|kept)\\b/gi,\n"
    u"    '<span class=\"kw\">$1</span>'));\n"
    u"}",
    'P655 card and panel prose')

sub(u"  /* Honor literal \\n in desc strings — render as a hard line break in tooltips. */\n"
    u"  return out.replace(/\\n/g,'<br>');\n"
    u"}",
    u"  /* Honor literal \\n in desc strings — render as a hard line break in tooltips. */\n"
    u"  /* P655: and every die tooltip and effect label comes through here. It\n"
    u"     already bound word+number pairs against orphan NUMBERS; the last two\n"
    u"     words are the same problem one step further along. */\n"
    u"  return _noOrphan(out.replace(/\\n/g,'<br>'));\n"
    u"}",
    'P655 tooltip prose')

# ── 3. the end screen's outcome line ─────────────────────────────────────
sub(u"      _dlgHTML+='</div><div class=\"dlg-scroll\"><canvas class=\"res-dlg-canvas\"></canvas><div class=\"dlg-text\">'+_dlgText+'</div></div>';",
    u"      /* P655: the end screen speaks in the same kind of box and wraps the same\n"
    u"         way, so it gets the same guarantee. */\n"
    u"      _dlgHTML+='</div><div class=\"dlg-scroll\"><canvas class=\"res-dlg-canvas\"></canvas><div class=\"dlg-text\">'+_noOrphan(_dlgText)+'</div></div>';",
    'P655 the end screen line')

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('\n%d edits' % n)
