var CJ_SessionsView = {
    statusCheckInterval: 5000,
    statusUrl: '',
    sessionStatus: -1,

    init: function(statusUrl, sessionStatus) {
        this.bindRestoreHistory();
        this.initStatusCheck();
        this.statusUrl = statusUrl;
        this.sessionStatus = sessionStatus;
    },

    bindRestoreHistory: function() {
        $('.apply-history-settings').click(function() {
            if (confirm("Are you sure you want to apply these settings to your current session?")) {
                $('#form-apply-history-' + $(this).data('id')).submit();
                return false;
            }
            return false;
        });
    },

    initStatusCheck: function() {
        setTimeout(
            function() {
                CJ_SessionsView.doStatusCheck(CJ_SessionsView.statusUrl);
            },
            CJ_SessionsView.statusCheckInterval
        );
    },

    doStatusCheck: function(statusUrl) {
        $.ajax({
            url: statusUrl,
            method: 'GET',
            cache: false,
            dataType: 'json'
        }).done(function(data) {
            if (data && data.result && data.result == true) {
                if (data.status != CJ_SessionsView.sessionStatus) {
                    location.reload();
                    return true;
                }
            }
            CJ_SessionsView.initStatusCheck();
        });
    }
};