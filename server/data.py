import os
import datetime
import constants
import sqlalchemy
import dotenv
import utils
import logging
import sqlalchemy.orm
import string
import random
from sqlalchemy import select
from typing import Optional
from model import Base, Device, DeviceLocation, AccessPoint, AccessPointSignal

logger = logging.getLogger("wifind-my-friends")

if os.path.exists(".env"): logger.info("Loading env variables from .env file.")
dotenv.load_dotenv()

CONNECTION_STRING = os.environ["CONNECTION_STRING"]
_engine = None

def create_engine():
    global _engine
    logger.debug("Creating SQL engine.")
    _engine = sqlalchemy.create_engine(CONNECTION_STRING)
    Base.metadata.create_all(_engine)

def generate_token(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class DataBaseSession:

    def __init__(self):
        global _engine
        if _engine is None: create_engine()
        self._session = sqlalchemy.orm.Session(_engine)

    def __enter__(self):
        self._session.__enter__()
        return self
    
    def __exit__(self, exception_type, exception_value, exception_traceback):
        self._session.__exit__(exception_type, exception_value, exception_traceback)

    # -- Devices

    def get_devices(self) -> list[Device]:
        return list(self._session.scalars(select(Device)).all())

    def get_device_with_id(self, id: int) -> Device | None:
        return self._session.scalars(select(Device)
            .where(Device.id == id)).first()
    
    def get_device_with_name(self, name: str) -> Device | None:
        return self._session.scalars(select(Device)
            .where(Device.name == name)).first()
    
    def get_device_with_token(self, token: str) -> Device | None:
        return self._session.scalars(select(Device)
            .where(Device.token == token)).first()
    
    def add_device(self, name: str, token: str) -> Device | None:
        if len(token) != 32: raise Exception("token must be 32 chars long.")

        device = self.get_device_with_token(token)
        if device is not None: return device

        device = Device(
            name=name,
            token = token
            )
        self._session.add(device)
        self._session.commit()
        return device
    
    # -- Device Locations

    def get_device_location_with_id(self, device_location_id: int) -> DeviceLocation | None:
        return self._session.scalars(select(DeviceLocation)
            .where(DeviceLocation.id == device_location_id)).first()

    def add_device_location(self, device_id: int) -> DeviceLocation | None:
        device = self.get_device_with_id(device_id)
        if device is None: return
        device_location = DeviceLocation(
            device_id = device_id,
            date_time = datetime.datetime.now(),
        )
        self._session.add(device_location)
        self._session.commit()
        return device_location

    def add_access_point_signal(self, device_location_id: int, access_point_id: int, rssi: float):
        device_location = self.get_device_location_with_id(device_location_id)
        if device_location is None: 
            print(f"No device_location with id [{device_location_id}].")
            return

        access_point = self.get_access_point_with_id(access_point_id)
        if access_point is None: 
            print(f"No access_point with id [{access_point_id}].")
            return
        
        access_point_signal = AccessPointSignal(
            access_point_id = access_point_id,
            device_location_id = device_location_id,
            rssi = rssi
        )
        self._session.add(access_point_signal)
        self._session.commit()
        return access_point_signal

    # -- Access Points

    def get_access_points(self) -> list[AccessPoint]:
        return list(self._session.scalars(select(AccessPoint)).all())

    def get_access_point_with_id(self, id: int) -> AccessPoint | None:
        return self._session.scalars(select(AccessPoint)
            .where(AccessPoint.id == id)).first()
    
    def get_access_points_with_ssid(self, ssid: str) -> list[AccessPoint]:
        return list(self._session.scalars(select(AccessPoint)
            .where(AccessPoint.ssid == ssid)).all())
    
    def get_access_point_with_bssid(self, bssid: str) -> AccessPoint | None:
        return self._session.scalars(select(AccessPoint)
            .where(AccessPoint.bssid == bssid)).first()
    
    def add_access_point(self, bssid: str, ssid: str) -> AccessPoint:
        access_point = self.get_access_point_with_bssid(bssid)
        if access_point is not None: return access_point

        access_point = AccessPoint(
            bssid=bssid,
            ssid=ssid,
            )
        self._session.add(access_point)
        self._session.commit()
        return access_point