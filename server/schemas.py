from uuid import UUID
from datetime import datetime
import pydantic

class DeviceSummaryInfoResponseSchema(pydantic.BaseModel):
    id: int
    name: str

class DeviceDetailedInfoResponseSchema(pydantic.BaseModel):
    id: int
    name: str
    locations: list["DeviceLocationSchema"]

class DeviceLocationSchema(pydantic.BaseModel):
    x: float | None
    y: float | None
    date_time: datetime
    signals: list["SignalSchema"]

class PostUpdateRequestSchema(pydantic.BaseModel):
    id: int | None
    name: str
    token: str
    signals: list["SignalSchema"]

class SignalSchema(pydantic.BaseModel):
    bssid: str
    ssid: str
    rssi: float

class AccessPointInfoResponseSchema(pydantic.BaseModel):
    id: int
    name: str | None
    ssid: str | None
    bssid: str
    position_x: float | None
    position_y: float | None

class AccessPointEditRequestSchema(pydantic.BaseModel):
    name: str | None
    ssid: str | None
    position_x: float | None
    position_y: float | None

class AccessPointCreateRequestSchema(pydantic.BaseModel):
    bssid: str
    name: str | None
    ssid: str | None
    position_x: float | None
    position_y: float | None

class NamedLocationResponseSchema(pydantic.BaseModel):
    name: str | None
    position_x: float | None
    position_y: float | None