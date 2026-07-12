# main.py

import datetime
import fastapi
import fastapi.responses
import fastapi.security
import fastapi.staticfiles
import fastapi.templating
import fastapi.middleware.cors
import logging
import os
from data import DataBaseSession
import uvicorn
import asyncio
from constants import MASTER_API_TOKEN
from utils import estimate_location

from schemas import (
    DeviceSummaryInfoResponseSchema,
    DeviceDetailedInfoResponseSchema,
    DeviceLocationSchema,
    SignalSchema,
    PostUpdateRequestSchema,
    AccessPointInfoResponseSchema,
    AccessPointEditRequestSchema,
    )

logger = logging.getLogger("wifind-my-friends")

def get_auth_user(token: str = fastapi.Depends(fastapi.security.APIKeyHeader(name="token"))):
    logger.debug(f"token: {token} vs {MASTER_API_TOKEN}")
    return token == MASTER_API_TOKEN

public = fastapi.APIRouter(prefix="/api")
authenticated = fastapi.APIRouter(prefix="/api", dependencies=[fastapi.Depends(get_auth_user)])

# /devices 

@public.get("/devices", status_code=200)
def get_devices() -> list[DeviceSummaryInfoResponseSchema]:
    with DataBaseSession() as db:
            return [DeviceSummaryInfoResponseSchema(
                id = device.id,
                name = device.name
            ) for device in db.get_devices()]

@public.get("/devices/{device_id:int}", status_code=200)
def get_device_location(device_id: int) -> DeviceDetailedInfoResponseSchema:

    device = db.get_device_with_id(device_id)
    if device is None: 
        raise fastapi.HTTPException(404, f"No device with id '{device_id}'.")

    return DeviceDetailedInfoResponseSchema(
        id=device_id,
        name=device.name,
        locations=[DeviceLocationSchema(
                x=loc.position_x,
                y=loc.position_y,
                signals = [SignalSchema(
                    bssid=signal.access_point.bssid,
                    rssi=signal.rssi
                ) for signal in loc.access_point_signals]
        ) for loc in device.locations]
    )

@public.get("/access-points", status_code=201)
def get_access_points():
        with DataBaseSession() as db:
            return [AccessPointInfoResponseSchema(
                id = access_point.id,
                name = access_point.name,
                ssid = access_point.ssid,
                bssid = access_point.bssid,
                position_x = access_point.position_x,
                position_y = access_point.position_y,
            ) for access_point in db.get_access_points()]

@public.put("/access-points/{access_point_id: int}", status_code=201)
def put_access_points(access_point_id: int, request: AccessPointEditRequestSchema):
        with DataBaseSession() as db:
            access_point = db.get_access_point_with_id(access_point_id)
            if access_point is None: raise fastapi.HTTPException(400, f"No access_points found with id [{access_point_id}]'.")
            if request.name is not None: access_point.name = request.name
            if request.ssid is not None: access_point.ssid = request.ssid
            if request.position_x is not None: access_point.position_x = request.position_x
            if request.position_y is not None: access_point.position_x = request.position_y
            db._session.commit()

@public.post("/update", status_code=201)
def post_update(request: PostUpdateRequestSchema):
    with DataBaseSession() as db:

        device = None
        if request.id is not None: device = db.get_device_with_id(request.id)
        else: device = db.get_device_with_token(request.token)

        with DataBaseSession() as db:
            if device is None:
                print(f"No device with provided id or token. Adding new device [{request.name}].")
                device = db.add_device(request.name, request.token)
                if device is None: raise fastapi.HTTPException(status_code=500, detail=f"Unable to add device to the database.")
            if device.token != request.token: raise fastapi.HTTPException(400, f"Invalid token for device with id [{device.id}]'.")

            location = db.add_device_location(device.id)
            if location is None: print("Unable to add device_location.")
            else:
                signals = []
                for signal in request.signals:
                    access_point = db.get_access_point_with_bssid(signal.bssid)
                    if access_point is None: access_point = db.add_access_point(signal.bssid, signal.ssid)
                    db.add_access_point_signal(location.id, access_point.id, signal.rssi)

                    if access_point.position_x is not None and access_point.position_y is not None:
                        signals.append((access_point.position_x, access_point.position_y, signal.rssi))
            
                if len(signals) >= 3:
                    print("Evaluating device position.")
                    result = estimate_location(signals)
                    print(result)
                    location.position_x = result[0]
                    location.position_y = result[1]
                else:
                    print("Not enough signals to triangulate...")
                     

        return device.id

app = fastapi.FastAPI()
app.include_router(public)
app.include_router(authenticated)
app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: No static files yet.
# app.mount("/", fastapi.staticfiles.StaticFiles(directory="static", html = True), name="static")

async def main():
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000, log_config=None)
    server = uvicorn.Server(config=config)
    await server.serve()

if __name__ == "__main__":
    import rich.logging

    # debug
    with DataBaseSession() as db:
        db.add_device("Tom", "0"*32)
        db.add_device("Solan", "1"*32)
        db.add_device("Ben", "2"*32)
        db.add_device("Oliver", "3"*32)

    handler = rich.logging.RichHandler(rich_tracebacks=True)
    # handler.addFilter(logging.Filter(name='wifind-my-friends'))
    logging.basicConfig(level=logging.DEBUG, format="%(message)s", datefmt="[%X]", handlers=[handler])

    asyncio.run(main())