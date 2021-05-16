var CJ_Utils = {
    isInteger: function(n) {
        return parseInt(n) == n;
    },

    sortSelect2Data: function(data) {
        for (var i = 0; i < data.length; i++) {
            for (var k = 0; k < i; k++) {
                if (data[i].text < data[k].text) {
                    var temp = data[i];
                    data[i] = data[k];
                    data[k] = temp;
                }
            }
        }
        return data;
    },

    submitOnClick: function() {
        $('.submit-on-click').click(function() {
            $(this).closest('form').submit();
            return false;
        });
    }
};

$(document).ready(function() {
    $('[data-toggle="popover"]').popover({
        html: true
    });

    $('[data-toggle="popover"]').click(function () {
        return false;
    });
});