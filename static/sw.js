const CACHE_NAME = 'todo-v2';
const URLS = ['/', '/inbox/', '/today/', '/upcoming/', '/done/', '/projects/'];

// Force clear old caches on install
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheName.includes('solo-todo') || cacheName === 'todo-v1') {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      return caches.open(CACHE_NAME).then(c => c.addAll(URLS));
    })
  );
});
self.addEventListener('fetch', (event) => {
  const req = event.request;

  // Never handle non-GET requests via cache; let them hit the network
  if (req.method !== 'GET') {
    event.respondWith(fetch(req));
    return;
  }

  // For GET requests: cache-first with network fallback, then cache the result
  event.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;
      return fetch(req)
        .then((res) => {
          // Only cache successful GET responses
          if (res && res.ok) {
            const copy = res.clone();
            caches.open(CACHE_NAME).then((c) => {
              c.put(req, copy).catch(() => {});
            });
          }
          return res;
        })
        .catch(() => caches.match('/'));
    })
  );
});