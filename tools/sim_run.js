/* sim_run.js — the loader every lens agent uses.
 *
 * shoot.js runs ONE eval file, so the harness has to travel with whatever
 * drives it. This concatenates tools/sim_harness.js in front of a tail file
 * and runs the pair through shoot.js.
 *
 *   node tools/sim_run.js tools/sim_yourtail.js [--seed 12345] [-- ...shoot args]
 *
 * The tail is plain JS with the harness already in scope: FSIM is defined,
 * every real game function is reachable, and whatever the tail `return`s is
 * printed by shoot.js as one "setup: " line of JSON.
 */
'use strict';
const fs=require('fs'),path=require('path'),os=require('os');
const {spawnSync}=require('child_process');

const argv=process.argv.slice(2);
const tail=argv[0];
if(!tail){console.error('usage: node tools/sim_run.js <tailfile.js> [--seed N] [-- shoot args]');process.exit(2);}
const sepIx=argv.indexOf('--');
const passthru=sepIx>=0?argv.slice(sepIx+1):[];
const seedIx=argv.indexOf('--seed');
const seed=seedIx>=0?argv[seedIx+1]:null;

const root=path.resolve(__dirname,'..');
const harness=fs.readFileSync(path.join(root,'tools','sim_harness.js'),'utf8');
const body=fs.readFileSync(path.resolve(tail),'utf8');
const preamble=seed!==null?`\n/* seed injected by sim_run */\nwindow.__FSIM_SEED=${Number(seed)};\n`:'\n';

/* ── startup sweep, then claim our own ────────────────────────────
   This file had the same defect shoot.js did: mkdtempSync and no rm on any
   path. Sweep first so a run that was hard-killed does not leave its dir
   forever - a terminate is not a catchable signal on Windows, so handlers
   alone are not a bound. Owner-marked, dead owner collected immediately,
   age gate only as a fallback. Same rule as shoot.js, not a lookalike. */
(function sweepStale(){
  var STALE_MS=30*60*1000,n=0;
  try{
    var tmp=os.tmpdir(),names=fs.readdirSync(tmp);
    for(var i=0;i<names.length;i++){
      if(!/^fsim-/.test(names[i]))continue;
      var p=path.join(tmp,names[i]);
      try{
        var st=fs.statSync(p); if(!st.isDirectory())continue;
        var owner=null;
        try{owner=parseInt(fs.readFileSync(path.join(p,'.fsim-owner'),'utf8').trim(),10);}catch(e){owner=null;}
        if(owner){
          var alive=true;
          try{process.kill(owner,0);}catch(e){alive=false;}
          if(alive)continue;
        }else if(Date.now()-st.mtimeMs<STALE_MS)continue;
        fs.rmSync(p,{recursive:true,force:true});n++;
      }catch(e){}
    }
  }catch(e){}
  if(n)console.error('swept '+n+' stale fsim-* dir(s)');
})();

const dir=fs.mkdtempSync(path.join(os.tmpdir(),'fsim-'));
try{fs.writeFileSync(path.join(dir,'.fsim-owner'),String(process.pid));}catch(e){}

/* removed on EVERY exit path, including the early process.exit below */
var _fsimCleaned=false;
function _fsimCleanup(){
  if(_fsimCleaned)return; _fsimCleaned=true;
  try{fs.rmSync(dir,{recursive:true,force:true});}catch(e){}
}
process.on('exit',_fsimCleanup);
['SIGINT','SIGTERM','SIGHUP','SIGBREAK'].forEach(function(sig){
  try{process.on(sig,function(){_fsimCleanup();process.exit(130);});}catch(e){}
});
process.on('uncaughtException',function(e){
  console.error('sim_run failed:',e&&e.message);_fsimCleanup();process.exit(1);
});
const combined=path.join(dir,'sim_combined.js');
fs.writeFileSync(combined,harness+preamble+body,'utf8');

/* --wait was hardcoded at 60s, which silently caps how big a batch can be:
   an N=2000 six-family pass needs ~90s and simply produced NO setup: line,
   indistinguishable from a crash. Overridable now, and the default is high
   enough that a large pass does not die quietly. */
const waitIx=argv.indexOf('--wait');
const waitS=waitIx>=0?String(Number(argv[waitIx+1])):'300';
const args=['tools/shoot.js','--eval-file',combined,'--wait',waitS,
            '--out',path.join(dir,'sim.png'),...passthru];
const r=spawnSync(process.execPath,args,{cwd:root,stdio:'inherit'});
process.exit(r.status===null?1:r.status);
