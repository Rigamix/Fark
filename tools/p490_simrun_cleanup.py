# -*- coding: utf-8 -*-
u"""P490 - sim_run.js leaks a temp dir per run. Same shape as the 270GB.

Found while checking whether the sim could even see the P489 change. sim_run.js
line 30 is `fs.mkdtempSync(path.join(os.tmpdir(),'fsim-'))` and there is no
rmSync, no finally, and no signal handler anywhere in the file - the identical
defect just fixed in shoot.js, in the tool that DRIVES shoot.js.

Each fsim- dir holds a concatenated harness+tail (sim_harness.js is ~40KB) and
a sim.png, so it is far smaller per run than a browser profile. It still grows
without bound, and the point of the shoot.js fix was the rule, not the size.

Same three parts as P482/P483, minus the process tree - sim_run spawns node,
not a browser, and spawnSync has already returned by the time we clean up:

  1. cleanup on process.on('exit') so it covers the normal path AND the
     early `process.exit` on a failed run
  2. signal handlers, best-effort (a terminate is not catchable on Windows -
     that is measured, see P483)
  3. a startup sweep with an ownership marker, so a hard kill is collected by
     the NEXT run rather than never

The `.fsim-owner` marker and the dead-owner rule are lifted from P483
deliberately: one pattern in the repo rather than a second that merely looks
similar.
"""
import io, os

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sim_run.js')
with io.open(SRC, encoding='utf-8') as f:
    s = f.read()
orig = s

OLD = u"const dir=fs.mkdtempSync(path.join(os.tmpdir(),'fsim-'));"
assert s.count(OLD) == 1, 'mkdtemp anchor matched %d' % s.count(OLD)

s = s.replace(OLD, u"""/* ── startup sweep, then claim our own ────────────────────────────
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
});""")

# ── gates, BEFORE the write ──
assert s != orig, 'nothing changed'
assert s.count('_fsimCleanup') == 4
assert s.count("process.on('exit',_fsimCleanup)") == 1
assert s.count('.fsim-owner') == 2, 'written once, read once'
assert s.count('fs.rmSync') == 2, 'sweep + cleanup'
assert s.count('process.kill(owner,0)') == 1
assert s.count('fs.mkdtempSync(') == 1  # match the CALL, not the bare name - my own comment says mkdtempSync
# the runner still does its actual job
assert 'spawnSync(process.execPath,args' in s
assert "path.join(dir,'sim_combined.js')" in s
assert s.count('{') == s.count('}'), 'brace mismatch %d vs %d' % (s.count('{'), s.count('}'))

with io.open(SRC, 'w', encoding='utf-8', newline='') as f:
    f.write(s)
print('P490 applied: sim_run.js cleans up and sweeps, same rule as shoot.js')
