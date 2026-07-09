import app
import asyncio
# from events.input import Buttons, BUTTON_TYPES

class WiFindMyFriendsApp(app.App):

    def __init__(self):  
        pass
    #     self._init_network()

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
        pass
        # Check if the CANCEL (back) button was pressed to exit the app
        # if self.button_states.get(BUTTON_TYPES["CANCEL"]):
        #     self.button_states.clear()
        #     self.minimise() # Minimizes the app and returns to the menu

    def draw(self, ctx):
        # Draw background (Clears the screen)
        ctx.save()
        ctx.rgb(0.1, 0.1, 0.1).rectangle(-120, -120, 240, 240).fill()
        
        # Draw "Hello World" text on the round display
        ctx.rgb(1, 1, 1).move_to(-60, -30).text("WiFi(nd)")
        ctx.rgb(1, 1, 1).move_to(-30, 0).text("My")
        ctx.rgb(1, 1, 1).move_to(-60, 30).text("Friends")
        ctx.restore()

__app_export__ = WiFindMyFriendsApp