import asyncio
import app
import math
import requests # type: ignore
import network # type: ignore
import hashlib
import settings # type: ignore
import os
import json
from events.input import Buttons, BUTTON_TYPES # type: ignore
from app_components import Menu, clear_background # type: ignore

CONFIG_REPO_URL = "https://thomasjackdalby.github.io/config/wifind-my-friends"
CONFIG_URL = f"{CONFIG_REPO_URL}/config.json"
DK_LOCATIONS_URL = f"{CONFIG_REPO_URL}/dk-locations.json"
KEY_SERVER_URL = "server_url"
KEY_SSID_FILTER = "ssid_filter"
KEY_SCAN_INTERVAL = "scan_interval"

DEFAULT_CONFIG = {
    KEY_SERVER_URL : "http://192.168.0.149:8000",
    KEY_SSID_FILTER : None,
    KEY_SCAN_INTERVAL: 10
}

SCREEN_TOP = -100
SCREEN_BOTTOM = 120
NUMBER_OF_WAVES = 8
WAVE_DELTA = 30
WAVE_SPEED = 1

PI = 3.14
TWO_PI = 2 * 3.14
PI_3 = PI / 3
PI_6 = PI / 6

STATE_TITLE = 0
STATE_SELECT_DEVICE = 1
STATE_DEVICE_POSITION = 2
STATE_ADMIN = 3

def convert_bytes_to_hex_str(bytes: bytes, separator: str = ""):
    return separator.join("{:02x}".format(b) for b in bytes)

class AppState:
    def __init__(self, app: WiFindMyFriendsApp) -> None:
        self._app = app

    def update(self, delta):
        pass
    
    def draw(self, ctx):
        pass

    def on_enter(self, args):
        pass

    def on_exit(self):
        pass

class TitleState(AppState):

    def __init__(self, app):
        self.wave_index = 0
        self._app = app

    def update(self, delta):
        if self._app.button_states.get(BUTTON_TYPES["CANCEL"]):
            self._app.minimise()
        elif self._app.button_states.get(BUTTON_TYPES["UP"]) or self._app.button_states.get(BUTTON_TYPES["DOWN"]):
            self._app.set_state(STATE_SELECT_DEVICE)
        elif self._app.button_states.get(BUTTON_TYPES["LEFT"]): # put another check in?
            self._app.set_state(STATE_ADMIN)

        self._app.button_states.clear()

    def draw(self, ctx):
        ctx.save()
        clear_background(ctx)
        
        # draw radar waves
        ctx.line_width = 2
        radius = self.wave_index
        for i in range(NUMBER_OF_WAVES):
            ctx.rgb(0, 1, 0).arc(0, SCREEN_BOTTOM, radius, TWO_PI, PI, True).stroke()
            ctx.rgb(0, 0.75, 0).arc(0, SCREEN_BOTTOM, radius - 3, TWO_PI, PI, True).stroke()
            radius += WAVE_DELTA
        
        # Draw "Hello World" text on the round display
        ctx.font_size = 40
        ctx.rgb(1, 1, 1) # White
        ctx.text_align = ctx.CENTER
        ctx.move_to(0, -20).text("WiFi")
        ctx.move_to(0, 10).text("My")
        ctx.move_to(0, 40).text("Friends")

        ctx.font_size = 25
        ctx.move_to(45, -45).text("nd")

        ctx.font_size = 20
        ctx.move_to(0, 90).text("v0.0.1")

        ctx.restore()

        self.wave_index += WAVE_SPEED
        if self.wave_index > WAVE_DELTA:
            self.wave_index = 0

class SelectDeviceState(AppState):
    def __init__(self, app):
        super().__init__(app)
        self.is_loading = True
        self._loading = LoadingGraphic("Fetching...")
        self._devices = []
        self._menu: Menu | None = None

    def on_enter(self, args):
        asyncio.create_task(self._fetch_device_list())

    async def _fetch_device_list(self):
        self.is_loading = True
        self._devices = []
        try:
            await asyncio.sleep(0.1)

            request_url = f"{self._app._config[KEY_SERVER_URL]}/api/devices"
            response = requests.get(request_url)
            if response.status_code == 200: self._devices = response.json()
            else: print(f"Unexpected status_code received from {request_url}")

            self._menu = Menu(
                self._app, 
                [device["name"] for device in self._devices],
                select_handler=self._on_select,
                back_handler=self._on_back
            )
        except Exception as e:
            self._devices = []
            self._menu = None
            print(f"Unable to fetch device list from server [{e}]")
        self.is_loading = False

    def update(self, delta):
        if self._menu is not None: self._menu.update(delta)
        if self.is_loading: self._loading.update()

        if self._app.button_states.get(BUTTON_TYPES["CANCEL"]):
            self._app.set_state(STATE_TITLE)
        elif not self.is_loading and self._app.button_states.get(BUTTON_TYPES["CONFIRM"]):
            asyncio.create_task(self._fetch_device_list())

        self._app.button_states.clear()

    def _on_select(self, item, position):
        if position < 0 or position >= len(self._devices):
            raise Exception("invalid position of [].")
        self._app.set_state(STATE_DEVICE_POSITION, self._devices[position]["id"])

    def _on_back(self):
        self._app.minimise()

    def draw(self, ctx):
        clear_background(ctx)
        if self.is_loading: self._loading.draw(ctx)
        else:
            if self._menu is not None:
                self._menu.draw(ctx)
            else:
                # not loading and no menu means we need to retry
                ctx.rgb(1, 1, 1)
                ctx.text_align = ctx.CENTER
                ctx.font_size = 20
                ctx.move_to(0, 0).text("Retry?")
                ctx.restore()

