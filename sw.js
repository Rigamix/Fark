const CACHE_NAME = 'gambit-v4';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './Card_ART/Flintlock_face.jpg',
  './Card_ART/Flintlock_face.png',
  './Characters_ART/Bishop.png',
  './Characters_ART/Commoner.png',
  './Characters_ART/Drunkard.png',
  './Characters_ART/Innkeeper.png',
  './Characters_ART/Knight.png',
  './Characters_ART/Merchant.png',
  './Characters_ART/Noble.png',
  './Characters_ART/Peasant.png',
  './Characters_ART/Soldier.png',
  './Environment_ART/gauntlet.png',
  './Environment_ART/main_01.png',
  './Environment_ART/main_02.png',
  './Environment_ART/main_03.png',
  './Environment_ART/match.png',
  './Fonts/Medieval/Enchanted Land.otf',
  './Fonts/Pixel/alagard.ttf',
  './Fonts/Pixel/Minecraft.ttf',
  './Fonts/Pixel/Pixellari.ttf',
  './Match_Art/bank.png',
  './Match_Art/bishop_frame.png',
  './Match_Art/commoner_frame.png',
  './Match_Art/drunkard_frame.png',
  './Match_Art/flee.png',
  './Match_Art/knight_frame.png',
  './Match_Art/Loadout.png',
  './Match_Art/merchant_frame.png',
  './Match_Art/noble_frame.png',
  './Match_Art/patron_frame.png',
  './Match_Art/peasant_frame.png',
  './Match_Art/roll.png',
  './Match_Art/soldier_frame.png',
  './Match_Art/yield.png',
  './Menu_Art/360_F_652771158_vE1ZV6lgjFQzZJIyS9gmSpZbjTYbBTJM.jpg',
  './Menu_Art/checkmark.png',
  './Menu_Art/Gauntlet.png',
  './Menu_Art/Menu.png',
  './Menu_Art/Rules.png',
  './Menu_Art/Settings.png',
  './Menu_Art/Shop.png',
  './Menu_Art/Stamp.png',
  './Menu_Art/iOS icon.png'
];

// Install: cache all assets
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate: clean old caches
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Fetch: network first, cache fallback (so updates always show)
self.addEventListener('fetch', e => {
  e.respondWith(
    fetch(e.request)
      .then(response => {
        // Update cache with fresh response
        const clone = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
        return response;
      })
      .catch(() => caches.match(e.request))
  );
});
