from modules.CredentialManager import *
from tkinter import *
import pystray
from PIL import ImageDraw, Image
import time

class SystemTrayIcon:

    def __init__(self, credential_manager, data_usage, utils):
        self._credential_manager = credential_manager
        self._data_usage = data_usage
        self._utils = utils

    def get_empty_image(self):
        return Image.new('RGBA', (self._utils.get_font_size(), self._utils.get_font_size_half()))  # Empty image

    def display_value(self, icon):
        self._data_usage.refresh()
        image = self.get_empty_image()
        draw = ImageDraw.Draw(image)
        draw.text(self._utils.get_location(), self._data_usage.get_summary(),
                  font=self._utils.get_font(), fill=self._utils.get_font_colour())
        icon.icon = image
        icon.title = self._data_usage.get_usage_report()

    def update_forever(self, icon):
        icon.visible = True
        while icon.visible:
            self.display_value(icon)
            time.sleep(REFRESH_INTERVAL)
        icon.stop()

    def show_full_report(self, icon):
        icon.notify(self._data_usage.get_usage_report(), " ")

    def exit_method(self, icon):
        icon.visible = False

    def logout_and_exit(self, icon):
        self._credential_manager.write_credentials_to_file("", "")
        self.exit_method(icon)

    def start_tray_icon(self):
        menu = pystray.Menu(pystray.MenuItem('Refresh', self.display_value, default=True),
                            pystray.MenuItem('Exit', self.exit_method),
                            pystray.MenuItem('Logout & exit', self.logout_and_exit))
        icon = pystray.Icon("icon_name", self.get_empty_image(), "Starting...", menu)
        icon.run(self.update_forever)


