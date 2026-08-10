/* 极简 Service Worker：网络优先，失败回退缓存（离线壳）。latest.json 与音频永不走缓存（保证最新）。 */
const CACHE = 'weather-v1';

self.addEventListener('install', function (e) {
  self.skipWaiting();
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', function (e) {
  var url = new URL(e.request.url);
  // 动态内容始终走网络（latest.json 与 .mp3 音频永不走缓存，保证最新）
  if (url.pathname.indexOf('latest.json') >= 0 || /\.mp3(\?|$)/.test(url.pathname)) {
    return;
  }
  e.respondWith(
    caches.open(CACHE).then(function (cache) {
      return fetch(e.request).then(function (res) {
        if (e.request.method === 'GET' && res.ok && url.origin === location.origin) {
          cache.put(e.request, res.clone());
        }
        return res;
      }).catch(function () {
        return cache.match(e.request);
      });
    })
  );
});
