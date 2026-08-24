const CACHE_NAME = 'vkvtt-shell-v66-2-sync-1';
const APP_SHELL = [
  '/vkvtt/',
  '/vkvtt/index.html',
  '/vkvtt/manifest.webmanifest',
  '/vkvtt/icon-192.png',
  '/vkvtt/icon-512.png',
  '/vkvtt/v66-home.css',
  '/vkvtt/v66-design-system.css',
  '/vkvtt/v66-home.js',
  '/vkvtt/v66-home-cloud.js',
  '/vkvtt/v66-ui.js',
  '/vkvtt/period-notifications.js'
  './v66-home-shell-v662.css',
  './v66-home-shell-v662.js',
  './swamiji-portrait.jpg',
];
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL)));
  self.skipWaiting();
});
self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  event.respondWith(fetch(event.request).then(response => {
    const copy = response.clone();
    caches.open(CACHE_NAME).then(cache => cache.put(event.request, copy));
    return response;
  }).catch(() => caches.match(event.request).then(hit => hit || (event.request.mode === 'navigate' ? caches.match('/vkvtt/index.html') : undefined))));
});
self.addEventListener('message', event => {
  const d = event.data || {};
  if (d.type !== 'VKVTT_SHOW_NOTIFICATION' || !d.title) return;
  event.waitUntil(self.registration.showNotification(d.title, {
    body: d.body || '',
    icon: '/vkvtt/icon-192.png',
    badge: '/vkvtt/icon-192.png',
    tag: d.tag || 'vkvtt-period-reminder',
    renotify: false,
    data: {url: d.url || '/vkvtt/'}
  }));
});
self.addEventListener('notificationclick', event => {
  event.notification.close();
  const url = event.notification.data?.url || '/vkvtt/';
  event.waitUntil(clients.matchAll({type:'window',includeUncontrolled:true}).then(list => {
    for (const c of list) { if ('focus' in c) { c.navigate(url); return c.focus(); } }
    return clients.openWindow ? clients.openWindow(url) : undefined;
  }));
});
