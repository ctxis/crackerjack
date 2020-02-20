var CJ_Select2_Wordlists = {
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

        var found = CJ_Select2_Wordlists.select2Search(searchFor, searchIn, searchInId);

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

var CJ_SessionsWordlist = {
    init: function(wordlists, selected_wordlist, selected_rule) {
        this.bindWordlists(wordlists, selected_wordlist);
        this.bindRules(selected_rule);
    },

    bindRules: function(selected_rule) {
        $('#rule').select2({}).val(selected_rule).trigger('change');
    },

    bindWordlists: function(wordlists, selected_wordlist) {
        wordlists = this.processWordlists(wordlists);
        $('#wordlist').select2({
            placeholder: 'Select wordlist',
            data: wordlists,
            escapeMarkup: CJ_Select2_Wordlists.escapeMarkup,
            templateResult: CJ_Select2_Wordlists.templateResult,
            templateSelection: CJ_Select2_Wordlists.templateSelection,
            matcher: CJ_Select2_Wordlists.matcher
        }).val(selected_wordlist).trigger('change');
    },

    processWordlists: function(wordlists) {
        // Convert keys to properties.
        data = [];
        for (var name in wordlists) {
            if (wordlists.hasOwnProperty(name)) {
                data.push({
                    id: name,
                    text: name,
                    size: wordlists[name].size_human
                });
            }
        }

        return CJ_Utils.sortSelect2Data(data);
    }
};