from os import access, system

from requests.models import Response
import read_write
import requests
import json
import urllib.parse
import input_ui


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
            credential_window = input_ui.CredentialWindow(
                self._credential_manager)
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
