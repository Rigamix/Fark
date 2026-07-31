return {readyState:document.readyState,
  screens:[...document.querySelectorAll('[id^=screen-]')].map(e=>e.id),
  visible:[...document.querySelectorAll('[id^=screen-]')].filter(e=>{
    const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden';}).map(e=>e.id),
  hasG:typeof G!=='undefined', hasS:typeof S!=='undefined',
  hasGetS:typeof _getS!=='undefined',
  hasPatronLines:typeof PATRON_LINES!=='undefined'&&PATRON_LINES.length,
  hsBtn:!!document.getElementById('hsBtnBottom')};
