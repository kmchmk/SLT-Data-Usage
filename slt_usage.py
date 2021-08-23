import pystray
from tkinter import *
from PIL import ImageDraw, ImageFont, Image
import time
import requests
import json
import urllib.parse
import base64
import platform
import sys
import os.path
import darkdetect
import rumps

SIZE = 100
FONT_TYPE = None
if platform.system() == "Windows":
    FONT_TYPE = ImageFont.truetype("tahoma.ttf", SIZE//2)
elif platform.system() == "Linux":  # Probably Ubuntu
    FONT_TYPE = ImageFont.truetype("UbuntuMono-R.ttf", SIZE//2)
elif platform.system() == "Darwin":  # MacOS
    FONT_TYPE = ImageFont.truetype("Symbol.ttf", SIZE//2)
else:
    raise Exception(
        "Sorry, we do not support '{}' OS yet.".format(platform.system()))
TOP_LEFT = (0, 0)
REFRESH_INTERVAL = 120  # seconds

# defining constants for data types in SLT
BONUS_DATA_SUMMARY = 'bonus_data_summary'
EXTRA_GB_DATA_SUMMARY = 'extra_gb_data_summary'
VAS_DATA_SUMMARY = 'vas_data_summary'

class CredentialManager:

    CREDENTIALS_FILE_NAME = os.path.join(os.path.expanduser("~"), '.slt_usage.cache')
    AUTH_URL = "https://omniscapp.slt.lk/mobitelint/slt/sltvasoauth/oauth2/token"

    def __init__(self):
        self._load_credentials_from_file()

    def get_refresh_token(self):
        return self._refresh_token

    def get_subscriber_id(self):
        return self._subscriber_id

    def generate_and_write_refresh_token_to_file(self, username, password):
        payload = "client_id={2}&grant_type=password&password={1}&scope=scope1&username={0}".format(
            username, urllib.parse.quote(password), DataUsage.X_IBM_CLIENT_ID)
        headers = {'content-type': "application/x-www-form-urlencoded"}
        response = requests.request("POST", self.AUTH_URL, data=payload, headers=headers)
        response = json.loads(response.text)

        try:
            refresh_token = response["refresh_token"]
            subscriber_id = response["metadata"]
            self.write_credentials_to_file(refresh_token, subscriber_id)
        except:
            self._refresh_token = ""  # ToDo - Empty or None

    def write_credentials_to_file(self, refresh_token, subscriber_id=None):
        if(subscriber_id is None):  # This is to overload the method
            subscriber_id = self._subscriber_id

        credentials = {
            "refresh_token": refresh_token,
            "subscriber_id": subscriber_id
        }

        # Encrypt credentials -> credential_bytes
        credential_json = json.dumps(credentials)
        credential_bytes = base64.b64encode(credential_json.encode('ascii'))

        # Write to file
        with open(self.CREDENTIALS_FILE_NAME, 'wb') as credential_file:
            credential_file.write(credential_bytes)

        self._refresh_token = refresh_token
        self._subscriber_id = subscriber_id

    def _load_credentials_from_file(self):
        try:
            # Read from file
            with open(self.CREDENTIALS_FILE_NAME, 'rb') as credentialFile:
                credential_bytes = credentialFile.read()

            # Decrypt credential_bytes -> credentials
            credential_json = base64.b64decode(credential_bytes).decode('ascii')
            credentials = json.loads(credential_json)

            self._refresh_token = credentials["refresh_token"]
            self._subscriber_id = credentials["subscriber_id"]
        except:
            self._refresh_token = ""
            self._subscriber_id = ""


class CredentialWindow:

    def __init__(self, credential_manager):

        self._credential_manager = credential_manager

        self._root = Tk()
        self._root.resizable(False, False)
        self._root.title('SLT Credentials')
        # Close button event
        self._root.protocol("WM_DELETE_WINDOW", self._function_cancel)

        Label(self._root, text='Username :').grid(row=0, column=0)
        Label(self._root, text='Password :').grid(row=1, column=0)

        self._tf_username = Entry(self._root)
        self._tf_username.grid(row=0, column=1)
        self._tf_password = Entry(self._root, justify=LEFT)
        self._tf_password.grid(row=1, column=1)

        frame = Frame(self._root)
        frame.grid(row=2, columnspan=2)
        Button(frame, text='Save', command=self._function_save).grid(row=0, column=0,)
        Button(frame, text='Cancel', command=self._function_cancel).grid(row=0, column=1)

    def _function_save(self):
        self._credential_manager.generate_and_write_refresh_token_to_file(
            self._tf_username.get(), self._tf_password.get())
        self._root.destroy()

    def _function_cancel(self):
        self._root.destroy()
        sys.exit()

    def start_window(self):
        self._root.mainloop()


class DataUsage:
    X_IBM_CLIENT_ID = '622cc49f-6067-415e-82cd-04b1b76f6377'

    def __init__(self, credential_manager):
        self._credential_manager = credential_manager

    def refresh(self):
        # Get access token first
        payload = "client_id={1}&grant_type=refresh_token&refresh_token={0}&scope=scope1".format(
            urllib.parse.quote(self._credential_manager.get_refresh_token()), self.X_IBM_CLIENT_ID)
        headers = {'content-type': "application/x-www-form-urlencoded"}
        response = requests.request("POST", CredentialManager.AUTH_URL, data=payload, headers=headers)
        response = json.loads(response.text)
        try:
            access_token = response["access_token"]
            refresh_token = response["refresh_token"]

            self._credential_manager.write_credentials_to_file(refresh_token)

            # Get the data usage
            url = "https://omniscapp.slt.lk/mobitelint/slt/sltvasservices/dashboard/summary"
            headers = {
                'subscriberid': self._credential_manager.get_subscriber_id(),
                'x-ibm-client-id': self.X_IBM_CLIENT_ID,
                'authorization': "Bearer {}".format(access_token)
            }
            self._response = json.loads(requests.request("GET", url, headers=headers).text)
            self.package_name = self._response["my_package_info"]["package_name"]
        except:
            self._response = None
        return bool(self._response)

    def get_summary(self):
        if(not self._response):
            return "X"
        elif(self.package_name.startswith("UNLIMITED FLASH")):
            return self._response["vas_data_summary"]["used"]
        else:
            return self._response["my_package_info"]["usageDetails"][1]["used"]

    def get_data_report(self, data_type, reference):
        if (self._response[data_type]):
            bonus_used = self._response[data_type]["used"]
            bonus_limit = self._response[data_type]["limit"]
            return "{}: {} / {}".format(reference, bonus_used, bonus_limit)
        else:
            return ""

    def get_package_name(self):
        return self.package_name

    def get_anytime_report(self):
        if (len(self._response["my_package_info"]["usageDetails"]) > 0):
            anytime_used = self._response["my_package_info"]["usageDetails"][0]["used"]
            anytime_limit = self._response["my_package_info"]["usageDetails"][0]["limit"]
            return "Anytime: {} / {}".format(anytime_used, anytime_limit if anytime_limit else "Unlimited")

    def get_night_report(self):
        if (len(self._response["my_package_info"]["usageDetails"]) > 0):
            anytime_used = self._response["my_package_info"]["usageDetails"][0]["used"]
            anytime_limit = self._response["my_package_info"]["usageDetails"][0]["limit"]
            if (len(self._response["my_package_info"]["usageDetails"]) > 1):
                total_used = self._response["my_package_info"]["usageDetails"][1]["used"]
                total_limit = self._response["my_package_info"]["usageDetails"][1]["limit"]
                return "Night: {} / {}".format(round(float(total_used) - float(anytime_used), 1),
                                                    round(float(total_limit) - float(anytime_limit), 1))

    def get_total_report(self):
        if (len(self._response["my_package_info"]["usageDetails"]) > 0):
            if (len(self._response["my_package_info"]["usageDetails"]) > 1):
                total_used = self._response["my_package_info"]["usageDetails"][1]["used"]
                total_limit = self._response["my_package_info"]["usageDetails"][1]["limit"]
                return "Total: {} / {}".format(total_used, total_limit)

    def format_line(self, usage):
        if usage != "":
            return "\n" + usage
        return ""

    def get_usage_report(self):
        if(not self._response):
            return "Incorrect credentials..."

        # Let's creat a full report
        report = self.package_name

        report += self.format_line(data_usage.get_data_report(BONUS_DATA_SUMMARY, "Bonus"))
        report += self.format_line(data_usage.get_data_report(VAS_DATA_SUMMARY, "VAS"))
        report += self.format_line(data_usage.get_data_report(EXTRA_GB_DATA_SUMMARY, "Extra"))
        report += self.format_line(data_usage.get_anytime_report())
        report += self.format_line(data_usage.get_night_report())
        report += self.format_line(data_usage.get_total_report())

        reported_time = self._response["my_package_info"]["reported_time"]
        report += "\n[As at {}]".format(reported_time)
        return report


class SystemTrayIcon:

    def __init__(self, credential_manager, data_usage):
        self._credential_manager = credential_manager
        self._data_usage = data_usage

    def get_empty_image(self):
        return Image.new('RGBA', (SIZE, SIZE//2))  # Empty image

    def _get_font_colour(self):  # This doesn't support custom themes yet
        if(platform.system() == "Linux"):  # Seems, Ubuntu top bar is always dark
            return 'white'
        elif(darkdetect.isDark()):
            return 'white'
        else:
            return 'black'

    def refresh(self, icon):
        image = self.get_empty_image()
        draw = ImageDraw.Draw(image)
        self._data_usage.refresh()
        draw.text(TOP_LEFT, self._data_usage.get_summary(), font=FONT_TYPE, fill=self._get_font_colour())
        icon.icon = image
        icon.title = self._data_usage.get_usage_report()

    def update_forever(self, icon):
        icon.visible = True
        while icon.visible:
            self.refresh(icon)
            time.sleep(REFRESH_INTERVAL)
        icon.stop()

    def exit_method(self, icon):
        icon.visible = False

    def logout_and_exit(self, icon):
        self._credential_manager.write_credentials_to_file("", "")
        self.exit_method(icon)

    def start_tray_icon(self):
        menu = (pystray.MenuItem('Refresh', self.refresh),
                pystray.MenuItem('Exit', self.exit_method),
                pystray.MenuItem('Logout & exit', self.logout_and_exit))
        icon = pystray.Icon("icon_name", self.get_empty_image(), "Starting...", menu)
        icon.run(self.update_forever)

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


credential_manager = CredentialManager()
data_usage = DataUsage(credential_manager)

while(not data_usage.refresh()):
    credential_window = CredentialWindow(credential_manager)
    credential_window.start_window()

# this block will be a separate representation for MacOS
if platform.system() == "Darwin":
    MacOSTrayIcon(credential_manager, data_usage).run()

else:
    main = SystemTrayIcon(credential_manager, data_usage)
    main.start_tray_icon()