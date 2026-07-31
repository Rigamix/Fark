/* load the harness into the live page, then run the check */
const src=await (await fetch('tools/sim_harness.js')).text();
(0,eval)(src);
if(typeof FSIM==='undefined')return {err:'harness did not install'};
const probe=await (await fetch('tools/apv_harness_trade.js')).text();
return await (new Function('return (async()=>{'+probe+'})()'))();
