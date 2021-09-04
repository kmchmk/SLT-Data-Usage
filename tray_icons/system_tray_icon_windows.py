from tray_icons.system_tray_icon_base import *
from PIL import ImageFont
import pystray._win32 # This is required. Do not delete.


class WindowsUtils(Utils):
    def get_font(self):
        return ImageFont.truetype("tahoma.ttf", self.get_font_size_half())


class WindowsSystemTrayIcon(SystemTrayIcon):
    pass
