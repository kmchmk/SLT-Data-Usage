import json
import base64

CREDENTIALS_FILE_NAME = 'credentials.json'


def writeCredentialsToFile(username, password):
    credentials = {
        "username": username,
        "password": password
    }

    # Encrypt credentials -> credentialBytes
    credentialJson = json.dumps(credentials)
    credentialBytes = base64.b64encode(credentialJson.encode('ascii'))

    # Write to file
    with open(CREDENTIALS_FILE_NAME, 'wb') as credentialFile:
        credentialFile.write(credentialBytes)


def readCredentialsFromFile():
    try:
        # Read from file
        with open(CREDENTIALS_FILE_NAME, 'rb') as credentialFile:
            credentialBytes = credentialFile.read()

        # Decrypt credentialBytes -> credentials
        credentialJson = base64.b64decode(credentialBytes).decode('ascii')
        credentials = json.loads(credentialJson)
        return credentials
    except:
        emptyCredentials = {
            "username": "",
            "password": ""
        }
        return emptyCredentials
