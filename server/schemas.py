from uuid import UUID
import pydantic

class DeviceInfoResponseSchema(pydantic.BaseModel):
    id: int
    name: str

class DeviceRegisterRequestSchema(pydantic.BaseModel):
    name: str
    token: str

class DeviceRegisterResponseSchema(pydantic.BaseModel):
    id: int

class SignalSchema(pydantic.BaseModel):
    id: int
    rrsi: float

class PostUpdateRequestSchema(pydantic.BaseModel):
    token: str
    signals: list[SignalSchema]


class AccessPointResponseSchema(pydantic.BaseModel):
    id: int
    ssid: str
    bssid: str
    position_x: float
    position_y: float