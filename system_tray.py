from read_write import CredentialManager
import pystray._win32
from PIL import Image, ImageDraw, ImageFont
import time
import data_usage
import input_ui

size = 100
font_type = ImageFont.truetype("tahoma.ttf", size//2)
TOP_LEFT = (0, 0)
REFRESH_INTERVAL = 120  # seconds


class Main:

    def __init__(self):
        self._credential_manager = CredentialManager()
        self._data_usage = data_usage.DataUsage(self._credential_manager)

    def get_empty_image(self): return Image.new(
        'RGBA', (size, size//2))  # Empty image

    def refresh(self, icon):
        image = self.get_empty_image()
        draw = ImageDraw.Draw(image)
        # ToDo - I used yellow below because of the System wide Dark theme
        self._data_usage.refresh()
        draw.text(TOP_LEFT, self._data_usage.get_summary(),
                  font=font_type, fill='yellow')
        icon.icon = image
        icon.title = self._data_usage.get_usage_report()

    def update_forever(self, icon):
        icon.visible = True
        while icon.visible:
            self.refresh(icon)
            time.sleep(REFRESH_INTERVAL)
        icon.stop()

    def open_credential_window(self, icon):
        credential_window = input_ui.CredentialWindow(self._credential_manager)
        credential_window.start_window()

    def exit_method(self, icon):
        icon.visible = False


main = Main()
menu = (pystray.MenuItem('Refresh', main.refresh),
        pystray.MenuItem('Change account', main.open_credential_window),
        pystray.MenuItem('Exit', main.exit_method))
icon = pystray.Icon("icon_name", main.get_empty_image(), "Starting...", menu)

icon.run(main.update_forever)
