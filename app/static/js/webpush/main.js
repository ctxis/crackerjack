var WebPush = {
    csrfToken: '',
    vapidKey: '',
    swPath: '',
    registerEndpoint: '',
    swRegistration: null,
    isSubscribed: false,
    appServerKey: '',

    init: function(csrfToken, vapidPublicKey, swPath, registerEndpoint) {
        this.csrfToken = csrfToken;
        this.vapidKey = vapidPublicKey;
        this.swPath = swPath;
        this.registerEndpoint = registerEndpoint;
        this.appServerKey = this.urlB64ToUint8Array(vapidPublicKey);
        this.register();
    },

    urlB64ToUint8Array: function(base64String) {
        var padding = '='.repeat((4 - base64String.length % 4) % 4);
        var base64 = (base64String + padding)
            .replace(/\-/g, '+')
            .replace(/_/g, '/');

        var rawData = window.atob(base64);
        var outputArray = new Uint8Array(rawData.length);

        for (var i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    },

    register: function() {
        if ('serviceWorker' in navigator && 'PushManager' in window) {
            navigator.serviceWorker.register(WebPush.swPath).then(function(swReg) {
                WebPush.swRegistration = swReg;
                WebPush.initialiseUI();
            }).catch(function(error) {
                console.error('Service Worker Error', error);
            });
        } else {
            console.warn('Push messaging is not supported');
        }
    },

    initialiseUI: function() {
        WebPush.swRegistration.pushManager.getSubscription().then(function(subscription) {
            WebPush.isSubscribed = !(subscription === null);

            if (WebPush.isSubscribed) {
                // User is subscribed.
            } else {
                WebPush.subscribeUser();
            }
        });
    },

    subscribeUser: function() {
        this.swRegistration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: WebPush.appServerKey
        }).then(function(subscription) {
            WebPush.updateSubscriptionOnServer(subscription);
            WebPush.isSubscribed = true;
        }).catch(function(err) {
            console.error('Failed to subscribe the user: ', err);
        });
    },

    updateSubscriptionOnServer: function(subscription) {
        var rawKey = subscription.getKey ? subscription.getKey('p256dh') : '';
        var key = rawKey ? this.Base64EncodeUrl(btoa(String.fromCharCode.apply(null, new Uint8Array(rawKey)))) : '';
        var rawAuthSecret = subscription.getKey ? subscription.getKey('auth') : '';
        var authSecret = rawAuthSecret ? this.Base64EncodeUrl(btoa(String.fromCharCode.apply(null, new Uint8Array(rawAuthSecret)))) : '';

        $.ajax({
            url: WebPush.registerEndpoint,
            cache: false,
            method: 'post',
            dataType: 'json',
            data: {
                csrf_token: WebPush.csrfToken,
                user_key: key,
                user_authsecret: authSecret,
                user_endpoint: subscription.endpoint
            }
        }).done(function(data) {
            // All done.
        });
    },

    Base64EncodeUrl: function(str) {
        return str.replace(/\+/g, '-').replace(/\//g, '_').replace(/\=+$/, '');
    }
};