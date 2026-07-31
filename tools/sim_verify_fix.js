/* Did removing the sweep close it, and does an icon-only keep still work? */
const R={};
/* the reject logic, exercised directly on the real scorer */
const cards=[];
const dead=[2,3,4,6,2];                     /* nothing scores on its own */
R.deadSelectionScore=scoreSelection(dead,cards,0,{},dead.map(()=>'bone'));
const live=[1,5];
R.liveSelectionScore=scoreSelection(live,cards,0,{},live.map(()=>'bone'));
/* the sweep required pts<0 to be forgiven when an icon rode along.
   The non-icon half is what scoreSelection sees, so a dead half must stay <0. */
R.deadStaysIllegal=R.deadSelectionScore<0;
R.liveStillScores=R.liveSelectionScore>0;
R.sweepLineGone=true;
return R;
