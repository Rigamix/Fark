/* SELF-DESTRUCT STUB — the painted game's service worker cached the whole
   origin and kept serving stale builds. Any browser that still has the old
   SW installed will fetch this update, wipe every cache, unregister itself
   and reload its tabs. Keep this file until playtesters stop reporting
   stale pages; the greybox proto registers no service worker. */
self.addEventListener('install',function(){self.skipWaiting();});
self.addEventListener('activate',function(e){
  e.waitUntil(
    caches.keys().then(function(ks){return Promise.all(ks.map(function(k){return caches.delete(k);}));})
    .then(function(){return self.registration.unregister();})
    .then(function(){return self.clients.matchAll({type:'window'});})
    .then(function(cs){cs.forEach(function(c){try{c.navigate(c.url);}catch(err){}});})
  );
});
