import tinytuya
import threading
import json
import os
import sys
from queue import Queue

from pprint import pprint


def resource_path(relative_path):
    """Get absolute path to resource, works for development and PyInstaller bundled executable."""
    try:
        # When running from the PyInstaller executable
        base_path = sys._MEIPASS
    except AttributeError:
        # When running from the source
        base_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    return os.path.join(base_path, relative_path)

# Set custom path for device configuration file
tinytuya.DEVICEFILE = resource_path("data/devices.json")
tinytuya.SNAPSHOTFILE = resource_path("data/snapshot.json")
tinytuya.CONFIGFILE = resource_path("data/tinytuya.json")
tinytuya.RAWFILE = resource_path("data/tuya-raw.json")
class TuyaModel:
    def __init__(self):
        self.custom_order = [
            "Tafel links",
            "Tafel midden rechts",
            "Tafel midden",
            "Tafel midden links",
            "Tafel rechts",
        ]
        self.devices = []
        self.load_devices()
        

    def load_devices(self):
        devices = tinytuya.Device(dev_id="bff54e8235e708b18f8md8", address="192.168.1.99")
        devices.status()
        print(devices.send())
        """Load saved devices from a file if available."""
        if os.path.exists(resource_path("data/devices-list.json")):
            with open(resource_path("data/devices-list.json"), "r") as file:
                devices = json.load(file)

                def custom_sort_key(device):
                    return self.custom_order.index(device["name"]) if device["name"] in self.custom_order else len(self.custom_order)
                devices.sort(key=custom_sort_key)
                self.devices = devices
        else:
            self.devices = []

    def get_all_device_ids(self):
        """Return a list of all device IDs."""
        return [device['id'] for device in self.devices]

    def save_devices(self):
        """Save the current list of devices to a file."""
        with open(resource_path("data/devices-list.json"), "w") as file:
            json.dump(self.devices, file)

    def scan_devices(self):
        """Scan for devices on the network and save the results."""
        print("Scanning for Tuya devices...")
      
        devices = tinytuya.deviceScan(verbose=True)
        pprint(devices)
        self.devices = [
            {
                "name": device.get("name", "Unknown Device"),
                "id": device["gwId"],
                "ip": device["ip"],
                "key": device.get("key", None)
            }
            for device in devices.values()
        ]
        self.save_devices()
        return self.devices

    def control_devices(self, device_ids, action, brightness=None, whiteness=None):
        """Control multiple devices at once and collect the results."""
        results = Queue()  # Use a thread-safe Queue to collect the results
        results_dict = {}  # Store results by device ID

        def control_device(device_info):
            """Control an individual device based on action and settings, and store the result."""
            device = tinytuya.BulbDevice(device_info["id"], device_info["ip"], device_info["key"])
            device.set_version(3.3)

            # Perform the action and collect the result
            result = {"id": device_info["id"], "name": device_info["name"], "status": None}
            if action == "on":
                device.turn_on()
                result["status"] = "on"
            elif action == "off":
                device.turn_off()
                result["status"] = "off"
            #elif action == "check":
            else:
                
                result["status"] = device.status()
                print(result["status"])
            # Set brightness and whiteness if provided, converted from percentage
            if brightness is not None:
                brightness_value = 25 + int(brightness * (255 - 25) / 100)
                device.set_value(2, brightness_value, True)

            if whiteness is not None:
                whiteness_value = int(whiteness * 255 / 100)
                device.set_value(3, whiteness_value, True)

            # Store result in the dictionary
            results_dict[device_info["id"]] = result

        # Create a thread for each device action
        threads = []
        for device_info in self.devices:
            if device_info["id"] in device_ids:
                thread = threading.Thread(target=control_device, args=(device_info,))
                threads.append(thread)
                thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Collect results in the custom order
        device_statuses = []
        for device_name in self.custom_order:
            for device_info in self.devices:
                if device_info["name"] == device_name and device_info["id"] in results_dict:
                    device_statuses.append(results_dict[device_info["id"]])

        return device_statuses  # Return the collected statuses
