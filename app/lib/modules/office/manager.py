import io
import tempfile
import os
from app.lib.modules.office import office2hashcat
from contextlib import redirect_stdout
from werkzeug.utils import secure_filename


class ModuleOfficeManager:
    def extract(self, file):
        filename = secure_filename(file.filename)

        temp_dir = tempfile.TemporaryDirectory()
        save_as = os.path.join(temp_dir.name, filename)
        file.save(save_as)

        output = self.__run_office2hashcat(save_as)

        temp_dir.cleanup()

        return output

    def __run_office2hashcat(self, file):
        # Because this script was taken as-is and is meant to be ran via CLI we use the io module to capture its output.
        f = io.StringIO()
        with redirect_stdout(f):
            try:
                office2hashcat.process_file(file)
            except:
                # Uh oh
                pass

        output = f.getvalue()
        return output
