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

const dir=fs.mkdtempSync(path.join(os.tmpdir(),'fsim-'));
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
