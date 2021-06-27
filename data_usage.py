from os import access
import requests, json, urllib.parse
import configparser

config = configparser.ConfigParser()
config.read('credentials.ini')

username = config['DEFAULT']['username']
password = urllib.parse.quote(config['DEFAULT']['password'])
subscriberid = config['DEFAULT']['subscriberid']
x_ibm_client_id = config['DEFAULT']['x_ibm_client_id']


def get_data_usage():
    # Get access token first
    url = "https://omniscapp.slt.lk/mobitelint/slt/sltvasoauth/oauth2/token"
    payload = "client_id={2}&grant_type=password&password={1}&scope=scope1&username={0}".format(username, password, x_ibm_client_id)
    headers = { 'content-type': "application/x-www-form-urlencoded" }
    response = requests.request("POST", url, data=payload, headers=headers)
    response = json.loads(response.text)
    access_token = response["access_token"]

    # Get the data usage
    url = "https://omniscapp.slt.lk/mobitelint/slt/sltvasservices/dashboard/summary"
    headers = {
        'subscriberid': subscriberid,
        'x-ibm-client-id': x_ibm_client_id,
        'authorization': "Bearer {}".format(access_token)
        }
    response = requests.request("GET", url, headers=headers)
    response = json.loads(response.text)
    data_usage =  response["vas_data_summary"]["used"]

    return data_usage