class DevicePositionState(AppState):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.is_loading = True
        self._loading = LoadingGraphic("Fetching...")

    def on_enter(self, args):
        if not isinstance(args, int): raise Exception("Incorrect datatype passed to DevicePositionState")
        device_id = args
        self.is_loading = True
        asyncio.create_task(self._fetch_device_location(device_id))

    async def _fetch_device_location(self, device_id: int):
        self.is_loading = True
        self._data = None
        try:
            await asyncio.sleep(0.1)
            response = requests.get(f"{self._app.settings["url"]}/api/devices/{device_id}?latest=true")
            print(response.status_code)
            if response.status_code == 200: self._data = response.json()
            else: self._data = None
   
        except Exception as e:
            self._data = None
            print(f"Unable to fetch device location from server [{e}]")
        self.is_loading = False
    
    def update(self, delta):
        if self.is_loading: self._loading.update()

        if self._app.button_states.get(BUTTON_TYPES["CANCEL"]):
            self._app.set_state(STATE_SELECT_DEVICE)
        self._app.button_states.clear()

    def draw(self, ctx):
        clear_background(ctx)

        if self.is_loading: self._loading.draw(ctx)
        elif self._data is None:
            # there's an error. retry
            clear_background(ctx)
            ctx.rgb(1, 1, 1)
            ctx.text_align = ctx.CENTER
            ctx.font_size = 20
            ctx.move_to(0, 0).text("Retry data load?")
            ctx.restore()
        else:
            
            # draw the information

            
            # ctx.line_width = 2
            ctx.rgb(1, 1, 1)
            ctx.text_align = ctx.CENTER
            ctx.font_size = 20
            ctx.move_to(0, 0).text(self._data["desc"])

            ctx.restore()

class AdminState(AppState):

    def __init__(self, app: WiFindMyFriendsApp) -> None:
        super().__init__(app)
        self._data = {}
        self._menu = None

    def update(self, delta):
        if self._menu is not None: self._menu.update(delta)
        elif self._app.button_states.get(BUTTON_TYPES["CANCEL"]):
            self._app.set_state(STATE_TITLE)
        elif self._menu is None and self._app.button_states.get(BUTTON_TYPES["LEFT"]):
            try:
                print("Choosing a DK")
                if len(self._app._signals) > 0:
                    # take the strongest signal as our closest access-point
                    self._closest_signal = list(sorted(self._app._signals, key=lambda s: -s[2]))[0]
                    print(f"Closest signal: {self._closest_signal[0]}")

                    # allow user to choose which DK it is
                    self._menu = Menu(
                        self._app, 
                        list(self._data.keys()),
                        select_handler=self._on_select,
                        back_handler=self._on_back
                    )
            except Exception as e:
                print(f"Failed to load dk-locations.json: {e}")

        self._app.button_states.clear()
    
    def _on_select(self, item, position):
        print("Selected item.")
        if item not in self._data:
            print(f"This is weird {item}")
            return

        dk_id = item
        dk_position = self._data[item]
        
        # get the access point with the matching bssid
        request_url = f"{self._app._config[KEY_SERVER_URL]}/api/access-points"
        response = requests.get(request_url)
        if response.status_code != 200:
            print(f"Didn't get 200 back [{response.status_code}] from {request_url}.")
            self.is_selecting = False
            return

        access_points = response.json()
        access_point = next(filter(lambda ap: ap["bssid"] == self._closest_signal[0], access_points))
        if access_point is None:
            print("Strongest signal not found in list of access points?")
            self.is_selecting = False
            return
        
        access_point_id = access_point["id"]
        request_url = f"{self._app._config[KEY_SERVER_URL]}/api/access-points/{access_point_id}"
        response_payload = {
            "name" : dk_id,
            "ssid" : self._closest_signal[1],
            "position_x" : dk_position[0],
            "position_y" : dk_position[1],
        }
        response = requests.put(request_url, json=response_payload)
        if response.status_code != 201:
            print(f"Didn't get 201 back [{response.status_code}] from {request_url}")
            return
        
        self._menu = None

    def _on_back(self):
        self._menu = None

    def draw(self, ctx):
        clear_background(ctx)
        if self._menu is None:
            ctx.rgb(1, 1, 1)
            ctx.font = "Comic Mono"
            ctx.text_align = ctx.CENTER
            ctx.font_size = 16
            ctx.move_to(0, SCREEN_TOP+15).text("ADMIN MODE")

            ctx.font_size = 14
            ctx.text_align = ctx.LEFT
            y = ctx.font_size
            for signal in sorted(self._app._signals, key=lambda s: -s[2]):
                if signal is None: continue
                ctx.move_to(-95, SCREEN_TOP+25+y).text(f"{signal[0]} {signal[2]} {signal[1]}")
                y += ctx.font_size
        else:
            self._menu.draw(ctx)

        ctx.restore()

    def on_enter(self, args):
        print(f"Loading config from [{DK_LOCATIONS_URL}]")
        response = requests.get(DK_LOCATIONS_URL)
        if response.status_code != 200: print(f"Unexpected status_code received from '{DK_LOCATIONS_URL}'.")
        else: self._data = response.json()

    def on_exit(self):
        self._data = {}

