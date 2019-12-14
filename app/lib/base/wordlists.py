import os


class WordlistManager:
    def __init__(self, wordlist_path):
        self.wordlist_path = wordlist_path

    def get_wordlists(self):
        if self.wordlist_path == '' or not os.path.isdir(self.wordlist_path):
            return {}

        files = [f for f in os.listdir(self.wordlist_path) if os.path.isfile(os.path.join(self.wordlist_path, f))]
        wordlists = {}
        for file in files:
            wordlists[file] = {
                'name': file,
                'path': os.path.join(self.wordlist_path, file),
                'size': os.stat(os.path.join(self.wordlist_path, file)).st_size,
                'size_human': self.human_filesize(os.stat(os.path.join(self.wordlist_path, file)).st_size)
            }

        return wordlists

    def human_filesize(self, num, suffix = 'B'):
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    def is_valid_wordlist(self, wordlist):
        wordlists = self.get_wordlists()
        return wordlist in wordlists
