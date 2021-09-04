from tray_icons.system_tray_icon_base import *
from PIL import ImageFont
import pystray._appindicator  # This is required. Do not delete.


class UbuntuUtils(Utils):

    def get_font(self):
        return ImageFont.truetype("/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf", self.get_font_size_half())

    def get_font_colour(self):  # This doesn't support custom themes yet
        return 'white'  # Seems, Ubuntu top bar is always dark


class UbuntuSystemTrayIcon(SystemTrayIcon):
    def start_tray_icon(self):
        menu = pystray.Menu(pystray.MenuItem('Refresh', self.display_value, default=True),
                            pystray.MenuItem('Full report', self.show_full_report),
                            pystray.MenuItem('Exit', self.exit_method),
                            pystray.MenuItem('Logout & exit', self.logout_and_exit))
        icon = pystray.Icon("icon_name", self.get_empty_image(), "Starting...", menu)
        icon.run(self.update_forever)
