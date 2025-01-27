from kivymd.app import MDApp
from kivy.lang import Builder 
from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.screen import Screen
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from bleak import BleakClient
from kivy.clock import Clock
import asyncio
from threading import Thread
from functools import partial
from kivy.uix.button import Button

BLE_ADDRESS = "70:b8:f6:67:64:a6"
CHAR_UUID = "9b7a6e35-cb8d-473b-9346-15507d362aa3"

class MainScreen(Screen):
    pass

class DemoApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loop = None  # Will hold the asyncio event loop
        self.ble_client = None  # BLE client instance
        self.active_button = None

    def build(self):
        # Load the KV file
        return Builder.load_file("ui.kv")
    
    def on_toggle_press(self, button):
        """Toggle button state and update colors"""
        label = button.ids.label 

        if self.active_button == button:
            # if the same button is pressed again, untoggle it
            button.md_bg_color = (46/255, 46/255, 46/255, 1)  # reset to default color
            label.theme_text_color = "Custom"
            label.text_color = (243/255, 243/255, 243/255, 1) # reset text color
            self.active_button = None
            print(f"'{label.text}' toggled OFF")
        else:
            if self.active_button:
                self.active_button.md_bg_color = (46/255, 46/255, 46/255, 1)  # reset previous button
                self.active_button.ids.label.theme_text_color = "Custom"
                self.active_button.ids.label.text_color = (243/255, 243/255, 243/255, 1)  # reset text color to white

            button.md_bg_color = (243/255, 243/255, 243/255, 1)  # white when toggled ON  
            label.theme_text_color = "Custom"
            label.text_color = (46/255, 46/255, 46/255, 1)  # black text when toggled ON
            self.active_button = button
            print(f"'{label.text} toggled ON")

    async def connect_to_device(self):
        """ Establish a persistent BLE connection. """
        try:
            self.ble_client = BleakClient(BLE_ADDRESS)
            await self.ble_client.connect()
            if self.ble_client.is_connected:
                print(f"Connected to {BLE_ADDRESS}")
            else:
                print("Failed to connect to ESP32")
        except Exception as e:
            print(f"An error occurred during connection: {e}")

    async def disconnect_from_device(self):
        """ Disconnect the BLE client. """
        if self.ble_client and self.ble_client.is_connected:
            await self.ble_client.disconnect()
            print(f"Disconnected from {BLE_ADDRESS}")

    async def send_command(self, command):
        """ Send a command to the ESP32 over BLE. """
        if self.ble_client and self.ble_client.is_connected:
            try:
                await self.ble_client.write_gatt_char(CHAR_UUID, command.encode('utf-8'))
                print(f"Sent command: {command}")
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print("Not connected to ESP32. Cannot send command.")

    def on_button_press(self, command, *args):
        """ Trigger send_command when a button is pressed. """
        print(f"Button pressed, sending command: {command}")

        # Schedule the async function in the running event loop
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.send_command(command), self.loop)

    def start_event_loop(self):
        """ Start the asyncio event loop in a separate thread. """
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def on_start(self):
        """ Start the event loop and connect to the BLE device when the app starts. """
        # Start the asyncio event loop in a separate thread
        Thread(target=self.start_event_loop, daemon=True).start()

        # Wait for the event loop to initialize and then connect
        def connect_when_ready(dt):
            if self.loop:  # Ensure the loop is initialized
                asyncio.run_coroutine_threadsafe(self.connect_to_device(), self.loop)

        Clock.schedule_once(connect_when_ready, 0.5)  # Schedule with a slight delay

    def on_stop(self):
        """ Disconnect from the BLE device when the app stops. """
        if self.loop:  # Ensure the loop is initialized
            asyncio.run_coroutine_threadsafe(self.disconnect_from_device(), self.loop)

if __name__ == '__main__':
    # Run application
    DemoApp().run()
