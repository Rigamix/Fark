/* The words the player actually sees. Reads the live tables rather than the
 * source, so a string that failed to parse into the object shows up here. */
const out={};
try{
  const mt=(typeof FAM_CARDS!=='undefined'?FAM_CARDS:[]).filter(c=>c.id==='marked_table')[0];
  out.card={name:mt&&mt.name, text:mt&&mt.text};
}catch(e){out.cardErr=String(e);}
try{
  out.tells=RUNGS.map(r=>r.tell&&({name:r.tell.name,desc:r.tell.desc})).filter(Boolean);
}catch(e){out.tellErr=String(e);}
/* nothing the player reads may still say seal-as-cursed-seat or mark-as-enchant */
const bad=[];
try{
  (typeof PATRON_LINES!=='undefined'?PATRON_LINES:[]).forEach(r=>{
    if(/marked dice|marked face|sealed seat/i.test(r.t||''))bad.push(r.t.slice(0,60));
  });
}catch(e){}
out.strayLines=bad;
out.verdict={
  cardRenamed: out.card && out.card.name==='Cursed Table',
  tooltipNamesTheSmoke: !!(out.card && /smoke/i.test((out.card.text||[])[0]||'')),
  noStrayMarkedDice: bad.length===0,
  tellsSayEnchanted: out.tells ? out.tells.every(t=>!/marked/i.test(t.desc||'')) : null
};
return out;
