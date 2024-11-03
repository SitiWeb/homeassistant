import os
import hashlib
import hmac
import requests
import time
import json

class TuyaAPI:
    def __init__(self, config_file="config.json", debug=False):
        # Load configuration
        self.debug = debug
        self.config_file = "config.secret.json" if os.path.exists("config.secret.json") else config_file
        self._load_config()
        
        # Initialize constants
        self.EmptyBodyEncoded = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        self.tuyatime = str(int(time.time()) * 1000)
        self.access_token = None

    def _load_config(self):
        with open(self.config_file, "r") as jsonfile:
            configData = json.load(jsonfile)
            self.ClientID = configData["ClientID"]
            self.ClientSecret = configData["ClientSecret"]
            self.BaseUrl = configData["BaseUrl"]
            self.deviceList = configData["deviceList"]
            if self.debug:
                print("Configuration loaded successfully")

    def _generate_signature(self, StringToSign):
        return hmac.new(self.ClientSecret.encode(), StringToSign.encode(), hashlib.sha256).hexdigest().upper()

    def get_access_token(self):
        URL = "/v1.0/token?grant_type=1"
        StringToSign = f"{self.ClientID}{self.tuyatime}GET\n{self.EmptyBodyEncoded}\n\n{URL}"
        
        if self.debug:
            print("StringToSign for AccessToken is:", StringToSign)

        AccessTokenSign = self._generate_signature(StringToSign)
        headers = {
            "sign_method": "HMAC-SHA256",
            "client_id": self.ClientID,
            "t": self.tuyatime,
            "mode": "cors",
            "Content-Type": "application/json",
            "sign": AccessTokenSign
        }

        response = requests.get(self.BaseUrl + URL, headers=headers).json()
        self.access_token = response.get("result", {}).get("access_token")

        if self.debug:
            print("Access token retrieved:", self.access_token)

        return self.access_token

    def get_device_info(self):
        if not self.access_token:
            self.get_access_token()

        device_ids = ",".join(self.deviceList.keys())
        URL = f"/v2.0/cloud/thing/batch?device_ids={device_ids}"
        StringToSign = f"{self.ClientID}{self.access_token}{self.tuyatime}GET\n{self.EmptyBodyEncoded}\n\n{URL}"
        
        if self.debug:
            print("StringToSign for DeviceInfo is:", StringToSign)

        RequestSign = self._generate_signature(StringToSign)
        headers = {
            "sign_method": "HMAC-SHA256",
            "client_id": self.ClientID,
            "t": self.tuyatime,
            "mode": "cors",
            "Content-Type": "application/json",
            "sign": RequestSign,
            "access_token": self.access_token
        }

        response = requests.get(self.BaseUrl + URL, headers=headers).json()

        if self.debug:
            print("Device Info Response:", response)

        devices_info = response.get("result", [])
        for device_info in devices_info:
            id = device_info.get("id")
            localKey = device_info.get("local_key")
            customName = device_info.get("custom_name")
            print(f"{id}\t{localKey}\t{customName}")
            
    def get_devices(self):
        if not self.access_token:
            self.get_access_token()

        device_ids = ",".join(self.deviceList.keys())
        URL = f"/v2.0/cloud/thing/batch?device_ids={device_ids}"
        StringToSign = f"{self.ClientID}{self.access_token}{self.tuyatime}GET\n{self.EmptyBodyEncoded}\n\n{URL}"
        
        if self.debug:
            print("StringToSign for DeviceInfo is:", StringToSign)

        RequestSign = self._generate_signature(StringToSign)
        headers = {
            "sign_method": "HMAC-SHA256",
            "client_id": self.ClientID,
            "t": self.tuyatime,
            "mode": "cors",
            "Content-Type": "application/json",
            "sign": RequestSign,
            "access_token": self.access_token
        }

        response = requests.get(self.BaseUrl + URL, headers=headers).json()

        if self.debug:
            print("Device Info Response:", response)

        devices_info = response.get("result", [])
        for device_info in devices_info:
            id = device_info.get("id")
            localKey = device_info.get("local_key")
            customName = device_info.get("custom_name")
            print(f"{id}\t{localKey}\t{customName}")
# Usage example:
tuya_api = TuyaAPI(debug=True)
tuya_api.get_access_token()
tuya_api.get_device_info()
