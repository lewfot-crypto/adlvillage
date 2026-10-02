const CACHE='adeline-0.47_데모-84a5114e';
const FILES=['./','index.html','manifest.json','pwa/icon-192.png','pwa/icon-512.png','pwa/apple-touch-icon.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)));self.skipWaiting()});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
// 인터넷이 되면 새 파일을 먼저 받고, 안 되면 저장해 둔 파일로 실행
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;
  e.respondWith(fetch(e.request).then(r=>{if(r.ok){const cp=r.clone();caches.open(CACHE).then(c=>c.put(e.request,cp))}return r}).catch(()=>caches.match(e.request,{ignoreSearch:true}).then(m=>m||caches.match('index.html'))))});
