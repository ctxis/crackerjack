import collections
import re


class HashcatManager:
    def __init__(self, shell, hashcat_binary, hashid, status_interval=10, force=False):
        self.shell = shell
        self.hashcat_binary = hashcat_binary
        self.hashid = hashid
        self.status_interval = 10 if int(status_interval) <= 0 else int(status_interval)
        self.force = force

    def get_supported_hashes(self):
        output = self.shell.execute([self.hashcat_binary, '--help'], user_id=0)

        # Split lines using \n and run strip against all elements of the list.
        lines = list(map(str.strip, output.split("\n")))
        hashes = self.__parse_supported_hashes(lines)
        return hashes

    def guess_hash(self, hash):
        supported_hashes = self.get_supported_hashes()

        results = self.hashid.guess(hash)
        results['descriptions'] = {}
        for hashtype in results['matches']:
            description = self.__get_hashtype_description(hashtype, supported_hashes=supported_hashes)
            if len(description) == 0:
                continue
            results['descriptions'][hashtype] = description

        return results

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

    def __get_hashtype_description(self, hash_type, supported_hashes=None):
        description = ''
        if supported_hashes is None:
            supported_hashes = self.get_supported_hashes()

        if not isinstance(hash_type, int):
            hash_type = int(hash_type)

        for type, hashes in supported_hashes.items():
            for code, name in hashes.items():
                if int(code) == hash_type:
                    description = name
                    break

            if len(description) > 0:
                break

        return description

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

    def build_export_password_command_line(self, hashfile, potfile, save_as, contains_usernames):
        command = [
            self.hashcat_binary,
            '--potfile-path',
            potfile,
            '--outfile',
            save_as,
            '--outfile-format',
            '2',
            '--show',
            hashfile,
            '--username' if contains_usernames == 1 else ''
        ]

        return command

    def build_command_line(self, session_name, mode, mask, hashtype, hashfile, wordlist, rule, outputfile, potfile,
                           increment_min, increment_max, optimised_kernel, workload, contains_usernames):
        command = {
            self.hashcat_binary: '',
            '--session': session_name,
            '--attack-mode': mode,
            '--hash-type': hashtype,
            '--outfile': outputfile,
            '--potfile-path': potfile,
            '--status': '',
            '--status-timer': self.status_interval,
            '--workload-profile': workload,
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

        if optimised_kernel == 1:
            command['--optimized-kernel-enable'] = ''

        if contains_usernames == 1:
            command['--username'] = ''

        if self.force:
            command['--force'] = ''

        return command

    def build_restore_command(self, session_name):
        command = {
            self.hashcat_binary: '',
            '--session': session_name,
            '--restore': ''
        }

        if self.force:
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
                ab??d
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
        # stream = stream.split("\\n")
        stream = stream.split("\n")

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

    def is_process_running(self, screen_name):
        screens = self.get_process_screen_names()
        return screen_name in screens

    def __detect_session_status(self, raw, screen_name, tail_screen):
        # States are:
        #   0   NOT_STARTED
        #   1   RUNNING
        #   2   STOPPED
        #   3   FINISHED
        #   4   PAUSED
        #   5   CRACKED
        #   98  ERROR
        #   99  UNKNOWN
        status = 0
        if self.is_process_running(screen_name):
            status = 1
            # If it's still running, there's a chance it's just paused. Check for that.
            if 'Status' in raw:
                if raw['Status'] == 'Paused':
                    status = 4

        # If it's not running, try to get the current status.
        if status == 0:
            if 'Status' in raw:
                if raw['Status'] == 'Running' or raw['Status'] == 'Paused':
                    # If we got to this point it means that the process isn't currently running but there is a 'Status'
                    # feed. In this case, mark it as an error.
                    status = 98
                elif raw['Status'] == 'Quit':
                    status = 2
                elif raw['Status'] == 'Exhausted':
                    status = 3
                elif raw['Status'] == 'Cracked':
                    status = 5

        # In the event that the status is still 0 BUT the screen.log file is not empty, it means there has been some
        # activity, so it's probably an error.
        if status == 0 and len(tail_screen) > 0:
            status = 98

        return status

    def process_hashcat_raw_data(self, raw, screen_name, tail_screen):
        # Build base dictionary
        data = {
            'process_state': self.__detect_session_status(raw, screen_name, tail_screen),
            'all_passwords': 0,
            'cracked_passwords': 0,
            'time_remaining': '',
            'estimated_completion_time': '',
            'progress': 0
        }

        # progress
        if 'Progress' in raw:
            matches = re.findall('\((\d+.\d+)', raw['Progress'])
            if len(matches) == 1:
                data['progress'] = matches[0]

        # passwords
        if 'Recovered' in raw:
            matches = re.findall('(\d+/\d+)', raw['Recovered'])
            if len(matches) > 0:
                passwords = matches[0].split('/')
                if len(passwords) == 2:
                    data['all_passwords'] = int(passwords[1])
                    data['cracked_passwords'] = int(passwords[0])

        # time remaining
        if 'Time.Estimated' in raw:
            matches = re.findall('\((.*)\)', raw['Time.Estimated'])
            if len(matches) == 1:
                data['time_remaining'] = 'Finished' if matches[0] == '0 secs' else matches[0].strip()

        # estimated completion time
        if 'Time.Estimated' in raw:
            matches = re.findall('(.*)\(', raw['Time.Estimated'])
            if len(matches) == 1:
                data['estimated_completion_time'] = matches[0].strip()

        return data
