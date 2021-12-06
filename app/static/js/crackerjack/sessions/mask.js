var CJ_HashcatMasks = {
    template: null,

    maxCustomCharsets: 4,

    validMasks: {
        'lower': '?l',
        'upper': '?u',
        'digits': '?d',
        'hexlower': '?h',
        'hexupper': '?H',
        'special': '?s',
        'all': '?a',
        'binary': '?b'
    },

    validReverseMasks: {
        '?l': 'lower',
        '?u': 'upper',
        '?d': 'digits',
        '?h': 'hexlower',
        '?H': 'hexupper',
        '?s': 'special',
        '?a': 'all',
        '?b': 'binary'
    },

    // This is here so that when we're parsing a compiled mask (ie someone re-visits the settings page) we don't trigger
    // the mask compilation process while checking the boxes programmatically.
    disableEvents: false,

    init: function(selected_masklist) {
        // Clone the object - this is what we will use to add new position settings.
        this.template = $('#mask-template').clone();
        // And remove it.
        $('#mask-template').remove();
        this.bindModes();
        this.bindMasklist(selected_masklist);
        this.bindMaxCharacters();
        this.bindSettingActions();
        this.bindCompiledMask();
    },

    bindModes: function() {
        this.setModes();
        $('.mode-option').click(function() {
            CJ_HashcatMasks.setModes();
            return true;
        });
    },

    bindMasklist: function(selected_masklist) {
        $('#masklist').select2({}).val(selected_masklist).trigger('change');
    },

    setModes: function() {
        mode = $("input[name='mask_type']:checked").val();
        if (typeof mode == 'undefined') {
            $('#mode-global').prop('checked', true);
            mode = 0;
        }

        if (mode == 0) {
            $('.box-mode-custom').addClass('d-none');
        } else if (mode == 1) {
            $('.box-mode-custom').addClass('d-none');
        } else if (mode == 2) {
            $('.box-mode-custom').removeClass('d-none');
        }
    },

    bindCompiledMask: function() {
        $('#compiled-mask').on('keyup', function() {
            CJ_HashcatMasks.parseFromString($(this).val());
        });
    },

    bindSettingActions: function() {
        $('#mask-placeholder').on('click', '.mask-checkbox', function() {
            if (!CJ_HashcatMasks.disableEvents) {
                CJ_HashcatMasks.updateMasks();
            }
        });

        $('#mask-placeholder').on('input', '.mask-input', function() {
            if (!CJ_HashcatMasks.disableEvents) {
                CJ_HashcatMasks.updateMasks();
            }
        });
    },

    bindMaxCharacters: function() {
        // The on('input') event works only in HTML5 as that's the only way to prevent triggering twice if you put
        // a listener for both change/keyup. See:
        // https://stackoverflow.com/questions/11276429/jquery-code-triggered-twice-for-bindkeyup-change-when-pressing-key
        $('#mask-max-characters').on('input', function() {
            amount = parseInt($(this).val());
            if (amount < 0) {
                return false;
            }

            if (!CJ_HashcatMasks.disableEvents) {
                CJ_HashcatMasks.generatePositionElements(amount, false);
            }
        });
    },

    clearFields: function() {
        allExistingPositions = this.getCurrentPositionElements();
        for (var i = 1; i <= allExistingPositions; i++) {
            var element = this.getPositionElement(i);
            $(element).find('.mask-checkbox').prop('checked', false);
            $(element).find('.mask-charset').val('');
        }
    },

    generatePositionElements: function(amount, clearFields) {
        allExistingPositions = this.getCurrentPositionElements();
        if (allExistingPositions > amount) {
            for (var i = (amount + 1); i <= allExistingPositions; i++) {
                this.removePositionElement(i);
            }
            if (clearFields) {
                this.clearFields();
            }
            // No need to keep going as we won't be adding any new elements.
            return true;
        }

        // The position value is (i+1) so we're going to start with i = 1 rather than i = 0.
        for (var i = 1; i <= amount; i++) {
            if (this.positionElementExists(i)) {
                continue;
            }

            template = CJ_HashcatMasks.template.clone();

            // Remove non-required classes to prevent making our life difficult further down.
            $(template).removeClass('d-none').attr('id', '');

            // Add parent class to identify position.
            $(template).addClass('mask-position-' + i);

            // Set the text for Position X.
            $(template).find('.position-number').text(i);

            // Set the ID's for labels/inputs.
            $(template).find('.mask-checkbox, .mask-label, .mask-input').each(function() {
                var attribute = ($(this).prop('tagName') == 'INPUT') ? 'id' : 'for';
                $(this).attr(attribute, 'mask-check-position-' + $(this).data('mask') + '-' + i);
            });

            // Add position element.
            $('#mask-placeholder').append(template);
        }

        if (clearFields) {
            this.clearFields();
        }
    },

    updateMasks: function() {
        var existingErrors = [];
        $('.mask-error').text('');

        masks = this.calculateMasks();
        compiled = this.compileMasks(masks);
        // Check if all positions have been set.
        var areMasksValid = this.checkMasks(masks);

        var error = $('.mask-error').text();
        if (error.length > 0) {
            existingErrors.push(error);
        }

        if (!areMasksValid) {
            existingErrors.push('Not all positions have a mask assigned to them');
        } else {
            $('.mask-error').text('');
        }

        $('.mask-error').html(existingErrors.join("<br>"));

        $('#compiled-mask').val(compiled);
    },

    checkMasks: function(masks) {
        var all = this.getCurrentPositionElements();
        var actual = 0;
        for (var i = 0; i < masks.length; i++) {
            if (masks[i].mask.length > 0) {
                actual++;
            }
        }

        return (all == actual);
    },

    compileMasks: function(masks) {
        var groupedMasks = [];
        var mask = [];
        for (var i = 0; i < masks.length; i++) {
            if (masks[i].custom) {
                // If this is a custom mask, check if it exists in the grouped array first.
                k = groupedMasks.indexOf(masks[i].mask);
                if (k == -1) {
                    // It's the first occurrence of this mask.
                    groupedMasks.push(masks[i].mask);
                    // Now we get its position in the array. If it's the first element it will return zero (0), which
                    // means that its 'charset' number will be index+1, ie 1.
                    k = groupedMasks.indexOf(masks[i].mask);
                }
                // We increment k by 1 to get the 'charset' number for the command line, ie -1 XXX -2 XXX -3 XXX etc.
                mask.push('?' + (++k));
            } else {
                mask.push(masks[i].mask);
            }
        }

        if (groupedMasks.length > CJ_HashcatMasks.maxCustomCharsets) {
            $('.mask-error').text('You cannot have more than ' + CJ_HashcatMasks.maxCustomCharsets + ' custom charsets (-1, -2, -3, ...etc)');
        } else {
            $('.mask-error').text('');
        }

        // Compile custom masks.
        compiled = [];
        for (var i = 0; i < groupedMasks.length; i++) {
            compiled.push('-' + (i + 1) + ' ' + groupedMasks[i]);
        }

        var compiled = compiled.join(' ') + ' ' + mask.join('');
        return compiled;
    },

    gatherSettings: function() {
        allExistingPositions = this.getCurrentPositionElements();
        settings = [];
        for (var i = 1; i <= allExistingPositions; i++) {
            if (!this.positionElementExists(i)) {
                // Something went wrong - return empty settings.
                alert('There is a mismatch between current position count and element count - This should not have happened');
                return [];
            }

            setting = [];
            var element = this.getPositionElement(i);

            // Get checked boxes.
            $(element).find('input:checked').each(function() {
                setting.push($(this).data('mask'));
            });

            // Get custom charset.
            var charset = $(element).find('.mask-charset').val().trim();

            settings.push({
                'position': i,
                'masks': setting,
                'charset': charset
            });
        }

        return settings;
    },

    calculateMasks: function() {
        var settings = this.gatherSettings();
        var masks = [];
        for (var i = 0; i < settings.length; i++) {
            var mask = this.calculateSingleMask(settings[i]);
            masks.push(mask);
        }
        return masks;
    },

    calculateSingleMask: function(settings) {
        mask = {
            'position': settings['position'],
            'mask': '',
            'custom': false
        };

        // If a charset is selected, ignore all other selections.
        if (settings['charset'].length > 0) {
            mask['custom'] = true;
            // As per https://hashcat.net/wiki/doku.php?id=mask_attack#masks
            // The custom '?' is represented as '??'
            mask['mask'] = settings['charset'].replace('?', '??');
        } else if (settings.masks.indexOf('binary') >= 0) {
            // If 'all' or 'binary' are checked, they should be on their own as ?l?u < ?a < ?b.
            mask['mask'] = '?b'
        } else if (settings.masks.indexOf('all') >= 0) {
            // If 'all' or 'binary' are checked, they should be on their own as ?l?u < ?a < ?b.
            mask['mask'] = '?a';
        } else if (settings.masks.length == 1) {
            // If a single option is selected and it's not 'all' (parsed above), then it's not custom and it's the actual mask.
            mask['mask'] = this.validMasks[settings.masks[0]];
        } else if (settings.masks.length > 0) {
            // Combine all masks under a single custom one.
            mask['custom'] = true;
            var data = [];
            for (var i = 0; i < settings.masks.length; i++) {
                data.push(this.validMasks[settings.masks[i]]);
            }
            // Sort array - this will help us group identical masks.
            data.sort();
            mask['mask'] = data.join('');
        }

        return mask;
    },

    removePositionElement: function(position) {
        $('.mask-position-' + position).remove();
    },

    getPositionElement: function(position) {
        return $('.mask-position-' + position);
    },

    positionElementExists: function(position) {
        return $('.mask-position-' + position).length > 0;
    },

    getCurrentPositionElements: function() {
        return $('.mask-position').length;
    },

    isInteger: function(n) {
        // This function exists in CJ_Utils too, but I wanted to make this one standalone.
        return parseInt(n) == n;
    },

    parseFromString: function(compiled) {
        if (compiled.length == 0) {
            return true;
        }

        // Parse the compiled mask into an object that's easier to use.
        data = this.processCompiledMask(compiled);

        // Update the user interface now.
        this.updateUI(data);
    },

    setCheckboxValue: function(position, mask, value) {
        if (!this.positionElementExists(position)) {
            return false;
        }
        var element = this.getPositionElement(position);

        $(element).find('#mask-check-position-' + mask + '-' + position).prop('checked', value);

        return true;
    },

    setTextValue: function(position, mask, value) {
        if (!this.positionElementExists(position)) {
            return false;
        }
        var element = this.getPositionElement(position);

        $(element).find('#mask-check-position-' + mask + '-' + position).val(value);
    },

    updateUI: function(data) {
        this.generatePositionElements(data.positions, true);
        $('#mask-max-characters').val(data.positions);

        masks = data.mask.split('?');
        for (var i = 0; i < masks.length; i++) {
            // This is a bit weird as because the first character is '?', the actual data will start coming in from
            // index 1. So we don't need to (i+1) to get the _actual_ charset.
            if (masks[i].length == 0) {
                continue;
            }

            if (this.isInteger(masks[i])) {
                // It's a custom group.
                var hasQuestionMark = false;
                var groupMask = data.groups[masks[i] - 1];
                // Remove all instances of official masks, but first check for a double question mark ??.
                if (groupMask.indexOf('??') >= 0) {
                    hasQuestionMark = true;
                    groupMask = groupMask.replace('??', '');
                }
                for (var charset in CJ_HashcatMasks.validReverseMasks) {
                    if (CJ_HashcatMasks.validReverseMasks.hasOwnProperty(charset)) {
                        if (groupMask.indexOf(charset) >= 0) {
                            // Exists - set the checkbox.
                            this.setCheckboxValue(i, this.validReverseMasks[charset], true);
                            // And remove it.
                            groupMask = groupMask.replace(charset, '');
                        }
                    }
                }
                // If there's anything left, it's a custom charset.
                if (hasQuestionMark) {
                    groupMask = groupMask + '?';
                }
                if (groupMask.length > 0) {
                    this.setTextValue(i, 'charset', groupMask);
                }
            } else {
                this.setCheckboxValue(i, this.validReverseMasks['?' + masks[i]], true);
            }
        }

        if (data.groups.length > CJ_HashcatMasks.maxCustomCharsets) {
            $('.mask-error').text('You cannot have more than ' + CJ_HashcatMasks.maxCustomCharsets + ' custom charsets (-1, -2, -3, ...etc)');
        } else {
            $('.mask-error').text('');
        }

        CJ_HashcatMasks.disableEvents = false;
    },

    processCompiledMask: function(compiled) {
        // Remove any double spaces.
        compiled = compiled.replace(/  /g, ' ');

        // Example mask. The last bit is the actual mask and the start is any custom sets.
        // -1 ?l?s -2 ?l ?u -3 ?d?s -4 ab??d ?1?u?2?3?4?l?u?d
        var info = compiled.split(' ');

        // The last element is the actual mask. Retrieve it and remove it from the array.
        var actualMask = info.pop().trim();

        /*
            We should be left with an array of:
                -1
                ?l?s
                -2
                ?l
                ?u
                -3
                ?d?s
                -4
                a-b??d
        */
        var charset = null;
        var allCharsets = [];
        while (info.length > 0) {
            var part = info.shift();
            if (part.length == 2 && part.charAt(0) == '-' && this.isInteger(part.charAt(1))) {
                // Save any previously parsed charset.
                if (charset !== null) {
                    charset['mask'] = charset['mask'].trim();
                    allCharsets.push(charset);
                }

                // This is a custom charset.
                charset = {
                    position: parseInt(part.charAt(1)),
                    mask: ''
                };
            } else {
                if (charset !== null) {
                    charset['mask'] += ' ' + part;
                }
            }
        }

        if (charset !== null) {
            charset['mask'] = charset['mask'].trim();
            allCharsets.push(charset);
        }

        // Now sort, just in case it's not in the right order.
        for (var i = 0; i < allCharsets.length; i++) {
            for (var k = 0; k < allCharsets.length - 1; k++) {
                if (allCharsets[i]['position'] < allCharsets[k]['position']) {
                    var swap = allCharsets[i];
                    allCharsets[i] = allCharsets[k];
                    allCharsets[k] = swap;
                }
            }
        }

        // And now put into the final object.
        // The number of question marks is the number of positions.
        // https://stackoverflow.com/questions/4009756/how-to-count-string-occurrence-in-string
        var positions = (actualMask.match(/\?/g) || []).length;

        var data = {
            'mask': actualMask,
            'positions': positions,
            'groups': []
        };

        for (var i = 0; i < allCharsets.length; i++) {
            data['groups'].push(allCharsets[i].mask);
        }

        return data;
    }
};

var CJ_SessionsMask = {
    init: function() {
        this.bindForm();
        this.bindIncrements();
    },

    bindIncrements: function() {
        $('#enable_increments').on('change', function() {
            $('#increment-min').prop('disabled', !$(this).is(':checked'));
            $('#increment-max').prop('disabled', !$(this).is(':checked'));
        });
    },

    bindForm: function() {
        $('#setup-hashcat').validate();
    }
};