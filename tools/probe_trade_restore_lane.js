/* S8 / P527 - does a trade still come home after the seat below it is removed?

   The arrangement the source itself names: Trade at a lane, then destroy a die
   in a lane BELOW it so the splice renumbers every seat after it, then end the
   match. Before P527 the ledger's lane was never shifted, so _tradeRestore had
   to guess the index back by counting materials.

   Four arms:
     A  removal BELOW the traded seat   - the arrangement that was broken
     B  no removal                       - the ordinary case must still work
     C  the traded seat itself destroyed - must not half-repair
     D  the rival's board must be repaired at ITS OWN seat, which never
        renumbered when the player lost a die. This is the arm that catches the
        fix for one side breaking the other. */
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const until=async(f,ms)=>{const t=Date.now();while(Date.now()-t<ms){try{if(f())return true;}catch(e){}await sleep(50);}return false;};
if(typeof launchBossMatch!=='function')return{error:'globals missing'};
if(typeof _tradeRestore!=='function')return{error:'_tradeRestore is not global'};

_getS(); S.run=S.run||{}; S.run.tier=2;
S.run.dice=['bone','iron','flint','lead','jade','amber'];
S.run.cards=S.run.cards||[]; S.settings=S.settings||{}; S.settings.reducedMotion=true;
launchBossMatch();
if(!(await until(()=>typeof G!=='undefined'&&G&&G.rung,9000)))return{error:'no match'};
await sleep(700);

const BRAND={t:'tithe',face:1};
/* the player traded their JADE at seat 4 for the rival's STARSTONE */
function setup(removeLane,killTradedSeat){
  G.matchDice=['bone','iron','flint','lead','starstone','amber'];
  G.matchOppDice=['bone','bone','bone','bone','jade','bone'];
  G._enchArr=[null,null,null,null,null,null];
  G.numDice=6; G.pool=[]; G._fairTrade=null; G._diceOut=[];
  G._tradeSwaps=[{lane:4,oLane:4,mine:'jade',theirs:'starstone',myEn:BRAND,cnt:1}];
  if(typeof removeLane==='number')_removeDieAt(killTradedSeat?4:removeLane);
  const laneAfter=(G._tradeSwaps&&G._tradeSwaps[0])?G._tradeSwaps[0].lane:null;
  const goneFlag=(G._tradeSwaps&&G._tradeSwaps[0])?!!G._tradeSwaps[0].seatGone:null;
  const mdBefore=(G.matchDice||[]).slice();
  const n=_tradeRestore();
  return {laneAfterRemoval:laneAfter, seatGone:goneFlag,
          mdBefore:mdBefore, mdAfter:(G.matchDice||[]).slice(),
          oppAfter:(G.matchOppDice||[]).slice(),
          enchAfter:(G._enchArr||[]).map(e=>e?e.t:null),
          restored:n,
          playerGotJadeBack:(G.matchDice||[]).indexOf('jade')!==-1,
          starstoneStillOnPlayer:(G.matchDice||[]).indexOf('starstone')!==-1,
          rivalGotStarstoneBack:(G.matchOppDice||[]).indexOf('starstone')!==-1,
          rivalStillHoldsJade:(G.matchOppDice||[]).indexOf('jade')!==-1};
}

const A=setup(1,false);   // remove seat 1, below the trade
const B=setup(null,false);// no removal
const C=setup(4,true);    // destroy the traded seat itself

/* the brand must come home to the seat the die is actually in */
const brandHomeA = A.mdAfter.indexOf('jade')>=0 && A.enchAfter[A.mdAfter.indexOf('jade')]==='tithe';
const brandHomeB = B.mdAfter.indexOf('jade')>=0 && B.enchAfter[B.mdAfter.indexOf('jade')]==='tithe';
/* D: neither side alone */
const halfRepairC = (C.playerGotJadeBack!==C.rivalGotStarstoneBack);

return {
  A_removalBelow:A, B_noRemoval:B, C_tradedSeatDestroyed:C,
  brandHomeAfterShift:brandHomeA, brandHomeNoShift:brandHomeB,
  halfRepairOnDestroyedSeat:halfRepairC,
  verdict:
    (A.laneAfterRemoval!==3) ? 'FAIL - the ledger lane did not shift with the removal ('+A.laneAfterRemoval+')'
    : !A.playerGotJadeBack ? 'FAIL - the player never got their die back after a shift'
    : !A.rivalGotStarstoneBack ? 'FAIL - the rival was not repaired at its own seat'
    : !brandHomeA ? 'FAIL - the brand did not come home to the shifted seat'
    : !B.playerGotJadeBack || !brandHomeB ? 'FAIL - the ordinary no-removal case broke'
    : halfRepairC ? 'FAIL - the destroyed-seat case repaired one side only'
    : 'PASS - lane maintained, brand home, both sides together, no half-repair'
};
