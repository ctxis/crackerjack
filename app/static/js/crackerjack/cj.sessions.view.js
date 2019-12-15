var CJ_SessionsView = {
    init: function() {
        $('.form-action').click(function() {
            $('#action').val($(this).data('action'));
            $('#form-action').submit();
            return false;
        });
    }
};