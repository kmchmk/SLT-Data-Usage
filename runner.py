import platform
from modules.usage_manager import *

if __name__ == "__main__":
    credential_manager = CredentialManager()
    data_usage = DataUsage(credential_manager)

    while(not data_usage.refresh()):
        credential_window = CredentialWindow(credential_manager)
        credential_window.start_window()

    if(platform.system() == "Windows"):
        from tray_icons.system_tray_icon_windows import *
        utils = WindowsUtils()
        main = WindowsSystemTrayIcon(credential_manager, data_usage, utils)
        main.start_tray_icon()
    elif(platform.system() == "Linux"):
        from tray_icons.system_tray_icon_ubuntu import *
        utils = UbuntuUtils()
        main = UbuntuSystemTrayIcon(credential_manager, data_usage, utils)
        main.start_tray_icon()
    elif(platform.system() == "Darwin"):
        from tray_icons.system_tray_icon_macos import *
        main = MacOSSystemTrayIcon(credential_manager, data_usage)
        main.run()
    else:
        print("We do not support '{}' OS yet. Let's try...".format(platform.system()))
        from tray_icons.system_tray_icon_base import *
        utils = Utils()
        main = SystemTrayIcon(credential_manager, data_usage, utils)
        main.start_tray_icon()
