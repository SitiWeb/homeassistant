# controller.py
import tkinter as tk

from view.view import TuyaView
class TuyaController:
    def __init__(self, model):
        self.model = model
        self.root = tk.Tk()  # Initialize your Tkinter root window
        
        self.view = TuyaView(self.root, self.model)  # Pass model to the view
        self.whiteness = None
        self.brightness = None
        if not self.model.devices:
            # Load initial devices and display them
            self.refresh_devices()
        else:
            self.view.set_device_list(self.get_status())
       
        # Bind buttons to control functions
        self.view.bind_on_button(self.turn_on_selected)
        self.view.bind_off_button(self.turn_off_selected)
        self.view.bind_refresh_button(self.refresh_devices)

        # Bind slider change events
        self.view.bind_brightness_change(self.on_brightness_change)
        self.view.bind_whiteness_change(self.on_whiteness_change)

    def refresh_devices(self):
        """Refresh the list of devices and update the view."""
        self.view.show_loading_popup()  # Show loading popup
        devices = self.model.scan_devices()  # Scan for devices
        self.view.set_device_list(self.get_status())  # Update the view with the new device list
        self.view.close_loading_popup()  # Close the loading popup

    def turn_on_selected(self):
        device_ids = self.view.get_selected_device_ids()
        brightness = self.view.get_brightness()
        whiteness = self.view.get_whiteness()
        self.view.turn_on_selected_devices()
        self.model.control_devices(device_ids, action="on", brightness=brightness, whiteness=whiteness)
        print(f"Turned on devices: {device_ids} with brightness {brightness} and whiteness {whiteness}")

    def turn_off_selected(self):
        device_ids = self.view.get_selected_device_ids()
        result = self.model.control_devices(device_ids, action="off")
        print(result)
        self.view.turn_off_selected_devices()
        print(f"Turned off devices: {device_ids}")

    def turn_off_device(self, device_id):
        """Turn off a single device."""
        self.model.control_devices([device_id], action="off")  # Call the model to turn off the device
        button = self.view.device_buttons[device_id]
        button.configure(image=self.lightbulb_off)  # Update icon to off
        toggle_button = self.view.toggle_buttons[device_id] 
        toggle_button.configure(text="on", command=lambda device=device_id: self.turn_on_device(device), image=self.view.img_off)

    def turn_on_device(self, device_id):
        """Turn off a single device."""
        self.model.control_devices([device_id], action="on")  # Call the model to turn off the device
        button = self.view.device_buttons[device_id]
        button.configure(image=self.lightbulb_on)  # Update icon to off
        toggle_button = self.view.toggle_buttons[device_id] 
        toggle_button.configure(text="off", command=lambda device=device_id: self.turn_off_device(device), image=self.view.img_on)


    def get_status(self):
        device_ids = self.model.get_all_device_ids()
        result = self.model.control_devices(device_ids, action="check")
        print(result)
        return(result)

    def on_brightness_change(self, event):
        """Handle brightness slider change."""
        device_ids = self.view.get_selected_device_ids()
        brightness = self.view.get_brightness()
        self.brightness = brightness
        if device_ids:
            brightness = self.view.get_brightness()
            self.model.control_devices(device_ids, action=None, brightness=brightness)
            for device_id in device_ids:
               
                self.set_device_text(device_id)

    def on_whiteness_change(self, event):
        """Handle whiteness slider change."""
        device_ids = self.view.get_selected_device_ids()
        whiteness = self.view.get_whiteness()
        self.whiteness = whiteness
        if device_ids:
            
            print(self.model.control_devices(device_ids, action=None, whiteness=whiteness))
            for device_id in device_ids:
               
                self.set_device_text(device_id)

    def set_device_text(self, device_id):
        button = self.view.device_buttons[device_id]
        button.configure(text=f"B:{self.brightness}% | W:{self.whiteness}%")