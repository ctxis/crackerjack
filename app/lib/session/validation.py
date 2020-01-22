class SessionValidation:
    def validate(self, session):
        errors = []

        # First check if hashes have been uploaded.
        if session['hashes_in_file'] == 0:
            errors.append('No hashes have been uploaded')

        # Now we check the hashtype.
        if session['hashcat']['hashtype'] == '':
            errors.append('No hash type has been selected')

        # Check attack mode settings.
        if session['hashcat']['mode'] == 0:
            # Do checks for wordlist attacks.
            if session['hashcat']['wordlist'] == '':
                errors.append('No wordlist has been selected')
        else:
            # Do checks for bruteforce attacks.
            if session['hashcat']['mask'] == '':
                errors.append('No mask has been set')

        # Check termination date
        if session['terminate_at'] is None:
            errors.append('No termination date has been set')

        return errors
