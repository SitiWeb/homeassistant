import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from pprint import pprint
import os
import sys
def resource_path(relative_path):
    """Get absolute path to resource, works for development and PyInstaller bundled executable."""
    try:
        # When running from the PyInstaller executable
        base_path = sys._MEIPASS
    except AttributeError:
        # When running from the source
        base_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    return os.path.join(base_path, relative_path)

class TuyaView:
    def __init__(self, root, model):  # Add model parameter
        self.root = root
        self.model = model  # Store the model in the view
        self.root.title("QuBerto's Lights Controller")

        # Create a style object and define button styles for selected and unselected states
        self.style = ttk.Style()
        self.style.configure("Unselected.TButton", background="#f0f0f0")
        self.style.configure("Selected.TButton", background="#90ee90")  # Light green for selected
        self.style.configure('flat.TButton', borderwidth=0)  # Light green for selected
        # Load and resize lightbulb icons with transparency preserved
        lightbulb_on_img = Image.open(resource_path("images/lightbulb-on.png")).convert("RGBA").resize((37, 30), Image.LANCZOS)
        lightbulb_off_img = Image.open(resource_path("images/lightbulb.png")).convert("RGBA").resize((25, 30), Image.LANCZOS)

        # Convert resized images to PhotoImage format compatible with Tkinter
        self.lightbulb_on = ImageTk.PhotoImage(lightbulb_on_img)
        self.lightbulb_off = ImageTk.PhotoImage(lightbulb_off_img)

          # Load and resize lightbulb icons with transparency preserved
        img_on_img = Image.open(resource_path("images/on.png")).convert("RGBA").resize((50, 30), Image.LANCZOS)
        img_off_img = Image.open(resource_path("images/off.png")).convert("RGBA").resize((50, 30), Image.LANCZOS)

        # Convert resized images to PhotoImage format compatible with Tkinter
        self.img_on = ImageTk.PhotoImage(img_on_img)
        self.img_off = ImageTk.PhotoImage(img_off_img)

        # Device list frame
        self.device_frame = ttk.Frame(self.root, padding="10")
        self.device_frame.grid(row=0, column=0, sticky="NSEW")

        # Device list label
        self.device_label = ttk.Label(self.device_frame, text="Device List")
        self.device_label.grid(row=0, column=0, pady=(0, 10))

        self.refresh_button = ttk.Button(self.device_frame, text="Refresh", command=None)
        self.refresh_button.grid(row=0, column=2, padx=(0, 10))

        self.select_all_button = ttk.Button(self.device_frame, text="Select/Deselect All", command=self.toggle_select_all)
        self.select_all_button.grid(row=0, column=1, padx=(0, 5))

        # Frame to hold device buttons
        self.device_buttons_frame = ttk.Frame(self.device_frame)
        self.device_buttons_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        # Keep track of device buttons and their selected state
        self.device_buttons = {}
        self.toggle_buttons = {}
        
        self.selected_devices = set()  # Use a set for easy addition/removal

        # Control Buttons in a single row
        control_frame = ttk.Frame(self.root)
        control_frame.grid(row=1, column=0, pady=(0, 5))


        self.on_button = ttk.Button(control_frame, text="Turn On")
        self.on_button.grid(row=0, column=1, padx=(5, 5))

        self.off_button = ttk.Button(control_frame, text="Turn Off", command=self.turn_off_selected_devices)
        self.off_button.grid(row=0, column=2, padx=(5, 5))

        

        # Brightness slider
        self.brightness_scale = tk.Scale(control_frame, from_=0, to=100, orient=tk.HORIZONTAL, label="Brightness")
        self.brightness_scale.grid(row=0, column=3, padx=(5, 5), pady=(5, 10))

        # Whiteness slider
        self.whiteness_scale = tk.Scale(control_frame, from_=0, to=100, orient=tk.HORIZONTAL, label="Whiteness")
        self.whiteness_scale.grid(row=0, column=4, padx=(5, 5), pady=(5, 10))

    def show_loading_popup(self):
        """Show a loading popup during device scanning."""
        self.popup = tk.Toplevel(self.root)
        self.popup.title("Loading")
        label = ttk.Label(self.popup, text="Scanning for devices, please wait...")
        label.pack(padx=20, pady=20)
        self.popup.update_idletasks()

    def close_loading_popup(self):
        """Close the loading popup once scanning is complete."""
        if hasattr(self, 'popup') and self.popup:
            self.popup.destroy()

    def set_device_text(self, device_id, b=None, w=None):
        if b == None:
            b = self.get_brightness()

        if w == None:
            w = self.get_whiteness()
        button = self.device_buttons[device_id]
        button.configure(text=f"B:{round(b)}% | W:{round(w)}%")

    def set_device_list(self, devices):
        """Populate the buttons with the scanned devices."""
        # Clear existing buttons
        for button in self.device_buttons.values():
            button.destroy()
        self.device_buttons.clear()

        # Create a button for each device in a single row
        for column_index, device in enumerate(devices):
            device_id = device['id']           
            device_status = device.get('status', {}).get('dps', {}).get('1', False)
            device_b = device.get('status', {}).get('dps', {}).get('2', False)
            device_w = device.get('status', {}).get('dps', {}).get('3', False)
            # Convert to percentage
            device_b_percentage = max(0, min(100, (device_b - 25) / (255 - 25) * 100))
            device_w_percentage = max(0, min(100, (device_w / 255) * 100))
            button = ttk.Button(self.device_buttons_frame, 
                                text="", 
                                command=lambda device=device: self.toggle_device_selection(device),
                                image=self.lightbulb_off,
                                width=15,
                                style="Unselected.TButton",
                                compound='top')  # Display image on top of text
            button.grid(row=0, column=column_index, padx=(5, 5), sticky="ew")
            
            # Create a button to turn off the single device
            toggle_button = ttk.Button(self.device_buttons_frame, 
                                        style='flat.TButton',
                                          text="Off", 
                                          image=self.img_on,
                                          command=lambda device=device_id: self.turn_off_single_device(device))
            toggle_button.grid(row=1, column=column_index, padx=(5, 5), sticky="ew")

            # Initialize button image based on device status
            button.selected = False  # Track if the button is selected
            self.device_buttons[device_id] = button  # Keep track of the button by device ID
            self.toggle_buttons[device_id] = toggle_button  # Keep track of the button by device ID
            self.set_device_text(device_id, device_b_percentage, device_w_percentage)
            # Update button image based on status
            if device_status:
                button.configure(image=self.lightbulb_on)
               
            else:
                button.configure(image=self.lightbulb_off)
                toggle_button.configure(
                    text="on",
                    command=lambda device=device_id: self.turn_on_single_device(device),
                    image=self.img_off,
                    )

    def toggle_device_selection(self, device):
        """Toggle selection state of the device button."""
        device_id = device['id']
        button = self.device_buttons[device_id]
        
        # Update the button icon based on the device's current status
        device_status = device.get('status', {}).get('dps', {}).get('1', False)
        if device_status:
            button.configure(image=self.lightbulb_on)
        else:
            button.configure(image=self.lightbulb_off)

        if button.selected:
            button.configure(style="Unselected.TButton")
            button.selected = False
            self.selected_devices.remove(device_id)
        else:
            button.configure(style="Selected.TButton")
            button.selected = True
            self.selected_devices.add(device_id)

    def turn_off_single_device(self, device_id):
        """Turn off a single device."""
  
        self.model.control_devices([device_id], action="off")  # Call the model to turn off the device
        button = self.device_buttons[device_id]
        button.configure(image=self.lightbulb_off)  # Update icon to off
        button.selected = False  # Ensure button state reflects selection
        toggle_button = self.toggle_buttons[device_id] 
        toggle_button.configure(text="on", command=lambda device=device_id: self.turn_on_single_device(device), image=self.img_off)

    def turn_on_single_device(self, device_id):
        """Turn off a single device."""
  
        self.model.control_devices([device_id], action="on")  # Call the model to turn off the device
        button = self.device_buttons[device_id]
        button.configure(image=self.lightbulb_on)  # Update icon to off
        button.selected = False  # Ensure button state reflects selection
        toggle_button = self.toggle_buttons[device_id] 
        toggle_button.configure(text="off", command=lambda device=device_id: self.turn_off_single_device(device), image=self.img_on)

    def turn_on_selected_devices(self):
        """Turn on all selected devices."""
        for device_id in self.selected_devices:
            button = self.device_buttons[device_id]
            button.configure(image=self.lightbulb_on)  # Update icon to on
            button.selected = True  # Ensure button state reflects selection
            toggle_button = self.toggle_buttons[device_id] 
            toggle_button.configure(text="off", command=lambda device=device_id: self.turn_off_single_device(device), image=self.img_on)

    def turn_off_selected_devices(self):
        """Turn off all selected devices."""
        for device_id in self.selected_devices:
            button = self.device_buttons[device_id]
            button.configure(image=self.lightbulb_off)  # Update icon to off
            button.selected = False  # Ensure button state reflects selection
            toggle_button = self.toggle_buttons[device_id] 
            toggle_button.configure(text="on", command=lambda device=device_id: self.turn_on_single_device(device), image=self.img_off)


    def toggle_select_all(self):
        """Select or deselect all devices."""
        if len(self.selected_devices) == len(self.device_buttons):
            # All are selected, deselect all
            for device_id in self.device_buttons:
                button = self.device_buttons[device_id]
                button.configure(style="Unselected.TButton")
                button.selected = False
            self.selected_devices.clear()
        else:
            # Not all are selected, select all
            for device_id in self.device_buttons:
                button = self.device_buttons[device_id]
                button.configure(style="Selected.TButton")
                button.selected = True
            self.selected_devices = set(self.device_buttons.keys())

    def get_selected_device_ids(self):
        """Get selected device IDs from the selected devices."""
        return list(self.selected_devices)

    def bind_on_button(self, command):
        self.on_button.config(command=command)
    
    def bind_off_button(self, command):
        self.off_button.config(command=command)
    
    def bind_refresh_button(self, command):
        self.refresh_button.config(command=command)

    def bind_brightness_change(self, command):
        self.brightness_scale.bind("<ButtonRelease-1>", command)  # Bind change on release

    def bind_whiteness_change(self, command):
        self.whiteness_scale.bind("<ButtonRelease-1>", command)  # Bind change on release

    def get_brightness(self):
        return self.brightness_scale.get()
    
    def get_whiteness(self):
        return self.whiteness_scale.get()
    

