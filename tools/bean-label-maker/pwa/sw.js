/* 원두 라벨 메이커 — 오프라인 캐시 + 안드로이드 공유 대상 수신 */
const CACHE = 'beanlabel-v1';
const SHELL = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png'];
const SHARE = 'beanlabel-shared';

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== CACHE && k !== SHARE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // 갤러리/카메라에서 "공유 → 원두라벨" 로 들어오는 경로
  if (e.request.method === 'POST' && url.pathname.endsWith('/share-target')) {
    e.respondWith((async () => {
      try{
        const fd = await e.request.formData();
        const files = fd.getAll('photos').filter(f => f && f.size > 0);
        const cache = await caches.open(SHARE);
        for (const k of await cache.keys()) await cache.delete(k);
        let n = 0;
        for (const f of files.slice(0, 6)) {
          await cache.put('shared-' + n,
            new Response(f, { headers: { 'content-type': f.type || 'image/jpeg' } }));
          n++;
        }
        return Response.redirect('./?shared=' + n, 303);
      }catch(err){ return Response.redirect('./?shared=0', 303); }
    })());
    return;
  }

  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request).then(hit => hit || fetch(e.request).then(res => {
      if (res.ok && url.origin === location.origin) {
        const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy));
      }
      return res;
    }).catch(() => caches.match('./index.html')))
  );
});
