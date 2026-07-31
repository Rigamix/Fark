/* RULINGS B AND D TOGETHER.
 * B: Starstone's +500 pays only when the Starstone die is part of the kept and
 *    scored selection - not for merely owning one and banking anything.
 * D: Still Waters hushes by MATERIAL FAMILY, not by whether the die carries a
 *    brand, so a plain Obsidian no longer sails through while the die the
 *    player paid to enchant gets punished.
 * The brief says B "as a side effect, makes it properly suppressible by Still
 * Waters for the first time" - so the two are checked together, because that
 * claim is only true if both landed. */
const out={};
const die=(mat,ench)=>({mat:mat,ench:ench||null,val:5,lane:0});

/* ── B: who pays, and who does not ── */
out.B={
  worked:            _starstonePay([die('starstone')]),          /* in the keep */
  twoWorked:         _starstonePay([die('starstone'),die('starstone')]),
  none:              _starstonePay([die('bone'),die('bone')]),   /* no starstone kept */
  boneOnly:          _starstonePay([die('bone')]),
  ledger:            _starstonePay([die('corvus_ledger_d')])     /* the relic, +300 */
};

/* ── D: the hush, by family, brand irrelevant ── */
/* WEAR THE BADGE. _stillWaters() is _ruleActive('confession','p'), and with no
   match running that is false - which would make every check below pass
   trivially against a badge that is not on. Stub the rule so the hush is
   actually exercised, and record both states so the OFF case is proved too. */
const realRuleActive=window._ruleActive;
out.beforeWearing={plainObsidian:_famHushed(die('obsidian')),
                   starstone:_starstonePay([die('starstone')])};
window._ruleActive=function(id,side){
  if(id==='confession'&&side==='p')return true;
  return realRuleActive.apply(this,arguments);
};
const sw=()=>{try{return _stillWaters();}catch(e){return 'ERR';}};
out.badgeWorn=sw();
out.D={
  plainObsidian:  _famHushed(die('obsidian')),          /* THE bug: was false */
  brandedObsidian:_famHushed(die('obsidian',{t:'break',face:5})),
  plainStarstone: _famHushed(die('starstone')),
  bone:           _famHushed(die('bone')),              /* mundane: no family */
  relicTooth:     _famHushed(die('grogs_tooth')),       /* relics are not badge-proof */
  ledgerRelic:    _famHushed(die('corvus_ledger_d'))
};
/* and what a hushed die's family effect resolves to */
out.effects={
  plainObsidian: _dieEffect(die('obsidian')),
  bone:          _dieEffect(die('bone'))
};

/* ── the two together: a hushed Starstone must pay nothing ── */
out.combined={
  starstoneWhileHushed:_starstonePay([die('starstone')]),
  note:'with the badge worn this must be 0; without it, 500'
};

window._ruleActive=realRuleActive;
out.afterRestore={plainObsidian:_famHushed(die('obsidian'))};
out.verdict={
  B_paysWhenKept:      out.B.worked>0 || out.badgeWorn===true,
  B_scalesPerDie:      out.B.twoWorked===out.B.worked*2,
  B_zeroWithoutOne:    out.B.none===0 && out.B.boneOnly===0,
  D_plainIsHushedToo:  out.badgeWorn ? out.D.plainObsidian===true : out.D.plainObsidian===false,
  D_brandIrrelevant:   out.D.plainObsidian===out.D.brandedObsidian,
  D_mundaneUntouched:  out.D.bone===false,
  D_relicsNotExempt:   out.badgeWorn ? out.D.relicTooth===true : out.D.relicTooth===false
};
return out;
