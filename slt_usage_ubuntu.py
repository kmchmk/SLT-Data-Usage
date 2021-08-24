from slt_usage import *
import pystray._appindicator


class UbuntuUtils(Utils):

    def isUbuntu():
        return platform.system() == "Linux"   # Probably Ubuntu

    def get_font():
        return ImageFont.truetype("UbuntuMono-R.ttf", Utils.get_font_size_half())

    def _get_font_colour(self):  # This doesn't support custom themes yet
        return 'white'  # Seems, Ubuntu top bar is always dark


class UbuntuSystemTrayIcon(SystemTrayIcon):
    def start_tray_icon(self):
        menu = pystray.Menu(pystray.MenuItem('Refresh', self.refresh, default=True),
                            pystray.MenuItem('Full report', self.show_full_report),
                            pystray.MenuItem('Exit', self.exit_method),
                            pystray.MenuItem('Logout & exit', self.logout_and_exit))
        icon = pystray.Icon("icon_name", self.get_empty_image(), "Starting...", menu)
        icon.run(self.update_forever)


if __name__ == "__main__":
    credential_manager = CredentialManager()
    data_usage = DataUsage(credential_manager)
    utils = UbuntuUtils()
    while(not data_usage.refresh()):
        credential_window = CredentialWindow(credential_manager)
        credential_window.start_window()

    main = UbuntuSystemTrayIcon(credential_manager, data_usage, utils)
    main.start_tray_icon()
