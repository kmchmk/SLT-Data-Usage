import json
import base64


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
