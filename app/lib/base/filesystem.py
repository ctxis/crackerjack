import os


class FileSystemManager:
    def get_files(self, absolute_path):
        if len(absolute_path) == '' or not os.path.isdir(absolute_path) or not os.access(absolute_path, os.R_OK):
            return {}

        files = [f for f in os.listdir(absolute_path) if os.path.isfile(os.path.join(absolute_path, f))]
        data = {}
        for file in files:
            data[file] = {
                'name': file,
                'path': os.path.join(absolute_path, file),
                'size': os.stat(os.path.join(absolute_path, file)).st_size,
                'size_human': self.human_filesize(os.stat(os.path.join(absolute_path, file)).st_size)
            }

        return data

    def human_filesize(self, num, suffix = 'B'):
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)
