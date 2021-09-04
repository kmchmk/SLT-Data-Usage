from utils.credential_manager import *
from utils.windows_ubuntu_base import *
from PIL import ImageFont


class WindowsUtils(Utils):
    def get_font(self):
        return ImageFont.truetype("tahoma.ttf", self.get_font_size_half())


class WindowsSystemTrayIcon(SystemTrayIcon):
    pass


if __name__ == "__main__":
    credential_manager = CredentialManager()
    data_usage = DataUsage(credential_manager)
    utils = WindowsUtils()

    while(not data_usage.refresh()):
        credential_window = CredentialWindow(credential_manager)
        credential_window.start_window()

    main = WindowsSystemTrayIcon(credential_manager, data_usage, utils)
    main.start_tray_icon()
