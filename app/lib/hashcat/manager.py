import collections


class HashcatManager:
    def __init__(self, shell, hashcat_binary):
        self.shell = shell
        self.hashcat_binary = hashcat_binary

    def get_supported_hashes(self):
        output = self.shell.execute([self.hashcat_binary, '--help'])

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

    def build_command_line(self, session_name, mode, mask, hashtype, hashfile, wordlist, rule, outputfile, potfile, force):
        command = {
            self.hashcat_binary: '',
            '--session': session_name,
            '--attack-mode': mode,
            '--hash-type': hashtype,
            '--outfile': outputfile,
            '--potfile-path': potfile,
            '--status': '',
            '--status-timer': 30,
            hashfile: '',
        }

        if mode == 0:
            # Wordlist.
            command[wordlist] = ''

            if len(rule) > 0:
                command['--rules-file'] = rule
        elif mode == 3:
            # Bruteforce.
            command[mask] = ''
        else:
            # Invalid or not implemented yet.
            return {}

        if force:
            command['force'] = ''

        return command

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
