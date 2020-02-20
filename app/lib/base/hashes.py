import os
import shutil


class HashesManager:
    def __init__(self, filesystem, uploaded_hashes_path):
        self.filesystem = filesystem
        self.uploaded_hashes_path = uploaded_hashes_path

    def get_uploaded_hashes(self):
        return self.filesystem.get_files(self.uploaded_hashes_path)

    def is_valid_uploaded_hashfile(self, uploaded_hashfile):
        files = self.get_uploaded_hashes()
        return uploaded_hashfile in files

    def get_uploaded_hashes_path(self, uploaded_hashfile):
        if not self.is_valid_uploaded_hashfile(uploaded_hashfile):
            return ''

        files = self.get_uploaded_hashes()
        uploaded_hashfile = files[uploaded_hashfile]
        return uploaded_hashfile['path']

    def get_name_from_path(self, path):
        return path.replace(self.uploaded_hashes_path, '').lstrip(os.sep)

    def copy_file(self, src, dst):
        try:
            shutil.copyfile(src, dst)
        except OSError:
            return False

        return True