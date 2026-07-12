import asyncio
import app
import math
import requests
from events.input import Buttons, BUTTON_TYPES
from app_components import Menu, clear_background

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

DEVICES = [
    "Tom",
    "Solan",
    "Ben"
]

class AppState:
    def __init__(self, app) -> None:
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
        try:
            await asyncio.sleep(0.1)
            response = requests.get(f"{self._app.settings["url"]}/api/devices")
            if response.status_code == 200: self._devices = response.json()
            else: self._devices = []

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

class WiFindMyFriendsApp(app.App):

    def __init__(self):
        self.button_states = Buttons(self)

        self.settings = {
            "url" : "http://192.168.0.104:8000"
        }

        self._states = [
            TitleState(self),
            SelectDeviceState(self),
            DevicePositionState(self)
        ]
        self._state: AppState = self._states[0]
        self._init_network()

    def set_state(self, state_index: int, args = None):
        self._state.on_exit()
        self._state = self._states[state_index]
        self._state.on_enter(args)

    def update(self, delta):
        self._state.update(delta)

    def draw(self, ctx):
        self._state.draw(ctx)

    def _init_network(self):
        try:
            import network
            self._wlan = network.WLAN(network.STA_IF)
            self._wlan.active(True)
            self._net_ok = True
            asyncio.create_task(self._scan_loop())
        except Exception:
            self._wlan = None
            self._net_ok = False

    async def _scan_loop(self):
        while True:
            await asyncio.sleep(5)

            try:
                results = self._wlan.scan()
            except Exception:
                results = []

            #ssid, bssid, channel, RSSI, authmode, hidden
            def parse_signal(result) -> tuple[str, str, float] | None:
                try:
                    ssid = result[0].decode("utf-8")
                    bssid = ":".join("{:02x}".format(b) for b in result[1][:6])
                    rssi = result[3]
                    return (bssid, ssid, rssi)
                except Exception:
                    return None

            def filter_signal(signal: tuple[str, str, float] | None) -> bool:
                if signal is None: return False
                _, ssid, _ = signal
                return True
            
                # if ssid == "Unsupported Network": return True
                # return False
            
            signals = list(filter(filter_signal, map(parse_signal, results)))

            if len(signals) <= 0:
                return

            request = {
                "id" : None,
                "name": "name",
                "token" : "6"*32,
                "signals" : [{
                    "bssid" : s[0],
                    "ssid" : s[1],
                    "rssi" : s[2]
                } for s in signals if s is not None]
            }
            requests.post(f"{self.settings["url"]}/api/update", json=request)

__app_export__ = WiFindMyFriendsApp