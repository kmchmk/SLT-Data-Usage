import pystray
from PIL import ImageDraw, ImageFont
import PIL  # Imported again due to multiple "Image" classes
import time
import requests
import json
import urllib.parse
import base64
from tkinter import *
import platform

SIZE = 100
FONT_TYPE = None
if platform.system() == "Windows":
    FONT_TYPE = ImageFont.truetype("tahoma.ttf", SIZE//2)
elif platform.system() == "Linux": # Probably Ubuntu
    FONT_TYPE = ImageFont.truetype("UbuntuMono-R.ttf", SIZE//2)
elif platform.system() == "Darwin": # MacOS
    FONT_TYPE = ImageFont.truetype("Symbol.ttf", SIZE//2)
else:
    raise Exception("Sorry, we do not support '{}' OS yet.".format(platform.system()))
# ToDo - I used yellow below because of the System wide Dark theme
FONT_COLOUR = 'yellow'
TOP_LEFT = (0, 0)
REFRESH_INTERVAL = 120  # seconds


class CredentialManager:

    CREDENTIALS_FILE_NAME = 'credentials.json'

    def __init__(self):
        self._load_credentials_from_file()

    def get_username(self):
        return self._username

    def get_password(self):
        return self._password

    def write_credentials_to_file(self, username, password):
        credentials = {
            "username": username,
            "password": password
        }

        # Encrypt credentials -> credentialBytes
        credentialJson = json.dumps(credentials)
        credentialBytes = base64.b64encode(credentialJson.encode('ascii'))

        # Write to file
        with open(self.CREDENTIALS_FILE_NAME, 'wb') as credentialFile:
            credentialFile.write(credentialBytes)

        self._username = username
        self._password = password

    def _load_credentials_from_file(self):
        try:
            # Read from file
            with open(self.CREDENTIALS_FILE_NAME, 'rb') as credentialFile:
                credentialBytes = credentialFile.read()

            # Decrypt credentialBytes -> credentials
            credentialJson = base64.b64decode(credentialBytes).decode('ascii')
            credentials = json.loads(credentialJson)
            self._username = credentials["username"]
            self._password = credentials["password"]
        except:
            self._username = ""
            self._password = ""


class CredentialWindow:

    def __init__(self, credential_manager):

        self._credential_manager = credential_manager

        self._root = Tk()
        self._root.resizable(False, False)
        self._root.title('SLT Credentials')

        Label(self._root, text='Username :').grid(row=0, column=0)
        Label(self._root, text='Password :').grid(row=1, column=0)

        self._tf_username = Entry(self._root)
        self._tf_username.grid(row=0, column=1)
        self._tf_password = Entry(self._root, justify=LEFT)
        self._tf_password.grid(row=1, column=1)

        frame = Frame(self._root)
        frame.grid(row=2, columnspan=2)
        Button(frame, text='Save',
               command=self._function_save).grid(row=0, column=0,)
        Button(frame, text='Cancel',
               command=self._function_cancel).grid(row=0, column=1)

    def _function_save(self):
        self._credential_manager.write_credentials_to_file(
            self._tf_username.get(), self._tf_password.get())
        self._root.destroy()

    def _function_cancel(self):
        self._root.destroy()

    def start_window(self):
        self._root.mainloop()


class DataUsage:
    X_IBM_CLIENT_ID = '622cc49f-6067-415e-82cd-04b1b76f6377'

    def __init__(self, credential_manager):
        self._credential_manager = credential_manager

    def refresh(self):
        # Get access token first
        url = "https://omniscapp.slt.lk/mobitelint/slt/sltvasoauth/oauth2/token"
        payload = "client_id={2}&grant_type=password&password={1}&scope=scope1&username={0}".format(
            self._credential_manager.get_username(), urllib.parse.quote(self._credential_manager.get_password()), self.X_IBM_CLIENT_ID)
        headers = {'content-type': "application/x-www-form-urlencoded"}
        response = requests.request("POST", url, data=payload, headers=headers)
        response = json.loads(response.text)

        try:
            access_token = response["access_token"]
            subscriberid = response["metadata"]

            # Get the data usage
            url = "https://omniscapp.slt.lk/mobitelint/slt/sltvasservices/dashboard/summary"
            headers = {
                'subscriberid': subscriberid,
                'x-ibm-client-id': self.X_IBM_CLIENT_ID,
                'authorization': "Bearer {}".format(access_token)
            }
            self._response = json.loads(requests.request("GET", url,
                                                         headers=headers).text)
            self.package_name = self._response["my_package_info"]["package_name"]

        except:
            credential_window = CredentialWindow(self._credential_manager)
            credential_window.start_window()
            self._response = None

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
            report += "\nBonus:  {} / {}".format(bonus_used, bonus_limit)

        if(self._response["vas_data_summary"]):
            vas_used = self._response["vas_data_summary"]["used"]
            vas_limit = self._response["vas_data_summary"]["limit"]
            report += "\nVAS:  {} / {}".format(vas_used, vas_limit)

        if(self._response["extra_gb_data_summary"]):
            extra_gb_used = self._response["extra_gb_data_summary"]["used"]
            extra_gb_limit = self._response["extra_gb_data_summary"]["limit"]
            report += "\nExtra:  {} / {}".format(extra_gb_used, extra_gb_limit)

        if(len(self._response["my_package_info"]["usageDetails"]) > 0):
            anytime_used = self._response["my_package_info"]["usageDetails"][0]["used"]
            anytime_limit = self._response["my_package_info"]["usageDetails"][0]["limit"]
            report += "\nAnytime:  {} / {}".format(anytime_used,
                                                   anytime_limit if anytime_limit else "Unlimited")

            if(len(self._response["my_package_info"]["usageDetails"]) > 1):
                total_used = self._response["my_package_info"]["usageDetails"][1]["used"]
                total_limit = self._response["my_package_info"]["usageDetails"][1]["limit"]
                report += "\nNight:  {} / {}".format(round(float(total_used) - float(anytime_used), 1),
                                                     round(float(total_limit) - float(anytime_limit), 1))
                report += "\nTotal:  {} / {}".format(total_used, total_limit)
        return report


class Main:

    def __init__(self):
        self._credential_manager = CredentialManager()
        self._data_usage = DataUsage(self._credential_manager)

    def get_empty_image(self):
        return PIL.Image.new('RGBA', (SIZE, SIZE//2))  # Empty image

    def refresh(self, icon):
        image = self.get_empty_image()
        draw = ImageDraw.Draw(image)
        self._data_usage.refresh()
        draw.text(TOP_LEFT, self._data_usage.get_summary(),
                  font=FONT_TYPE, fill=FONT_COLOUR)
        icon.icon = image
        icon.title = self._data_usage.get_usage_report()

    def update_forever(self, icon):
        icon.visible = True
        while icon.visible:
            self.refresh(icon)
            time.sleep(REFRESH_INTERVAL)
        icon.stop()

    def open_credential_window(self, icon):
        credential_window = CredentialWindow(self._credential_manager)
        credential_window.start_window()

    def exit_method(self, icon):
        icon.visible = False


main = Main()
menu = (pystray.MenuItem('Refresh', main.refresh),
        pystray.MenuItem('Change account', main.open_credential_window),
        pystray.MenuItem('Exit', main.exit_method))
icon = pystray.Icon("icon_name", main.get_empty_image(), "Starting...", menu)

icon.run(main.update_forever)
