from os import access, system
import read_write
import requests
import json
import urllib.parse
import input_ui


class DataUsage:
    X_IBM_CLIENT_ID = '622cc49f-6067-415e-82cd-04b1b76f6377'

    def __init__(self):
        pass

    def refresh(self):
        credentials = read_write.readCredentialsFromFile()
        # Get access token first
        url = "https://omniscapp.slt.lk/mobitelint/slt/sltvasoauth/oauth2/token"
        payload = "client_id={2}&grant_type=password&password={1}&scope=scope1&username={0}".format(
            credentials['username'], urllib.parse.quote(credentials['password']), self.X_IBM_CLIENT_ID)
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
            self.response = json.loads(requests.request(
                "GET", url, headers=headers).text)
            self.package_name = self.response["my_package_info"]["package_name"]

        except:
            input_ui.change_account(None)
            self.response = None

    def get_summary(self):
        if(not self.response):
            return "X"
        elif(self.package_name.startswith("UNLIMITED FLASH")):
            return self.response["vas_data_summary"]["used"]
        else:
            return self.response["my_package_info"]["usageDetails"][1]["used"]

    def get_usage_report(self):
        if(not self.response):
            return "Incorrect credentials..."

        # Let's creat a full report
        report = self.package_name

        if(self.response["bonus_data_summary"]):
            bonus_used = self.response["bonus_data_summary"]["used"]
            bonus_limit = self.response["bonus_data_summary"]["limit"]
            report += "\nBonus:  {} / {}".format(bonus_used, bonus_limit)

        if(self.response["vas_data_summary"]):
            vas_used = self.response["vas_data_summary"]["used"]
            vas_limit = self.response["vas_data_summary"]["limit"]
            report += "\nVAS:  {} / {}".format(vas_used, vas_limit)

        if(self.response["extra_gb_data_summary"]):
            extra_gb_used = self.response["extra_gb_data_summary"]["used"]
            extra_gb_limit = self.response["extra_gb_data_summary"]["limit"]
            report += "\nExtra:  {} / {}".format(extra_gb_used, extra_gb_limit)

        if(len(self.response["my_package_info"]["usageDetails"]) > 0):
            anytime_used = self.response["my_package_info"]["usageDetails"][0]["used"]
            anytime_limit = self.response["my_package_info"]["usageDetails"][0]["limit"]
            report += "\nAnytime:  {} / {}".format(anytime_used, anytime_limit)

            if(len(self.response["my_package_info"]["usageDetails"]) > 1):
                total_used = self.response["my_package_info"]["usageDetails"][1]["used"]
                total_limit = self.response["my_package_info"]["usageDetails"][1]["limit"]
                report += "\nNight:  {} / {}".format(float(total_used) - float(
                    anytime_used), float(total_limit) - float(anytime_limit))
                report += "\nTotal:  {} / {}".format(total_used, total_limit)
        return report
