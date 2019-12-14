from flask import current_app
from pathlib import Path
import os


class ScreenManager:
    def get_screenrc_path(self):
        path = Path(current_app.root_path)
        return os.path.join(str(path.parent), 'files', 'screen', 'screen.rc')
