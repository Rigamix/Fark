/* A DROPPED CSS RULE IS SILENT.
 * The .ptcard .lwho bug was a lost comment opener, which made the parser
 * swallow the rule that followed it. Nothing errored; the page just quietly
 * used a different rule. This asks the BROWSER which selectors it actually
 * parsed - rather than trusting that written CSS is live CSS - and separately
 * scans the raw style text for the same shape of mistake. */
const OPEN = '/' + '*';
const CLOSE = '*' + '/';

const out = { missingSelectors: [], unbalanced: [], totalRules: 0 };

/* 1. every selector the browser really has */
const seen = new Set();
for (const sh of document.styleSheets){
  let rules = null;
  try { rules = sh.cssRules; } catch(e){ continue; }
  const walk = rs => {
    for (const r of rs){
      if (r.selectorText) seen.add(r.selectorText.trim());
      if (r.cssRules) walk(r.cssRules);
    }
  };
  walk(rules);
  out.totalRules += rules.length;
}

/* the ones this bug touched, plus their neighbours - if a rule after a broken
   comment is eaten, its siblings are the first casualties */
const WANT = ['.ptcard .lwho', '.ptcard .lwho.win', '.ptcard .lfront',
              '.ptcard .lfront .lffg', '.ptcard .ctext', '.ptcard .cseal'];
out.missingSelectors = WANT.filter(w => !seen.has(w));
out.sawLwho = seen.has('.ptcard .lwho');

/* 2. the raw scan: a close marker that closes nothing means the opener was
      lost, which is exactly the failure that hid this */
const styles = [...document.querySelectorAll('style')].map(s => s.textContent);
styles.forEach((txt, si) => {
  let depth = 0, i = 0;
  while (i < txt.length - 1){
    if (txt[i] === OPEN[0] && txt[i+1] === OPEN[1]){ depth++; i += 2; continue; }
    if (txt[i] === CLOSE[0] && txt[i+1] === CLOSE[1]){
      depth--;
      if (depth < 0){
        out.unbalanced.push({
          styleIndex: si, at: i,
          before: txt.slice(Math.max(0, i - 200), i).replace(/\s+/g, ' ').slice(-200),
          after: txt.slice(i + 2, i + 120).replace(/\s+/g, ' ')
        });
        depth = 0;
      }
      i += 2; continue;
    }
    i++;
  }
  if (depth > 0) out.unbalanced.push({ styleIndex: si, at: -1,
    before: '(comment left OPEN at end of style block)', after: '' });
});

out.styleBlocks = styles.length;
return out;
