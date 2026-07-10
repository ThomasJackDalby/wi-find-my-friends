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
from model import (
    DeviceLocation
)
from schemas import (
    DeviceRegisterRequestSchema,
    DeviceRegisterResponseSchema,
    PostUpdateRequestSchema,
    DeviceInfoResponseSchema,
    AccessPointResponseSchema
    )

logger = logging.getLogger("wifind-my-friends")

def get_auth_user(token: str = fastapi.Depends(fastapi.security.APIKeyHeader(name="token"))):
    logger.debug(f"token: {token} vs {MASTER_API_TOKEN}")
    return token == MASTER_API_TOKEN

public = fastapi.APIRouter(prefix="/api")
authenticated = fastapi.APIRouter(prefix="/api", dependencies=[fastapi.Depends(get_auth_user)])

# /devices 

@public.get("/devices", status_code=200)
def get_devices(name: str | None = None) -> list[DeviceInfoResponseSchema]:
    with DataBaseSession() as db:
        if name is None:
            return [DeviceInfoResponseSchema(
                id = device.id,
                name = device.name
            ) for device in db.get_devices()]
        
        device = db.get_device_with_name(name)
        if device is not None: 
            return [DeviceInfoResponseSchema(
                id = device.id,
                name = device.name
            )]
        return []

@public.post("/devices", status_code=201)
def post_register(request: DeviceRegisterRequestSchema) -> DeviceRegisterResponseSchema:
    with DataBaseSession() as db:
        device = db.add_device(request.name, request.token)
        if device is None: raise fastapi.HTTPException(status_code=500, detail=f"Unable to add device to the database.")
        return DeviceRegisterResponseSchema(
            id = device.id,
        )

# /device/locations

@public.get("/devices/{device_id:int}/locations", status_code=201)
def get_device_location(device_id: int):
    return {
        "id" : device_id,
        "name" : "Solan",
        "pos_x" : 123,
        "pos_y" : 456,
        "desc" : "Near the Robot Arms"
    }


@public.post("/devices/{device_id:int}/locations", status_code=201)
def post_update(
        device_id: int,
        request: PostUpdateRequestSchema):
    with DataBaseSession() as db:
        device = db.get_device_with_id(device_id)
        if device is None:
            raise fastapi.HTTPException(404, f"No device with id '{device_id}'.")

        if device.token != request.token:
            raise fastapi.HTTPException(400, f"Incorrect token provided with request.")

        # need to calculate the location based on the rssi signals
        # device_location = DeviceLocation(

        # )

# /anchors

# @public.get("/anchors", status_code=200)
# def get_devices(name: str | None) -> list[AccessPointResponseSchema]:
#     with DataBaseSession() as db:
#         if name is None:
#             return [AccessPointResponseSchema(
#                 id = anchor.id,
#                 name = anchor.name
#             ) for anchor in db.get_anchors()]
#         return anchor

# @public.post("anchors/{device_id:int}/locations", status_code=201)
# def post_update(
# add_reference_device

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