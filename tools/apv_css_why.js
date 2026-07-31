/* Is the page stale, or is the rule still being dropped? */
const OPEN = '/' + '*';
const CLOSE = '*' + '/';
const txt = document.querySelector('style').textContent;
const i = txt.indexOf('.ptcard .lwho{');
const out = {
  styleHasRuleText: i >= 0,
  /* the 400 characters the parser sees immediately before the rule - if the
     fix is live this begins with a proper comment opener */
  before: i >= 0 ? txt.slice(Math.max(0, i - 420), i).replace(/\s+/g, ' ') : null,
  hasFixMarker: txt.indexOf('THIS ' + OPEN + ' WAS MISSING') >= 0
};
/* and what the browser parsed, in that neighbourhood */
const seen = [];
for (const sh of document.styleSheets){
  let rules = null; try { rules = sh.cssRules; } catch(e){ continue; }
  for (const r of rules){
    if (r.selectorText && r.selectorText.indexOf('ptcard') >= 0) seen.push(r.selectorText);
  }
}
out.parsedPtcardRules = seen.slice(0, 40);
out.parsedPtcardCount = seen.length;
return out;
