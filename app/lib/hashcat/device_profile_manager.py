from app import db
from app.lib.models.hashcat import DeviceProfileModel
from sqlalchemy import func


class DeviceProfileManager:
    def __init__(self, supported_devices):
        self.__supported_devices = supported_devices

    def get_device_profiles(self):
        profiles = {}
        records = DeviceProfileModel.query.order_by('name').all()
        for profile in records:
            profiles[profile.id] = self.__load_profile(profile)

        return profiles

    def __load_profile(self, record):
        return {
            'id': record.id,
            'name': record.name,
            'devices': self.__parse_device(record.devices),
            'enabled': True if record.enabled == 1 else False
        }

    def __parse_device(self, saved_devices):
        devices = {}
        saved_devices = saved_devices.split(',')
        for device_id in saved_devices:
            if self.is_valid_device(device_id):
                devices[device_id] = self.__supported_devices[device_id]

        return devices

    def is_valid_device(self, device_id):
        return str(device_id) in self.__supported_devices

    def get_supported_devices(self):
        return self.__supported_devices

    def get_profile(self, id):
        profile = self.get(id=id)
        if not profile:
            return None

        return self.__load_profile(profile[0])

    def get(self, id=None, name=None, devices=None, enabled=None):
        query = DeviceProfileModel.query
        if id is not None:
            query = query.filter(DeviceProfileModel.id == id)

        if name is not None:
            query = query.filter(func.lower(DeviceProfileModel.name) == func.lower(name))

        if devices is not None:
            query = query.filter(DeviceProfileModel.devices == devices)

        if enabled is not None:
            query = query.filter(DeviceProfileModel.enabled == enabled)

        return query.all()

    def save(self, id, name, devices, enabled):
        profile = self.get(id=id)
        profile = profile[0] if profile else DeviceProfileModel()

        profile.name = name
        profile.devices = ','.join(str(d) for d in sorted(set(devices)))
        profile.enabled = enabled

        db.session.add(profile)
        db.session.commit()

        db.session.refresh(profile)

        return profile

    def delete(self, id):
        DeviceProfileModel.query.filter_by(id=id).delete()
        db.session.commit()
        return True

    def has_enabled_profiles(self):
        return len(self.get(enabled=True)) > 0

    def is_profile_enabled(self, profile_id):
        return len(self.get(id=profile_id, enabled=True)) > 0

    def get_device_list(self, profile_id):
        if not self.is_profile_enabled(profile_id):
            return None

        profile = self.get_profile(profile_id)
        if len(profile['devices']) == 0:
            return None

        # Get the keys of the dictionary - https://stackoverflow.com/a/45253740
        device_ids = [*profile['devices']]
        return ','.join(device_ids)
