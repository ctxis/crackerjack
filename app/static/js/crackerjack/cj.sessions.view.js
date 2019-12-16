var CJ_SessionsView = {
    autoRefreshInterval: 5000,

    init: function() {
        this.bindFormAction();
        this.bindRawProgress();
        this.bindAutoRefresh();
    },

    bindFormAction: function() {
        $('.form-action').click(function() {
            // Add an extra check for the 'reset' link.
            if ($(this).data('action') == 'reset') {
                if (!confirm("This will kill the current screen session. You should only run this if you cannot get hashcat to start.\n\nAre you sure you want to do this?")) {
                    return false;
                }
            }
            $('#action').val($(this).data('action'));
            $('#form-action').submit();
            return false;
        });
    },

    bindRawProgress: function() {
        $('.raw-progress').click(function() {
            if ($('#raw-progress').hasClass('d-none')) {
                $('#raw-progress').removeClass('d-none');
            } else {
                $('#raw-progress').addClass('d-none');
            }
            return false;
        });
    },

    bindAutoRefresh: function() {
        if (!$('#autorefresh').length) {
            return false;
        }

        // Set a timeout if the element exists - it should only be there if hashcat is running.
        setInterval(function() {
            if ($('#autorefresh').is(':checked')) {
                location.reload();
            }
        }, this.autoRefreshInterval);
    }
};