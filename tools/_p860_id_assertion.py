# -*- coding: utf-8 -*-
u"""P860 (BOSS REWARD BRIEF section 6, and section 8 says it lands FIRST):
a startup assertion that fails loudly when two DEFINITION tables define a
row under the same id - so every rename in the sections that follow is
checked by the file rather than by a person reading a census.

THE BRIEF'S CENSUS IS WRONG IN BOTH DIRECTIONS, and the reason matters
more than the number, because it decides what the assertion may look at.
The brief counted 23 collided ids with three at depth three. Driven at
runtime against the real arrays (tools/_census_ids2.js) the answer is SIX,
and the gap is two different mistakes cancelling:

  OVER-COUNTED. Five of the brief's 23 - slow_cook, falling_star,
  preserve, short_fuse, steady_hand - are single rows in FAM_CARDS. Their
  "second table" is a test fixture at 22510 and a sim fixture at 45590,
  both of which are `{id:'steady_hand',tier:1}` REFERENCES to the family
  card. A reference is not a definition.

  UNDER-COUNTED, and this is the important half. Ten more ids do appear in
  two arrays each - grogs_flask, brutus_fist, ambrose_grace, old_bones,
  wild_die, coin_flip, the_nudge in NPC_RESCUES; the_tab, corvus_ledger,
  aldrics_vow, twinning_charm, all_in, loan in NPC_ARMS; seven relic dice
  in _RELIC_FAM. Every one of those is a FOREIGN KEY DOING ITS JOB. An
  NPC_RESCUES row is named for the card whose effect it runs
  (npcUseActive('the_tab') at 39881 IS the card id), and _RELIC_FAM is
  keyed by DICE_TYPES id on purpose.

So an assertion over "any id in two arrays" would fire 20-odd times on
correct code at every boot, and the one thing an assertion may never be is
routine. It checks DEFINITION tables only - the ones that are supposed to
be mutually disjoint because their rows are different KINDS of thing that
can end up side by side in one list or one lookup.

WHAT IT WOULD HAVE CAUGHT, stated so this is not a hypothetical: the
comment already in the file at 16193 documents a bug from exactly this
class - _RELIC_FAM's key was corvus_ledger (the CARD) where the DIE is
corvus_ledger_d, "so _matFam returned null for the relic and Break fired
the MUNDANE no-op instead of Starstone's extra turn", silently. That one
is a dangling reference rather than a collision, so this assertion checks
BOTH directions: unresolvable reference ids are reported too.

THE SIX, grandfathered by name so a seventh still fails:
  the_tab         CARDS + FAM_CARDS   (section 2 deletes the CARDS row - goes away)
  finnicks_palm   CARDS + DICE_TYPES  (section 2 deletes the CARDS row - goes away)
  the_collector   CARDS + FEATS
  high_roller     CARDS + FEATS
  second_wind     CARDS + FEATS
  pickpocket      FAM_CARDS + TELLS   (Finnick's badge and a Vagabond family card)

finnicks_palm is the one the brief singled out and it is real: under the
new spoils screen his card and his die would have been two tiles both
reading FINNICK'S PALM behind the same MJ icon.
"""
import io, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'fark_proto.html')
s = io.open(P, encoding='utf-8', newline='').read()
edits = []


def sub(old, new, label):
    global s
    if s.count(old) == 1:
        s = s.replace(old, new)
        edits.append(label)
        return
    pat = re.escape(old).replace('\\\n', '\n').replace('\n', '\\r?\n')
    ms = list(re.finditer(pat, s))
    if len(ms) != 1:
        sys.exit('ANCHOR x%d for %s (nothing written)' % (len(ms), label))
    m = ms[0]
    rep = new.replace('\n', '\r\n') if '\r\n' in m.group(0) else new
    s = s[:m.start()] + rep + s[m.end():]
    edits.append(label)


