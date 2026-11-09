/* v2: online-first data and document fetches, offline-friendly assets. */
const CACHE = 'penny-scout-live-v2';
const CORE = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './apple-touch-icon.png'];
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== self.location.origin) return;
  const isFeed = url.pathname.endsWith('/data/leads.json');
  const cacheKey = isFeed ? new Request(new URL('./data/leads.json',self.location.href).toString()) : request;
  const freshFirst = isFeed || request.mode === 'navigate' || url.pathname.endsWith('/index.html');
  if (freshFirst) {
    event.respondWith(fetch(request).then(response => {
      if (response.ok) {const copy=response.clone();caches.open(CACHE).then(cache => cache.put(cacheKey,copy));}
      return response;
    }).catch(async () => await caches.match(cacheKey) || await caches.match('./index.html')));
  } else {
    event.respondWith(caches.match(cacheKey).then(cached => cached || fetch(request).then(response => {
      if (response.ok) {const copy=response.clone();caches.open(CACHE).then(cache=>cache.put(cacheKey,copy));}
      return response;
    })));
  }
});
