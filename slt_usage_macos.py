import rumps
from slt_usage import *

class MacOSSystemTrayIcon(rumps.App):

    def __init__(self, credential_manager, data_usage):
        self._data_usage = data_usage
        self._credential_manager = credential_manager

        super(MacOSSystemTrayIcon, self).__init__("SLT_Data_Usage")
        self.menu = [self._data_usage.get_package_name(),
                     "Change View",
                     "View Summary",
                     "Logout & Quit"]
        self.update_menu()

    def update_menu(self):
        if(self._data_usage.get_anytime_report()):
            self.menu.get("Change View").add(rumps.MenuItem("Anytime", self.anytime_onoff))
        if(self._data_usage.get_night_report()):
            self.menu.get("Change View").add(rumps.MenuItem("Night Time", self.nighttime_onoff))
        if(self._data_usage.get_total_report()):
            self.menu.get("Change View").add(rumps.MenuItem("Total", self.total_onoff))
        if(self._data_usage.get_data_report(EXTRA_GB_DATA_SUMMARY, "Extra")):
            self.menu.get("Change View").add(rumps.MenuItem("Extra GB", self.extragb_onoff))
        if(self._data_usage.get_data_report(VAS_DATA_SUMMARY, "VAS")):
            self.menu.get("Change View").add(rumps.MenuItem("VAS", self.vas_onoff))
        if(self._data_usage.get_data_report(BONUS_DATA_SUMMARY, "Bonus")):
            self.menu.get("Change View").add(rumps.MenuItem("Bonus Data", self.bonus_onoff))
        self.menu.get("Change View").add(rumps.MenuItem("No Text View", self.update_text_view))

        self.selected = self.menu.get("Change View").keys()[0]  # Select the first item as default title
        self.no_text_view = False
        self.menu.get("Change View").get(self.selected).callback(None)

    def format_usage(self, usage):
        if(usage):
            if self.no_text_view:
                return usage.split(": ")[1].replace("/ ", "(") + ")"
            return usage.replace("/ ", "(") + ")"
        return "No Data"

    def update_text_view(self, sender):
        sender.state = not sender.state
        self.no_text_view = not self.no_text_view
        self.menu.get("Change View").get(self.selected).callback(None)

    @rumps.clicked("View Summary")
    def view_summary(self, _):
        rumps.alert(self._data_usage.get_usage_report())

    @rumps.clicked("Logout & Quit")
    def logout_and_quit(self, _):
        self._credential_manager.write_credentials_to_file("", "")
        rumps.quit_application()

    def anytime_onoff(self, sender):
        self.title = self.format_usage(self._data_usage.get_anytime_report())
        self.selected = "Anytime"

    def nighttime_onoff(self, sender):
        self.title = self.format_usage(self._data_usage.get_night_report())
        self.selected = "Night Time"

    def total_onoff(self, sender):
        self.title = self.format_usage(self._data_usage.get_total_report())
        self.selected = "Total"

    def extragb_onoff(self, sender):
        self.title = self.format_usage(self._data_usage.get_data_report(EXTRA_GB_DATA_SUMMARY, "Extra"))
        self.selected = "Extra GB"

    def vas_onoff(self, sender):
        self.title = self.format_usage(self._data_usage.get_data_report(VAS_DATA_SUMMARY, "VAS"))
        self.selected = "VAS"

    def bonus_onoff(self, sender):
        self.title = self.format_usage(self._data_usage.get_data_report(BONUS_DATA_SUMMARY, "Bonus"))
        self.selected = "Bonus Data"

    @rumps.timer(REFRESH_INTERVAL)
    def refresh_content(self, sender):
        self._data_usage.refresh()
        self.menu.get("Change View").get(self.selected).callback(None)


if __name__ == "__main__":
    credential_manager = CredentialManager()
    data_usage = DataUsage(credential_manager)

    while(not data_usage.refresh()):
        credential_window = CredentialWindow(credential_manager)
        credential_window.start_window()

    # this block will be a separate representation for MacOS
    main = MacOSSystemTrayIcon(credential_manager, data_usage)
    main.run()
