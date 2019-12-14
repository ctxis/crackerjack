from app.lib.models.config import ConfigModel
from app import db


class SettingsManager:
    def save(self, name, value):
        setting = ConfigModel.query.filter(ConfigModel.name == name).first()
        if setting is None:
            setting = ConfigModel(name=name, value=value)
            db.session.add(setting)
        else:
            setting.value = value

        db.session.commit()

        return True

    def get(self, name, default=None):
        setting = ConfigModel.query.filter(ConfigModel.name == name).first()
        if setting is None:
            return default
        return setting.value
