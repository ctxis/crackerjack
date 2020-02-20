var CJ_Select2_HashFiles = {
    escapeMarkup: function (markup) {
        return markup;
    },

    templateResult: function (item) {
        if (item.id == -1) {
            return '';
        }
        return '<span>' + item.text + '</span><span class="float-right subtext">' + item.size + '</span>';
    },

    templateSelection: function (item) {
        if (item.id == '') {
            return '';
        }
        return item.text + ' (' + item.size + ')';
    },

    matcher: function (params, data) {
        if ($.trim(params.term) === '') {
            return data;
        } else if (typeof data.text === 'undefined') {
            return null;
        }

        // What we are searching for - to lowercase to make our life easier.
        searchFor = params.term.toString().toLowerCase().trim();
        searchIn = data.text.toString().toLowerCase();
        searchInId = data.id.toString();

        var found = CJ_Select2_HashFiles.select2Search(searchFor, searchIn, searchInId);

        if (found) {
            return modifiedData = $.extend({}, data, true);
        }

        return null;
    },

    select2Search: function(searchTerms, searchInText, searchInId) {
        // I could use regular expressions but I refuse to.
        // https://blog.codinghorror.com/regular-expressions-now-you-have-two-problems/

        searchTerms = searchFor.split(' ');
        // See if ALL terms appear in the element. This is helpful when you want to search for
        // "Oper Syst Lin" rather than the whole text.
        var count = 0;
        for (var i = 0; i < searchTerms.length; i++) {
            if (searchInText.indexOf(searchTerms[i]) > -1) {
                count++;
            }
        }
        found = (count == searchTerms.length);

        return found;
    }
};

var CJ_SessionsHashes = {
    init: function(uploaded_hashfiles) {
        this.bindHashFiles(uploaded_hashfiles);
        this.bindModes();
    },

    bindModes: function() {
        this.setModes();
        $('.mode-option').click(function() {
            CJ_SessionsHashes.setModes();
            return true;
        });
    },

    setModes: function() {
        mode = $("input[name='mode']:checked").val();
        if (typeof mode == 'undefined') {
            $('#mode-upload').prop('checked', true);
            mode = 0;
        }

        if (mode == 0) {
            $('.box-mode-upload').removeClass('d-none');
            $('.box-mode-paste').addClass('d-none');
            $('.box-mode-remote').addClass('d-none');
        } else if (mode == 1) {
            $('.box-mode-upload').addClass('d-none');
            $('.box-mode-paste').removeClass('d-none');
            $('.box-mode-remote').addClass('d-none');
        } else if (mode == 2) {
            $('.box-mode-upload').addClass('d-none');
            $('.box-mode-paste').addClass('d-none');
            $('.box-mode-remote').removeClass('d-none');
        }
    },

    bindHashFiles: function(uploaded_hashfiles) {
        hashfiles = this.processHashFiles(uploaded_hashfiles);
        $('#remotefile').select2({
            placeholder: 'Select uploaded hashes',
            data: hashfiles,
            escapeMarkup: CJ_Select2_HashFiles.escapeMarkup,
            templateResult: CJ_Select2_HashFiles.templateResult,
            templateSelection: CJ_Select2_HashFiles.templateSelection,
            matcher: CJ_Select2_HashFiles.matcher
        }).trigger('change');
    },

    processHashFiles: function(hashfiles) {
        // Convert keys to properties.
        data = [];
        for (var name in hashfiles) {
            if (hashfiles.hasOwnProperty(name)) {
                data.push({
                    id: name,
                    text: name,
                    size: hashfiles[name].size_human
                });
            }
        }

        return CJ_Utils.sortSelect2Data(data);
    }
};

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