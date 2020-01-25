self.addEventListener('push', function(event) {
    var data = {};
    if (event.data) {
        data = event.data.json();
    }

    var title = data.title || 'Invalid title';
    var message = data.body || 'Invalid body';
    var url = data.url || '';
    var icon = data.icon || '';

    event.waitUntil(
        self.registration.showNotification(title, {
            body: message,
            icon: icon,
            badge: icon,
            data: {
                url: url
            }
        })
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();

    event.waitUntil(
        clients.openWindow(event.notification.data.url)
    );
});