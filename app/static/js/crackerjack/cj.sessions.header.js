var CJ_SessionsHeader = {
    autoRefreshInterval: 5000,
    terminateAt: new Date(),

    init: function(terminateAt) {
        this.terminateAt = new Date(terminateAt);

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

            switch ($(this).data('action')) {
                case 'start':
                case 'restore':
                case 'resume':
                    if (CJ_SessionsHeader.terminateAt < new Date()) {
                        alert("The termination date for this session has passed. If you want to keep using this session please set a future date in the session's settings");
                        return false;
                    }
                    break;
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