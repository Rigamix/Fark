#!/usr/bin/env bash
# One family per page load - the memory wall is cumulative matches, not batch
# size, so six families in one page is ~1GB and dies while each alone is ~185MB.
set -e
cd "$(dirname "$0")/.."
for fam in obsidian amber starstone silver jade vagabond; do
  python -c "
import io,re,sys
p='tools/sim_break_control.js'
s=io.open(p,encoding='utf-8').read()
s=re.sub(r\"__FSIM_FAM:'[a-z]+'\", \"__FSIM_FAM:'$fam'\", s)
io.open(p,'w',encoding='utf-8',newline='').write(s)
assert \"__FSIM_FAM:'$fam'\" in io.open(p,encoding='utf-8').read()
"
  node tools/sim_run.js tools/sim_break_control.js 2>/dev/null | grep '^setup:' || echo "setup: {\"fam\":\"$fam\",\"FAILED\":true}"
done
