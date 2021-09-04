from tkinter import *
import requests
import json
import urllib.parse
import base64
import sys
import os

REFRESH_INTERVAL = 120  # seconds
TEST_MODE = False  # Temporary value added for testing purposes

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
        self._root.attributes('-topmost', True)
        self._root.title('SLT Credentials')
        self._root.eval('tk::PlaceWindow . center')
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
        if(TEST_MODE):  # This block is added for testing purposes
            self._response = json.loads(
                '{"status":"NORMAL","reported_time":"26-Aug-2021 07:36 PM","my_package_summary":{"limit":"76.7","used":"35.4","volume_unit":"GB"},"bonus_data_summary":{"limit":"6.6","used":"6.6","volume_unit":"GB"},"free_data_summary":null,"vas_data_summary":null,"extra_gb_data_summary":null,"my_package_info":{"package_name":"WEB FAMILY PLUS","package_summary":null,"usageDetails":[{"name":"Standard","limit":"30.7","remaining":"4.4","used":"26.3","percentage":14,"volume_unit":"GB","expiry_date":"31-Aug","claim":null,"unsubscribable":false,"timestamp":0,"subscriptionid":null},{"name":"Total (Standard + Free)","limit":"76.7","remaining":"41.3","used":"135.4","percentage":54,"volume_unit":"GB","expiry_date":"31-Aug","claim":null,"unsubscribable":false,"timestamp":0,"subscriptionid":null}],"reported_time":"26-Aug-2021 07:36 PM"}}')
            self._package_name = self._response["my_package_info"]["package_name"]
            return True
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
            self._package_name = self._response["my_package_info"]["package_name"]
        except:
            self._response = None
        return bool(self._response)

    def get_summary(self):
        if(not self._response):
            return "X"
        elif(self._package_name.startswith("UNLIMITED FLASH")):
            return self._response["vas_data_summary"]["used"]
        else:
            return self._response["my_package_info"]["usageDetails"][1]["used"]

    def get_data_report(self, data_type, reference):
        if (self._response[data_type]):
            bonus_used = self._response[data_type]["used"]
            bonus_limit = self._response[data_type]["limit"]
            return "{}: {} / {}".format(reference, bonus_used, bonus_limit)

    def get_package_name(self):
        return self._package_name

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
        if (len(self._response["my_package_info"]["usageDetails"]) > 1):
            total_used = self._response["my_package_info"]["usageDetails"][1]["used"]
            total_limit = self._response["my_package_info"]["usageDetails"][1]["limit"]
            return "Total: {} / {}".format(total_used, total_limit)

    def _format_line(self, usage):
        if(usage):
            return "\n{}".format(usage)
        return ""

    def get_usage_report(self):
        if(not self._response):
            return "Error occured!\nPlease refresh again."

        # Let's creat a full report
        report = self._package_name
        report += self._format_line(self.get_data_report(BONUS_DATA_SUMMARY, "Bonus"))
        report += self._format_line(self.get_data_report(VAS_DATA_SUMMARY, "VAS"))
        report += self._format_line(self.get_data_report(EXTRA_GB_DATA_SUMMARY, "Extra"))
        report += self._format_line(self.get_anytime_report())
        report += self._format_line(self.get_night_report())
        report += self._format_line(self.get_total_report())

        reported_time = self._response["my_package_info"]["reported_time"]
        report += "\n[As at {}]".format(reported_time)
        return report
