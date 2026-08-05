# -*- coding: utf-8 -*-
u"""Remove the comments left orphaned by P476, and fix one that is now false.

The probe reported blockLowBankGone:false. The mechanic IS gone from executable
code - all five surviving references are prose. But prose about deleted code is
exactly the stale-comment problem this project keeps finding, and one of them is
worse than stale:

  _oppFxPlayer's header LISTS block_low_bank as one of the mechanics it
  contains. It no longer does. A header that enumerates contents is a claim, and
  that claim is now wrong.

  Two comments describe the deleted branches themselves ("block_low_bank,
  opponent side. NO CARD declares this...") - they document code that is not
  there.

The two remaining mentions are historical - they cite block_low_bank as a past
example inside longer explanations - and stay, because they are about what was
learned rather than about what the file contains.
"""
import io, os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'fark_proto.html')
s = io.open(SRC, encoding='utf-8').read()
orig = s

# 1. the header that enumerates contents and is now wrong
OLD_HDR = u"/* _oppFxPlayer - steal_pct, steal_low_bank, block_low_bank, challenge, halve_first_bank."
assert s.count(OLD_HDR) == 1, 'header matched %d' % s.count(OLD_HDR)
s = s.replace(OLD_HDR,
              u"/* _oppFxPlayer - steal_pct, steal_low_bank, challenge, halve_first_bank.\n"
              u"   (block_low_bank was here until P476 deleted it - no card declared it.)")

# 2. the two comments describing branches that no longer exist
def drop_comment(src, needle):
    i = src.find(needle)
    assert i >= 0, 'comment not found: %s' % needle[:40]
    st = src.rfind('/*', 0, i)
    en = src.find('*/', i)
    assert st >= 0 and en > st, 'comment bounds not found'
    en += 2
    while en < len(src) and src[en] in ' \t':
        en += 1
    if en < len(src) and src[en] == '\n':
        en += 1
    # take the indentation that preceded it too
    ls = src.rfind('\n', 0, st) + 1
    if src[ls:st].strip() == '':
        st = ls
    return src[:st] + src[en:]

for needle in [u"block_low_bank, opponent side. NO CARD currently declares this",
               u"block_low_bank, player side. NO CARD currently declares this"]:
    s = drop_comment(s, needle)

assert s != orig
# executable code must be free of it; prose may still cite it as history
body = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
assert 'block_low_bank' not in body, 'still present in executable code'
left = len(re.findall(r'block_low_bank', s))
assert left == 3, 'expected 3 historical mentions, found %d' % left

io.open(SRC, 'w', encoding='utf-8', newline='').write(s)
print('orphaned comments removed; %d historical mentions kept' % left)
