import collections


class HashcatManager:
    def __init__(self, shell, hashcat_binary, status_interval=10):
        self.shell = shell
        self.hashcat_binary = hashcat_binary
        self.status_interval = 10 if int(status_interval) <= 0 else int(status_interval)

    def get_supported_hashes(self):
        output = self.shell.execute([self.hashcat_binary, '--help'], user_id=0)

        # Split lines using \n and run strip against all elements of the list.
        lines = list(map(str.strip, output.split("\n")))
        hashes = self.__parse_supported_hashes(lines)
        return hashes

    def __parse_supported_hashes(self, lines):
        found = False
        hashes = {}
        for line in lines:
            if line == '- [ Hash modes ] -':
                found = True
            elif found and line == '' and len(hashes) > 0:
                break
            elif found and line != '':
                if line[0] == '#' or line[0] == '=':
                    continue

                # We found a line that has a code/type/description - parse it.
                info = self.__parse_hash_line(line)
                if info is False:
                    continue

                if not info['category'] in hashes:
                    hashes[info['category']] = {}

                hashes[info['category']][info['code']] = info['name']

        return hashes

    def __parse_hash_line(self, line):
        data = list(map(str.strip, line.split('|')))

        if len(data) == 3:
            return {
                'code': data[0],
                'name': data[1],
                'category': data[2]
            }

        return False

    def compact_hashes(self, hashes):
        data = {}
        for type, hashes in hashes.items():
            for code, hash in hashes.items():
                data[code] = type + ' / ' + hash

        # Sort dict - why you gotta be like that python? This is why you have no friends.
        data = collections.OrderedDict(sorted(data.items(), key=lambda kv: kv[1]))
        return data

    def is_valid_hash_type(self, hash_type):
        valid = False
        supported_hashes = self.get_supported_hashes()
        for type, hashes in supported_hashes.items():
            for code, name in hashes.items():
                if code == hash_type:
                    valid = True
                    break

            if valid:
                break

        return valid

    def build_command_line(self, session_name, mode, mask, hashtype, hashfile, wordlist, rule, outputfile, potfile, increment_min, increment_max, force):
        command = {
            self.hashcat_binary: '',
            '--session': session_name,
            '--attack-mode': mode,
            '--hash-type': hashtype,
            '--outfile': outputfile,
            '--potfile-path': potfile,
            '--status': '',
            '--status-timer': self.status_interval,
            hashfile: '',
        }

        if mode == 0:
            # Wordlist.
            command[wordlist] = ''

            if len(rule) > 0:
                command['--rules-file'] = rule
        elif mode == 3:
            # Bruteforce.
            parsed_mask = self.parse_mask_from_string(mask)
            for group in parsed_mask['groups']:
                command['-' + str(group['position'])] = group['mask']

            command[parsed_mask['mask']] = ''

            if increment_min > 0 or increment_max > 0:
                command['--increment'] = ''

            if increment_min > 0:
                command['--increment-min'] = increment_min

            if increment_max > 0:
                command['--increment-max'] = increment_max
        else:
            # Invalid or not implemented yet.
            return {}

        if force:
            command['--force'] = ''

        return command

    def parse_mask_from_string(self, mask):
        # This function should be the same as the processCompiledMask() from the frontend.

        # Replace double quotes.
        compiled = mask.replace('  ', '')

        # Example mask. The last bit is the actual mask and the start is any custom sets.
        # -1 ?l?s -2 ?l ?u -3 ?d?s -4 ab??d ?1?u?2?3?4?l?u?d
        info = compiled.split(' ')

        # The last element is the actual mask. Retrieve it and remove it from the array.
        actual_mask = info.pop().strip()

        """
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
        """
        charset = False
        all_charsets = []
        while len(info) > 0:
            part = info.pop(0)
            if len(part) == 2 and part[0] == '-' and part[1].isdigit():
                # Save any previously parsed charset.
                if charset is not False:
                    charset['mask'] = charset['mask'].strip()
                    all_charsets.append(charset)

                charset = {
                    'position': int(part[1]),
                    'mask': ''
                }
            else:
                if charset is not False:
                    charset['mask'] = ' ' + part

        if charset is not False:
            charset['mask'] = charset['mask'].strip()
            all_charsets.append(charset)

        # Now sort, just in case it's not in the right order.
        for i in range(len(all_charsets)):
            for k in range(0, len(all_charsets) - i - 1):
                if all_charsets[i]['position'] < all_charsets[k]['position']:
                    swap = all_charsets[i]
                    all_charsets[i] = all_charsets[k]
                    all_charsets[k] = swap

        # And now put into the final object. The number of question marks is the number of positions.
        data = {
            'mask': actual_mask,
            'positions': actual_mask.count('?'),
            'groups': all_charsets
        }

        return data

    def parse_stream(self, stream):
        stream = str(stream)
        progress = self.__stream_get_last_progress(stream)
        data = self.__convert_stream_progress(progress)

        return data

    def __convert_stream_progress(self, progress):
        data = {}

        progress = progress.split("\n")

        for line in progress:
            parts = line.split(": ", 1)
            if len(parts) != 2:
                continue
            key = parts[0].rstrip(".")
            value = parts[1]

            data[key] = value

        return data

    def __stream_get_last_progress(self, stream):
        # Split all stream by \n.
        stream = stream.split("\\n")

        progress_starts_from = self.__stream_find_last_progress_line(stream)
        if progress_starts_from is False:
            return ''

        progress = []
        for i in range(progress_starts_from, len(stream)):
            if stream[i] == '':
                break

            progress.append(stream[i])

        return "\n".join(progress)

    def __stream_find_last_progress_line(self, lines):
        found = False
        for i in range(len(lines) - 1, 0, -1):
            if lines[i].startswith('Session..'):
                found = i
                break

        return found

    def get_running_processes_commands(self):
        if len(self.hashcat_binary) == 0:
            return []

        # Return only the command column from the running processes.
        output = self.shell.execute(['ps', '-www', '-x', '-o', 'cmd'], user_id=0)
        output = output.split("\n")

        processes = []
        length = len(self.hashcat_binary)
        for line in output:
            # Check if the beginning of the command path matches the path of the hashcat binary path.
            if line[:length] == self.hashcat_binary:
                processes.append(line)

        return processes

    def get_process_screen_names(self):
        processes = self.get_running_processes_commands()
        names = []

        for process in processes:
            name = self.extract_session_from_process(process)
            if len(name) == 0:
                continue

            names.append(name)

        return names

    def extract_session_from_process(self, process):
        parts = process.split(" ")
        name = ''
        for i, item in enumerate(parts):
            if item == '--session':
                name = parts[i + 1]
                break

        return name