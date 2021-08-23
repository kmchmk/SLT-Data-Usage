
import rumps

class MacOSTrayIcon(rumps.App):
    def format_usage(self, usage, no_text=False):
        if usage == "": return "No Data"
        if no_text: return usage.split(": ")[1].replace("/ ", "(") + ")"
        return usage.replace("/ ", "(") + ")"

    def __init__(self, credential_manager, data_usage):
        self.selected = "Anytime"
        self.no_text_view = False
        super(MacOSTrayIcon, self).__init__(self.format_usage(data_usage.get_anytime_report()))
        self.menu = [data_usage.get_package_name(), ["Change View", ["Anytime", "Night Time", "Total", "Extra GB", "VAS", "Bonus Data", "No Text View"]],
                     "View Summary", "Logout & Quit"]
        self._data_usage = data_usage
        self._credential_manager = credential_manager

    def refresh_views(self):
        if self.selected == "Anytime": self.anytime_onoff("")
        if self.selected == "Night Time": self.nighttime_onoff("")
        if self.selected == "Total": self.total_onoff("")
        if self.selected == "Extra GB": self.extragb_onoff("")
        if self.selected == "VAS": self.vas_onoff("")
        if self.selected == "Bonus Data": self.bonus_onoff("")

    @rumps.clicked("Change View", "No Text View")
    def update_text_view(self, sender):
        sender.state = not sender.state
        self.no_text_view = not self.no_text_view
        self.refresh_views()

    @rumps.clicked("View Summary")
    def view_summary(self, _):
        rumps.alert(self._data_usage.get_usage_report())

    @rumps.clicked("Logout & Quit")
    def view_summary(self, _):
        self._credential_manager.write_credentials_to_file("", "")
        rumps.quit_application()

    @rumps.clicked("Change View", "Anytime")
    def anytime_onoff(self, sender):
        if self.no_text_view:
            super(MacOSTrayIcon, self).__init__(self.format_usage(self._data_usage.get_anytime_report(), True))
        else:
            super(MacOSTrayIcon, self).__init__(self.format_usage(self._data_usage.get_anytime_report()))
        self.selected = "Anytime"

    @rumps.clicked("Change View", "Night Time")
    def nighttime_onoff(self, sender):
        if self.no_text_view:
            super(MacOSTrayIcon, self).__init__(self.format_usage(self._data_usage.get_night_report(), True))
        else:
            super(MacOSTrayIcon, self).__init__(self.format_usage(self._data_usage.get_night_report()))
        self.selected = "Night Time"

    @rumps.clicked("Change View", "Total")
    def total_onoff(self, sender):
        if self.no_text_view:
            super(MacOSTrayIcon, self).__init__(self.format_usage(self._data_usage.get_total_report(), True))
        else:
            super(MacOSTrayIcon, self).__init__(self.format_usage(self._data_usage.get_total_report()))
        self.selected = "Total"

    @rumps.clicked("Change View", "Extra GB")
    def extragb_onoff(self, sender):
        if self.no_text_view:
            super(MacOSTrayIcon, self).__init__(self.format_usage(self._data_usage.get_data_report(EXTRA_GB_DATA_SUMMARY, "Extra"), True))
        else:
            super(MacOSTrayIcon, self).__init__(self.format_usage(self._data_usage.get_data_report(EXTRA_GB_DATA_SUMMARY, "Extra")))
        self.selected = "Extra GB"

    @rumps.clicked("Change View", "VAS")
    def vas_onoff(self, sender):
        if self.no_text_view:
            super(MacOSTrayIcon, self).__init__(self.format_usage(self._data_usage.get_data_report(VAS_DATA_SUMMARY, "VAS"), True))
        else:
            super(MacOSTrayIcon, self).__init__(self.format_usage(self._data_usage.get_data_report(VAS_DATA_SUMMARY, "VAS")))
        self.selected = "VAS"

    @rumps.clicked("Change View", "Bonus Data")
    def bonus_onoff(self, sender):
        if self.no_text_view:
            super(MacOSTrayIcon, self).__init__(self.format_usage(self._data_usage.get_data_report(BONUS_DATA_SUMMARY, "Bonus"), True))
        else:
            super(MacOSTrayIcon, self).__init__(self.format_usage(self._data_usage.get_data_report(BONUS_DATA_SUMMARY, "Bonus")))
        self.selected = "Bonus Data"

    @rumps.timer(300)
    def refresh_content(self, sender):
        self._data_usage.refresh()
        self.refresh_views()