var CJ_HashcatMasks = {
    template: null,
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

    init: function() {
        // Clone the object - this is what we will use to add new position settings.
        CJ_HashcatMasks.template = $('#mask-template').clone();
        // And remove it.
        $('#mask-template').remove();
        CJ_HashcatMasks.bindMaxCharacters();
        CJ_HashcatMasks.bindSettingActions();
    },

    bindSettingActions: function() {
        $('#mask-placeholder').on('click', '.mask-checkbox', function() {
            CJ_HashcatMasks.updateMasks();
        });

        $('#mask-placeholder').on('input', '.mask-input', function() {
            CJ_HashcatMasks.updateMasks();
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

            CJ_HashcatMasks.generatePositionElements(amount);
        });
    },

    generatePositionElements: function(amount) {
        allExistingPositions = this.getCurrentPositionElements();
        if (allExistingPositions > amount) {
            for (var i = (amount + 1); i <= allExistingPositions; i++) {
                this.removePositionElement(i);
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
    },

    updateMasks: function() {
        masks = this.calculateMasks();
        compiled = this.compileMasks(masks);
        // Check if all positions have been set.
        if (!this.checkMasks(masks)) {
            $('.mask-error').text('Not all positions have a mask assigned to them');
        } else {
            $('.mask-error').text('');
        }
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
        var custom = [];
        var mask = [];
        for (var i = 0; i < masks.length; i++) {
            if (masks[i].custom) {
                var c = custom.length + 1;
                custom.push('-' + c + ' ' + masks[i].mask);
                mask.push('?' + c);
            } else {
                mask.push(masks[i].mask);
            }
        }

        var compiled = custom.join(' ') + ' ' + mask.join('');
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
            mask['mask'] = settings['charset'];
        } else if ($.inArray('binary', settings.masks) >= 0) {
            // If 'all' or 'binary' are checked, they should be on their own as ?l?u < ?a < ?b.
            mask['mask'] = '?b'
        } else if ($.inArray('all', settings.masks) >= 0) {
            // If 'all' or 'binary' are checked, they should be on their own as ?l?u < ?a < ?b.
            mask['mask'] = '?a';
        } else if (settings.masks.length == 1) {
            // If a single option is selected and it's not 'all' (parsed above), then it's not custom and it's the actual mask.
            mask['mask'] = this.validMasks[settings.masks[0]];
        } else if (settings.masks.length > 0) {
            // Combine all masks under a single custom one.
            mask['custom'] = true;
            for (var i = 0; i < settings.masks.length; i++) {
                mask['mask'] += this.validMasks[settings.masks[i]];
            }
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
    }
};