class LoadingGraphic:

    def __init__(self, text = ""):
        self.text = text
        self._arc_length = PI_3
        self._max_index = 50

        self._index = 0
        self._angle_delta = TWO_PI / self._max_index

    def update(self):
        self._index += 1
        if self._index >= self._max_index:
            self._index = 0

    def draw(self, ctx):
        ctx.line_width = 10
        start_angle = self._index * self._angle_delta
        ctx.rgb(0, 1, 0).arc(0, 0, 100, start_angle, start_angle + self._arc_length, False).stroke()
        ctx.rgb(0, 0.75, 0).arc(0, 0, 85, -start_angle, -start_angle - self._arc_length, True).stroke()

        ctx.rgb(1, 1, 1)
        ctx.text_align = ctx.CENTER
        ctx.font_size = 20
        ctx.move_to(0, 0).text(self.text)

# "url" : 

class WiFindMyFriendsApp(app.App):

    def __init__(self):
        super().__init__()
        self.button_states = Buttons(self)

        self._load_config()
        self._update_url = f"{self._config[KEY_SERVER_URL]}/api/update"
        self._badge_owner = settings.get("name") or "Attendee"
        self._signals = []

        self._states = [
            TitleState(self),
            SelectDeviceState(self),
            DevicePositionState(self),
            AdminState(self)
        ]
        self._state: AppState = self._states[0]
        self._init_network()

    def update(self, delta):
        self._state.update(delta)

    def draw(self, ctx):
        self._state.draw(ctx)

    def set_state(self, state_index: int, args = None):
        self._state.on_exit()
        self._state = self._states[state_index]
        self._state.on_enter(args)

    def _init_network(self):
        try:
            self._wlan = network.WLAN(network.STA_IF)
            self._wlan.active(True)
            self._net_ok = True

            mac_address = self._wlan.config("mac")
            self._mac_str = convert_bytes_to_hex_str(mac_address, ":")
            self._token = convert_bytes_to_hex_str(hashlib.sha256(mac_address).digest())[:32]

            asyncio.create_task(self._scan_loop())
        except Exception:
            self._wlan = None
            self._net_ok = False

    def _load_config(self):
        self._config: dict = DEFAULT_CONFIG
        
        print(f"Loading config from [{CONFIG_URL}]")
        response = requests.get(CONFIG_URL)
        if response.status_code != 200:
            print(f"Unexpected status_code received from {CONFIG_URL}. Only default config will be available.")
            return
        self._config.update(response.json())

    async def _scan_loop(self):
        if self._wlan is None:
            print("No wlan instance. Scanning will be disabled.")
            return
        while True:
            await asyncio.sleep(self._config[KEY_SCAN_INTERVAL])

            try:
                results = self._wlan.scan()
            except Exception as e:
                print(f"An error occured whilst performing a wlan scan. {e}")
                results = []

            #ssid, bssid, channel, RSSI, authmode, hidden
            def parse_signal(result) -> tuple[str, str, float] | None:
                try:
                    ssid = result[0].decode("utf-8")
                    bssid = convert_bytes_to_hex_str(result[1][:6], ":")
                    rssi = result[3]
                    return (bssid, ssid, rssi)
                except Exception as e:
                    print("An error occured whilst parsing the signal.")
                    print(e)
                    return None

            def filter_signal(signal: tuple[str, str, float] | None) -> bool:
                if signal is None: return False
                _, ssid, _ = signal
                if self._config[KEY_SSID_FILTER] == None: return True
                if self._config[KEY_SSID_FILTER] == ssid: return True
                return False
            
            self._signals: list[tuple[str, str, float]] = list(filter(filter_signal, map(parse_signal, results))) # type: ignore

            if len(self._signals) <= 0:
                print("No wifi networks detected so no update packet will be sent.")
                continue

            def format_signal(signal):
                return {
                    "bssid" : signal[0],
                    "ssid" : signal[1],
                    "rssi" : signal[2]
                }

            print(f"Sending update package to {self._update_url}")
            request = {
                "id" : None,
                "name": self._badge_owner,
                "token" : self._token,
                "signals" : list(map(format_signal, filter(lambda s: s is not None, self._signals)))
            }
            requests.post(self._update_url, json=request)

__app_export__ = WiFindMyFriendsApp