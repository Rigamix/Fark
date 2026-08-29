/* P860 verification. Section 9 of the brief: "an assertion nobody has seen
   fail is not known to work" - so this drives BOTH verdicts, clean and
   deliberately broken, and checks the clean one is clean for the right
   reason (grandfathered) rather than because the check saw nothing. */
if(typeof _assertUniqueIds!=='function')return {FATAL:'_assertUniqueIds missing - patch did not land'};

/* the instrument can see: the definition tables are non-empty */
const defs=_idDefTables();
const sizes={};
Object.keys(defs).forEach(k=>{sizes[k]=_idsOf(defs[k]).length;});
const anyEmpty=Object.keys(sizes).filter(k=>!sizes[k]);

/* 1. clean boot */
const clean=_assertUniqueIds();

/* 2. a NEW collision must fail. Injecting an id that already lives in CARDS
      into a fresh table is exactly the mistake section 6 is guarding. */
const injected=_assertUniqueIds({_PROBE_TABLE:[{id:'grogs_flask'},{id:'iron_crown'}]});

/* 3. a GRANDFATHERED id injected again must STILL be silent - the list is by
      id, so this proves the grandfather is doing the suppressing and the
      check is not simply blind to the extra table. */
const grandfathered=_assertUniqueIds({_PROBE_TABLE:[{id:'second_wind'}]});

/* 4. the six that exist today, by name, so a drift in the list is visible */
const present=[];
const where={};
Object.keys(defs).forEach(t=>{_idsOf(defs[t]).forEach(id=>{(where[id]||(where[id]=[])).push(t);});});
Object.keys(where).forEach(id=>{
  const u=[...new Set(where[id])];
  if(u.length>1)present.push(id+' :: '+u.join('+'));
});

return {
  tableSizes:sizes,
  instrumentCanSee: anyEmpty.length===0,
  emptyTables:anyEmpty,

  cleanBootPasses: clean.collisions.length===0,
  cleanDanglingEmpty: clean.dangling.length===0,
  cleanStale: clean.stale,

  injectedCollisionCaught: injected.collisions.length===2,
  injectedCollisionText: injected.collisions,

  grandfatheredStaysSilent: grandfathered.collisions.length===0,

  liveCollisions: present.sort(),
  liveCollisionCount: present.length,

  VERDICT: (anyEmpty.length===0 && clean.collisions.length===0 && clean.dangling.length===0
            && injected.collisions.length===2 && grandfathered.collisions.length===0
            && present.length===6) ? 'PASS' : 'FAIL',
};
