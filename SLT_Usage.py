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
import os
import darkdetect


REFRESH_INTERVAL = 120  # seconds


class Utils:

    _SIZE = 100
    _TOP_LEFT = (0, 0)

    def get_font_size():
        return Utils._SIZE

    def get_font_size_half():
        return Utils.get_font_size()//2

    def isUbuntu():
        return platform.system() == "Linux"   # Probably Ubuntu

    def get_font():
        if platform.system() == "Windows":
            return ImageFont.truetype("tahoma.ttf", Utils.get_font_size_half())
        elif Utils.isUbuntu():
            return ImageFont.truetype("UbuntuMono-R.ttf", Utils.get_font_size_half())
        elif platform.system() == "Darwin":  # MacOS
            return ImageFont.truetype("Symbol.ttf", Utils.get_font_size_half())
        else:
            raise Exception(
                "Sorry, we do not support '{}' OS yet.".format(platform.system()))

    def get_location():
        return Utils._TOP_LEFT

    def show_notification(title, body):
        if Utils.isUbuntu(): os.system("notify-send '{}' '{}'".format(title, body))


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

    def get_usage_report(self):
        if(not self._response):
            return "Incorrect credentials..."

        # Let's creat a full report
        report = self.package_name

        if(self._response["bonus_data_summary"]):
            bonus_used = self._response["bonus_data_summary"]["used"]
            bonus_limit = self._response["bonus_data_summary"]["limit"]
            report += "\nBonus: {} / {}".format(bonus_used, bonus_limit)

        if(self._response["vas_data_summary"]):
            vas_used = self._response["vas_data_summary"]["used"]
            vas_limit = self._response["vas_data_summary"]["limit"]
            report += "\nVAS: {} / {}".format(vas_used, vas_limit)

        if(self._response["extra_gb_data_summary"]):
            extra_gb_used = self._response["extra_gb_data_summary"]["used"]
            extra_gb_limit = self._response["extra_gb_data_summary"]["limit"]
            report += "\nExtra: {} / {}".format(extra_gb_used, extra_gb_limit)

        if(len(self._response["my_package_info"]["usageDetails"]) > 0):
            anytime_used = self._response["my_package_info"]["usageDetails"][0]["used"]
            anytime_limit = self._response["my_package_info"]["usageDetails"][0]["limit"]
            report += "\nAnytime: {} / {}".format(anytime_used,
                                                  anytime_limit if anytime_limit else "Unlimited")

            if(len(self._response["my_package_info"]["usageDetails"]) > 1):
                total_used = self._response["my_package_info"]["usageDetails"][1]["used"]
                total_limit = self._response["my_package_info"]["usageDetails"][1]["limit"]
                report += "\nNight: {} / {}".format(round(float(total_used) - float(anytime_used), 1),
                                                    round(float(total_limit) - float(anytime_limit), 1))
                report += "\nTotal: {} / {}".format(total_used, total_limit)

        reported_time = self._response["my_package_info"]["reported_time"]
        report += "\n[As at {}]".format(reported_time)
        return report


class SystemTrayIcon:

    def __init__(self, credential_manager, data_usage):
        self._credential_manager = credential_manager
        self._data_usage = data_usage

    def get_empty_image(self):
        return Image.new('RGBA', (Utils.get_font_size(), Utils.get_font_size_half()))  # Empty image

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
        draw.text(Utils.get_location(), self._data_usage.get_summary(),
                  font=Utils.get_font(), fill=self._get_font_colour())
        icon.icon = image
        icon.title = self._data_usage.get_usage_report()

    def update_forever(self, icon):
        icon.visible = True
        while icon.visible:
            self.refresh(icon)
            time.sleep(REFRESH_INTERVAL)
        icon.stop()

    def show_full_report(self, icon):
        Utils.show_notification(" ", self._data_usage.get_usage_report())

    def exit_method(self, icon):
        icon.visible = False

    def logout_and_exit(self, icon):
        self._credential_manager.write_credentials_to_file("", "")
        self.exit_method(icon)

    def start_tray_icon(self):
        menu = (pystray.MenuItem('Refresh', self.refresh),
                pystray.MenuItem('Exit', self.exit_method),
                pystray.MenuItem('Logout & exit', self.logout_and_exit))
        if(Utils.isUbuntu()):
            menu = (pystray.MenuItem('Full report', self.show_full_report),) + menu
        icon = pystray.Icon("icon_name", self.get_empty_image(), "Starting...", menu)
        icon.run(self.update_forever)


credential_manager = CredentialManager()
data_usage = DataUsage(credential_manager)

while(not data_usage.refresh()):
    credential_window = CredentialWindow(credential_manager)
    credential_window.start_window()

main = SystemTrayIcon(credential_manager, data_usage)
main.start_tray_icon()
