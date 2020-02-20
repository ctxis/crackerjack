/*
    https://stackoverflow.com/questions/3717793/javascript-file-upload-size-validation
*/
var CJ_FileSize = {
    fileElement: null,
    errorElement: null,
    sizeMessageElement: null,
    maxSize: 100, // In MB.

    init: function(fileElement, errorElement, sizeMessageElement, maxSize) {
        this.fileElement = fileElement;
        this.errorElement = errorElement;
        this.sizeMessageElement = sizeMessageElement;
        this.maxSize = maxSize;

        this.bind();
    },

    bind: function() {
        if (!window.FileReader) {
            $(this.errorElement).text('FileReader API is not supported by your browser.');
            return false;
        }

        var el = $(this.fileElement);
        if (!el) {
            $(this.errorElement).text('Could not locate the file element on the page.');
            return false;
        } else if (!el[0].files) {
            $(this.errorElement).text('Your browser does not support the `files` property');
            return false;
        }

        $(this.fileElement).change(function() {
            CJ_FileSize.checkFileSize();
        });
    },

    checkFileSize: function() {
        var el = $(this.fileElement)[0];
        if (!el.files[0]) {
            // No file selected.
            return false;
        }

        // This will be in bytes.
        var fileSize = el.files[0].size;

        // MB.
        var friendlySize = Math.ceil(fileSize / 1024 / 1024);

        $(this.sizeMessageElement).addClass('d-none');
        if (friendlySize > this.maxSize) {
            $(this.sizeMessageElement).find('.file-size').text(friendlySize);
            $(this.sizeMessageElement).find('.file-limit').text(this.maxSize);
            $(this.sizeMessageElement).removeClass('d-none');
            return false;
        }
        return true;
    }
};