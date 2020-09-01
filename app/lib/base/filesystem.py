import os
import glob
import datetime


class FileSystemManager:
    def get_files(self, absolute_path, recursive=False):
        if len(absolute_path) == '' or not os.path.isdir(absolute_path) or not os.access(absolute_path, os.R_OK):
            return {}

        data = {}
        for file in sorted(glob.glob(os.path.join(absolute_path, '**'), recursive=recursive)):
            if not os.path.isfile(file):
                continue

            name = file.replace(absolute_path, '').lstrip(os.sep)
            data[name] = {
                'name': name,
                'path': file,
                'size': os.stat(file).st_size,
                'size_human': self.human_filesize(os.stat(file).st_size),
                'created_at': datetime.datetime.fromtimestamp(int(os.path.getctime(file))),
                'modified_at': datetime.datetime.fromtimestamp(int(os.path.getmtime(file))),
                'type': 'file'
            }

        return data

    def get_folders(self, absolute_path, recursive=False):
        if len(absolute_path) == '' or not os.path.isdir(absolute_path) or not os.access(absolute_path, os.R_OK):
            return {}

        data = {}
        for file in sorted(glob.glob(os.path.join(absolute_path, '**'), recursive=recursive)):
            if os.path.isfile(file):
                continue

            name = file.replace(absolute_path, '').lstrip(os.sep)
            data[name] = {
                'name': name,
                'path': file,
                'type': 'folder'
            }

        return data

    def human_filesize(self, num, suffix = 'B'):
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)