BLOCK = u"""};
/* \u2550\u2550\u2550 P860: ONE ID, ONE THING \u2550\u2550\u2550
   Placed here because ENCH_ICONS is the LAST definition table in the file -
   everything this reads is declared above this line, so the check can run at
   boot rather than being deferred to a first-use hook that might not fire.

   DEFINITION vs REFERENCE is the whole design. A definition table owns its
   rows; a reference list names rows owned elsewhere. NPC_RESCUES and NPC_ARMS
   are deliberately named for the CARDS ids whose effects they run - the rival
   playing THE TAB really is the_tab - and _RELIC_FAM is keyed by DICE_TYPES id
   on purpose. Checking those for "collisions" would shout ~20 times a boot on
   correct code, and an assertion that shouts routinely is one nobody reads.
   So: definition tables must be mutually disjoint, reference lists must
   RESOLVE, and those are two different failures with two different messages.

   Why bother: a feat and a card sharing a name, a legacy dead card and a live
   redesigned card sharing an id, and a card id used where a die id was meant
   (see the _RELIC_FAM note at corvus_ledger_d - it returned null silently and
   Break fired the wrong branch) have each cost this project real time. A
   census is a snapshot; this is a tripwire. */
var _ID_GRANDFATHER={
  /* THE SIX THAT EXIST TODAY. Measured at runtime, not read off the source -
     tools/_census_ids2.js walks the real arrays. Anything not on this list is
     a NEW collision and fails. Two of these retire in the section-2 card pass;
     when they do, the check says so rather than leaving the list to rot. */
  the_tab:'CARDS active + the Amber family card. The CARDS row goes in section 2.',
  finnicks_palm:'CARDS active + his relic DIE. Two spoils tiles, one name, one icon - the brief section 6 case. The CARDS row goes in section 2.',
  the_collector:'CARDS + FEATS.',
  high_roller:'CARDS + FEATS.',
  second_wind:'CARDS + FEATS.',
  pickpocket:'the Vagabond family card + Finnick\\'s badge.'
};
function _idDefTables(){
  /* tells are defined in two places - on a RUNGS row and in PARKED_TELLS -
     and a parked rule is still a definition, which is the point of parking. */
  var tells=[];
  try{RUNGS.forEach(function(r){if(r&&r.tell&&r.tell.id)tells.push({id:r.tell.id});});}catch(e){}
  try{Object.keys(PARKED_TELLS).forEach(function(k){tells.push({id:k});});}catch(e){}
  return {CARDS:CARDS,NPC_CARDS:NPC_CARDS,DICE_TYPES:DICE_TYPES,FEATS:FEATS,
          FAM_CARDS:FAM_CARDS,ENCH_ICONS:ENCH_ICONS,TELLS:tells};
}
function _idRefLists(){
  /* lists that NAME rows owned above. BOUNTY_POOL is deliberately absent: its
     ids are objective names in their own namespace, not references to a table. */
  return {NPC_RESCUES:(typeof NPC_RESCUES!=='undefined'?NPC_RESCUES:null),
          NPC_ARMS:(typeof NPC_ARMS!=='undefined'?NPC_ARMS:null),
          _RELIC_FAM:(typeof _RELIC_FAM!=='undefined'?_RELIC_FAM:null),
          _SEAL_POOL:(typeof _SEAL_POOL!=='undefined'?_SEAL_POOL:null),
          NPC_FAM_READY:(typeof NPC_FAM_READY!=='undefined'?NPC_FAM_READY:null)};
}
function _idsOf(v){
  if(!v)return[];
  if(Object.prototype.toString.call(v)==='[object Array]')
    return v.map(function(r){return (r&&typeof r==='object')?r.id:r;})
            .filter(function(x){return typeof x==='string';});
  if(typeof v==='object')return Object.keys(v);
  return[];
}
/* `extra` lets a probe inject a deliberate collision and watch this fail -
   section 9 is explicit that an assertion nobody has seen fail is not known to
   work, and there is no other way to see this one fail on purpose. */
function _assertUniqueIds(extra){
  var defs=_idDefTables(),k;
  if(extra)for(k in extra)if(extra.hasOwnProperty(k))defs[k]=extra[k];
  var where={},owners=[];
  for(k in defs){if(!defs.hasOwnProperty(k))continue;
    _idsOf(defs[k]).forEach(function(id){(where[id]||(where[id]=[])).push(k);});}
  var collisions=[],stale=[];
  for(var id in where){if(!where.hasOwnProperty(id))continue;
    var u=[];where[id].forEach(function(t){if(u.indexOf(t)<0)u.push(t);});
    if(u.length>1&&!_ID_GRANDFATHER.hasOwnProperty(id))collisions.push(id+' in '+u.join(' + '));
    if(u.length>1)owners.push(id);}
  for(var g in _ID_GRANDFATHER)if(_ID_GRANDFATHER.hasOwnProperty(g)&&owners.indexOf(g)<0)stale.push(g);
  /* the other direction: a reference naming a row nothing defines. This is the
     shape the corvus_ledger_d bug had, and it fails silently by nature. */
  var refs=_idRefLists(),dangling=[];
  for(k in refs){if(!refs.hasOwnProperty(k))continue;
    _idsOf(refs[k]).forEach(function(id){if(!where[id])dangling.push(k+' -> '+id);});}
  if(collisions.length){
    try{console.error('[ID] NEW COLLISION \u2014 one id, two definition tables:\\n  '+collisions.join('\\n  ')
      +'\\nGive it its own id, or add it to _ID_GRANDFATHER with the reason.');}catch(e){}
  }
  if(dangling.length){
    try{console.error('[ID] DANGLING REFERENCE \u2014 names a row nothing defines:\\n  '+dangling.join('\\n  '));}catch(e){}
  }
  if(stale.length){
    /* a NOTE, never a failure: a grandfather entry going quiet means someone
       FIXED it, and a check that punished that would teach people to leave
       collisions alone. */
    try{console.info('[ID] grandfather entries no longer colliding (safe to delete): '+stale.join(', '));}catch(e){}
  }
  return {collisions:collisions,dangling:dangling,stale:stale};
}
try{
  var _idChk=_assertUniqueIds();
  /* On a dev host a console line is not loud enough - it scrolls past. The
     banner is gated the same way P852 gates the debug URL, so a player never
     sees it even if a future edit does introduce a collision. */
  var _idH=location.hostname||'';
  if((_idChk.collisions.length||_idChk.dangling.length)&&
     (location.protocol==='file:'||_idH==='localhost'||_idH==='127.0.0.1'||_idH==='[::1]'||_idH===''))
    window.addEventListener('DOMContentLoaded',function(){
      var b=document.createElement('div');
      b.style.cssText='position:fixed;left:0;right:0;top:0;z-index:99999;background:#8b1a1a;color:#fff;'
        +'font:11px/1.5 monospace;padding:6px 8px;white-space:pre-wrap';
      b.textContent='ID CHECK FAILED\\n'+_idChk.collisions.concat(_idChk.dangling).join('\\n');
      document.body.appendChild(b);
    });
}catch(e){try{console.error('[ID] check itself threw',e);}catch(e2){}}
/* TRADE'S MACHINERY."""

sub(u"""};
/* TRADE'S MACHINERY.""", BLOCK, '1 the id assertion')

for needed in ['_assertUniqueIds', '_ID_GRANDFATHER', '_idDefTables', '_idRefLists']:
    if needed not in s:
        sys.exit('KEEPER MISSING: %s (nothing written)' % needed)
if s.count('function _assertUniqueIds(') != 1:
    sys.exit('assertion defined %d times (nothing written)' % s.count('function _assertUniqueIds('))

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('done: %d edits (%s)' % (len(edits), ', '.join(edits)))
