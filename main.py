# main.py

import tkinter as tk
from model.model import TuyaModel
from view.view import TuyaView
from controller.controller import TuyaController

def main():
    # Initialize Model, View, Controller

    model = TuyaModel()
    controller = TuyaController(model)
    
    controller.root.mainloop()

if __name__ == "__main__":
    main()