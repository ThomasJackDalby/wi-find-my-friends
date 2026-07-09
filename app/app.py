import asyncio
import app
import math
from events.input import Buttons, BUTTON_TYPES
from app_components import Menu, clear_background

SCREEN_BOTTOM = 120
NUMBER_OF_WAVES = 8
WAVE_DELTA = 30
WAVE_SPEED = 1

PI = 3.14
TWO_PI = 2 * 3.14

STATE_TITLE = 0
STATE_SELECT_DEVICE = 1
STATE_DEVICE_POSITION = 2

DEVICES = [
    "Tom",
    "Solan",
    "Ben"
]

class WiFindMyFriendsApp(app.App):

    def __init__(self):
        self.index = 0
        self.button_states = Buttons(self)
        self.state = STATE_TITLE

        # self.device_index = 0
        self.select_device_menu = Menu(
            self, 
            DEVICES,
            select_handler=self.on_select,
            back_handler=self.on_back
        )
    #     self._init_network()

    def on_select(self, item, position):
        print(f"User clicked item index {position}: {item}")
        # send a get request to the server to get their position
        # if the position is got, move to the show position screen
        self.state = STATE_DEVICE_POSITION

    def on_back(self):
        self.minimise()

    # def _init_network(self):
    #     try:
    #         import network
    #         self._wlan = network.WLAN(network.STA_IF)
    #         self._wlan.active(True)
    #         self._net_ok = True
    #         asyncio.create_task(self._scan_loop())
    #     except Exception:
    #         self._wlan = None
    #         self._net_ok = False

    # async def _scan_loop(self):
    #     while True:
    #         await asyncio.sleep(0.1)

    #         try:
    #             results = self._wlan.scan()
    #         except Exception:
    #             results = []

    #         # TODO: Update to discard unknown APs
    #         # Or do we just send all, and let the server discard APs which are known to not be static.
    #         self._dev_count = len(results)
    #         self._scan_age = 0.0

    #         batch = []
    #         for e in results:
    #             bssid = bytes(e[1][:6])
    #             rssi = e[3]
    #             batch.append((bssid, rssi))
    #         self._pending = batch

    def update(self, delta):
        if self.state == STATE_TITLE: self._update_title()
        elif self.state == STATE_SELECT_DEVICE: self._update_select_device(delta)
        elif self.state == STATE_DEVICE_POSITION: self._update_device_position(delta)

    def _update_title(self):
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.minimise()
        elif self.button_states.get(BUTTON_TYPES["UP"]) or self.button_states.get(BUTTON_TYPES["DOWN"]):
            self.state = STATE_SELECT_DEVICE
        self.button_states.clear()
        
    def _update_select_device(self, delta):
        self.select_device_menu.update(delta)
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.state = STATE_TITLE
        self.button_states.clear()

    def _update_device_position(self, delta):
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.state = STATE_TITLE
        self.button_states.clear()

    def draw(self, ctx):
        if self.state == STATE_TITLE: self._draw_title(ctx)
        elif self.state == STATE_SELECT_DEVICE: self._draw_select_device(ctx)
        elif self.state == STATE_DEVICE_POSITION: self._draw_device_position(ctx)

    def _draw_title(self, ctx):
        ctx.save()
        clear_background(ctx)
        
        # draw radar waves
        ctx.line_width = 2
        radius = self.index
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

        self.index += WAVE_SPEED
        if self.index > WAVE_DELTA:
            self.index = 0

    def _draw_select_device(self, ctx):
        clear_background(ctx)
        self.select_device_menu.draw(ctx)

    def _draw_device_position(self, ctx):
        clear_background(ctx)
        
        # ctx.line_width = 2
        ctx.rgb(1, 1, 1)
        ctx.text_align = ctx.CENTER
        ctx.font_size = 20
        ctx.move_to(0, 0).text("I have no friggen idea..")

        ctx.restore()


__app_export__ = WiFindMyFriendsApp