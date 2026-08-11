/* OPEN 7 - Sleight is retired from the PLAYER's draft and still live for the rival.
 * Denis ruled "retire it" on the premise that one inert card is low stakes. It is
 * inert only on the player's side; the rival's G._oSleight fires a real reroll,
 * and FAM_LIVE gates BOTH pools - so a blanket retirement would have cut a
 * working card from finnick and whisper (BOSS_FAM: both vagabond), and night 3
 * is the one night already above target.
 * CONTROLS: the pools are non-empty and other vagabond cards still appear, or
 * "sleight is absent" would be true of an empty list.
 */
await new Promise(r=>setTimeout(r,1400));
const v={}, notes={};
const draft=[], opp=[];
for(let i=0;i<400;i++){
  try{ FAM_CARDS.forEach(function(d){ if(_famDraftable(d)&&d.fam==='vagabond'&&draft.indexOf(d.id)<0)draft.push(d.id); }); }catch(e){ notes._err=String(e).slice(0,80); break; }
}
try{ FAM_CARDS.forEach(function(d){ if(FAM_LIVE[d.id]&&!d.unique&&d.fam==='vagabond'&&opp.indexOf(d.id)<0)opp.push(d.id); }); }catch(e){}
notes._playerVagabondPool=draft; notes._rivalVagabondPool=opp;
notes._bossFam={finnick:BOSS_FAM.finnick, whisper:BOSS_FAM.whisper};
/* CONTROLS */
v.thePlayerPoolIsNotEmpty = draft.length>0;
v.theRivalPoolIsNotEmpty  = opp.length>0;
/* THE RULING */
v.sleightIsGoneFromThePlayerDraft = draft.indexOf('sleight')<0;
v.sleightIsStillLiveForTheRival   = opp.indexOf('sleight')>=0;
/* and nothing else was retired by accident */
v.onlySleightWasRemoved = opp.filter(id=>draft.indexOf(id)<0).join(',')==='sleight';
for(const k of Object.keys(v)){ if(k[0]==='_'){notes[k]=v[k];delete v[k];} }
return { verdict:v, notes:notes };
