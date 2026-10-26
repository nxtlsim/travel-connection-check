const C='tcc-shell-v3',SHELL=['./','index.html','manifest.json','icon-192.png','icon-512.png','rates.json'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(SHELL.map(u=>new Request(u,{cache:'reload'})))));self.skipWaiting()});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))));self.clients.claim()});
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==location.origin)return;
const key=u.pathname.endsWith('rates.json')?new Request(u.origin+u.pathname):e.request;
e.respondWith(fetch(new Request(e.request.url,{cache:'no-cache',credentials:'same-origin'})).then(r=>{if(r.ok){const cp=r.clone();caches.open(C).then(c=>c.put(key,cp))}return r}).catch(()=>caches.match(key,{ignoreSearch:true}).then(r=>r||caches.match('index.html'))))});
