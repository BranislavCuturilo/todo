const CACHE_NAME = 'solo-todo-v1';
const URLS = ['/', '/inbox/', '/today/', '/upcoming/', '/done/', '/projects/'];
self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(URLS)));
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