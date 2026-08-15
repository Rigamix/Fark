# -*- coding: utf-8 -*-
"""P726b: the 1-preference spans ALL kept groups, not just the first.

P726's preference was per-group: a turn whose first keep held a 5 and a
later keep held the 1 still trapped the 5 (the group scan stopped at the
first group with any scorer). Two passes - every group asked for a 1,
then every group asked for a 5 - so the better die wins wherever it sits.

Anchor matching is per-line ending-tolerant (\\r?\\n) because the P726
edit left this block MIXED - original CRLF lines interleaved with LF
insertions - which defeats the usual whole-string LF->CRLF fallback.
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()

OLD_LINES = [
 u"    (G.kept||[]).some(function(k){",
 u"      /* P534: through _keptScorers, so a BRANDED face can never be chosen.",
 u"         It banks zero by law - _splitIcons holds those dice out of scoring -",
 u"         and brands live on faces 1 and 5, which are the only faces this",
 u"         looks for, so every brand was a candidate and worth 100 or 50. */",
 u"      /* P726: prefer the 1 - it pays 100 against the 5's 50, and a player",
 u"         who kept both means the better one (Denis preserved 'a 1'). */",
 u"      var _ps=_keptScorers(k).filter(function(dd){return dd&&(dd.val===1||dd.val===5);});",
 u"      var _pd=_ps.filter(function(dd){return dd.val===1;})[0]||_ps[0];",
 u"      /* P559 (D6b): TAKE THE BRAND WITH THE MATERIAL. P514 added mat to this",
 u"         capture and did not add ench beside it, so the die came back the right",
 u"         material wearing nothing. Everywhere else in the file the two travel",
 u"         together - the kept group's own dice entries are {val,mat,ench}, which",
 u"         is exactly where _pd comes from, and _removeDieAt's _diceOut record is",
 u"         {lane,mat,ench}. */",
 u"      if(_pd){found=_pd.val;foundMat=_pd.mat||k.mat||'bone';foundEnch=_pd.ench||null;",
 u"        foundLane=(typeof _pd.lane==='number')?_pd.lane:null;/* P726: the stash line read",
 u"           foundLane but nothing ever assigned it - P691's seat record was stillborn */",
 u"        return true;}",
 u"      return (k.vals||[]).some(function(v){",
 u"        if(v===1||v===5){found=v;foundMat=k.mat||'bone';return true;}",
 u"        return false;",
 u"      });",
 u"    });",
]
NEW = u"""    /* P726/P726b: prefer the 1 - it pays 100 against the 5's 50, and a
       player who kept both means the better one (Denis preserved 'a 1').
       TWO PASSES ACROSS ALL GROUPS: a single scan stopped at the first
       group holding any scorer, so a first-kept 5 shadowed a later-kept 1.
       P534 still holds: _keptScorers, so a BRANDED face can never be
       chosen (it banks zero by law and brands live on the very faces this
       looks for). P559 still holds: the brand travels with the material -
       the kept group's dice entries are {val,mat,ench,lane}, exactly what
       the record carries forward. */
    [1,5].some(function(want){
      return (G.kept||[]).some(function(k){
        var _pd=_keptScorers(k).filter(function(dd){return dd&&dd.val===want;})[0];
        if(_pd){found=_pd.val;foundMat=_pd.mat||k.mat||'bone';foundEnch=_pd.ench||null;
          foundLane=(typeof _pd.lane==='number')?_pd.lane:null;/* P726: the stash line
             read foundLane but nothing ever assigned it - P691 was stillborn */
          return true;}
        /* the vals fallback for entries with no dice array - what canUse tests */
        return (k.vals||[]).some(function(v){
          if(v===want){found=v;foundMat=k.mat||'bone';return true;}
          return false;
        });
      });
    });"""

pat = u'\\r?\\n'.join(re.escape(l) for l in OLD_LINES)
m = list(re.finditer(pat, s))
if len(m) != 1:
    sys.exit('ANCHOR x%d (need 1) for two-pass preference' % len(m))
s = s[:m[0].start()] + NEW + s[m[0].end():]
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('  ok  two-pass preference across groups')
print('done: 1 edit')
