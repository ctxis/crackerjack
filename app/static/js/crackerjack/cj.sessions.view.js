var CJ_SessionsView = {
    init: function() {
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
    }
};