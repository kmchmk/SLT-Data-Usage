from os import access, system
import read_write
import requests
import json
import urllib.parse
import input_ui

X_IBM_CLIENT_ID = '622cc49f-6067-415e-82cd-04b1b76f6377'


def get_data_usage():
    credentials = read_write.readCredentialsFromFile()
    # Get access token first
    url = "https://omniscapp.slt.lk/mobitelint/slt/sltvasoauth/oauth2/token"
    payload = "client_id={2}&grant_type=password&password={1}&scope=scope1&username={0}".format(
        credentials['username'], urllib.parse.quote(credentials['password']), X_IBM_CLIENT_ID)
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
            'x-ibm-client-id': X_IBM_CLIENT_ID,
            'authorization': "Bearer {}".format(access_token)
        }
        response = requests.request("GET", url, headers=headers)
        response = json.loads(response.text)
        data_usage = response["vas_data_summary"]["used"]

        return data_usage
    except:
        input_ui.change_account(None)
        return 'X'
