#
#   Any settings you put here will override the default ones from __init__.py
#   Make sure this file is in the ./instance folder.
#
import os

current_path = basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = "HelloWorld!"
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(current_path, 'crackerjack.sqlite3')
SQLALCHEMY_TRACK_MODIFICATIONS = False
