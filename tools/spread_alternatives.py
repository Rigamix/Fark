# -*- coding: utf-8 -*-
u"""Build the runner that compares `spread` against statistics using all agents.

`spread` = max(win%) - min(win%) across four agents. SPREAD_AUDIT established it
is sound for "these are equal" and for a landslide, and UNSOUND for a mid-sized
delta - which is the regime both the aggression pass and the oppCards lift's
spread column fell into. That is a named limit on the sim, and unlike the other
two (a reimplemented turn loop, four agents) it needs no design decision to
address: it is a question about which estimator to read.

WHY max-min IS THE PROBLEM: it discards every agent between the extremes. With
four agents it reads TWO of them, and both are the most volatile order
statistics in the sample - the max and the min are exactly where noise lands
hardest. So its seed-to-seed variance is large by construction, not by accident.

THREE CANDIDATES, all computed from the SAME per-agent numbers the sweep already
collects, so this costs one run rather than one run per statistic:

  spread   max - min                    (today's, for comparison)
  sd       population standard deviation across the four agents
  mad      mean absolute deviation from the agent mean

THE TEST IS NOT "which is bigger" - they are on different scales and that would
be meaningless. It is SIGNAL-TO-NOISE: for each statistic, how much does it vary
across seeds with NOTHING changed, relative to how much it moves down the tier
ladder? A statistic whose seed-noise swamps the tier trend cannot resolve a
mid-sized change no matter how many seeds are averaged.

Nothing is decided here. This builds the runner and states what would count as
an answer, because swapping the statistic the whole difficulty conversation
reads is not a thing to do on one number.
"""
import io, os, sys

sp = sys.argv[1] if len(sys.argv) > 1 else '.'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
h = io.open(os.path.join(ROOT, 'tools', 'sim_harness.js'), encoding='utf-8').read()
w = io.open(os.path.join(ROOT, 'tools', 'sim_tier_sweep.js'), encoding='utf-8').read()

body = w.replace("var seed=(window.__FSIM_SEED!==undefined)?window.__FSIM_SEED:20260731;",
                 "var seed=_S;")
body = body.replace("var N=(window.__FSIM_N!==undefined)?window.__FSIM_N:220;", "var N=_N;")
assert 'var seed=_S;' in body and 'var N=_N;' in body

# keep the per-agent win list, which the sweep collapses to a mean and a spread
body = body.replace(
    "out.tiers[t]={win:mean(wins),capEnd:mean(caps),",
    "out.tiers[t]={agents:wins.slice(),win:mean(wins),capEnd:mean(caps),")
assert 'agents:wins.slice()' in body, 'could not keep the per-agent numbers'

runner = h + u"""
/* FIVE SEEDS, per-agent win rates kept so three estimators can be compared from
   ONE run rather than one run each. */
const SEEDS=[20260731,20260801,20260802,20260803,20260804];
const runOne=function(_S,_N){
""" + body + u"""
};
const all=SEEDS.map(function(s){ try{ return runOne(s,120); }catch(e){ return {err:String(e).slice(0,90)}; } });
function sd(a){var m=a.reduce(function(x,y){return x+y;},0)/a.length;
  return Math.sqrt(a.reduce(function(x,y){return x+(y-m)*(y-m);},0)/a.length);}
function mad(a){var m=a.reduce(function(x,y){return x+y;},0)/a.length;
  return a.reduce(function(x,y){return x+Math.abs(y-m);},0)/a.length;}
const out={};
for(let t=0;t<8;t++){
  const per=all.filter(r=>r&&r.tiers&&r.tiers[t]).map(r=>r.tiers[t].agents);
  if(!per.length) continue;
  out[t]={
    spread: per.map(a=>+(Math.max.apply(null,a)-Math.min.apply(null,a)).toFixed(2)),
    sd:     per.map(a=>+sd(a).toFixed(2)),
    mad:    per.map(a=>+mad(a).toFixed(2))
  };
}
return {seeds:all.filter(r=>r&&r.tiers).length, perTier:out,
        errs:all.filter(r=>r&&r.err).map(r=>r.err).slice(0,2)};
"""
io.open(os.path.join(sp, 'spread_alts.js'), 'w', encoding='utf-8', newline='').write(runner)
print('runner written to', os.path.join(sp, 'spread_alts.js'))
