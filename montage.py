# use to individually address lights


from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock
import asyncio
from threading import Thread
from bleak import BleakClient
from kivymd.uix.screen import Screen
from threading import Thread

BLE_ADDRESS = "70:b8:f6:67:64:a6"
CHAR_UUID = "9b7a6e35-cb8d-473b-9346-15507d362aa3"

class MainScreen(Screen):
    pass

class DemoApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loop = None              # asyncio event loop
        self.ble_client = None        # BLE client instance
        self.current_element = None   # Track the currently active ElementCard

        # Map each card’s text to its corresponding command
        self.command_map = {
            "Antero-Posterior": "antero-posterior",
            "Bipolar": "bipolar",
            "Transverse": "transverse",
            "Infant": "infant",
            "Sphenoidal": "sphenoidal",
            "Brain Death": "brain death",
            "Hatband": "hatband",
            "EEG Electrodes": "eeg electrodes",
        }

    # KV file for the UI
    def build(self):
        return Builder.load_file("ui.kv")

    # Establish a persistent BLE connection
    async def connect_to_device(self):
        try:
            self.ble_client = BleakClient(BLE_ADDRESS)
            await self.ble_client.connect()
            if self.ble_client.is_connected:
                print(f"Connected to {BLE_ADDRESS}")
            else:
                print("Failed to connect to ESP32")
        except Exception as e:
            print(f"An error occurred during connection: {e}")

    # Disconnect the BLE client
    async def disconnect_from_device(self):
        if self.ble_client and self.ble_client.is_connected:
            await self.ble_client.disconnect()
            print(f"Disconnected from {BLE_ADDRESS}")

    # Send a command (as string) over BLE to ESP32
    async def send_command(self, command):
        if self.ble_client and self.ble_client.is_connected:
            try:
                if isinstance(command, str):
                    # handle different command formats
                    if command == "\x01":
                        formatted_command = bytes([1])
                    else:
                        formatted_command = command.strip().encode()
                    print(f"Sending command: {formatted_command}")
                    await self.ble_client.write_gatt_char(CHAR_UUID, formatted_command)
                    print("Command sent successfully")
            except Exception as e:
                print(f"Error sending command: {e}")
        else:
            print("Not connected to ESP32. Cannot send command")

    # Trigger send_command when button is pressed
    def on_button_press(self, command, *args):
        if not isinstance(command, str):
            print(f"Error: Command is not a string: {command}")
            return
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.send_command(command), self.loop)

   # Toggle card and send command when ElementCard is pressed 
    def on_toggle_press(self, element_card):
        card_text = element_card.text.strip()
        command = self.command_map.get(card_text, None)
        if command is None:
            print(f"No command mapped for {card_text}")
            return

        if element_card.active:
            # Toggled off
            print(f"OFF: {card_text}")
            element_card.active = False
            if self.current_element == element_card:
                self.current_element = None
            self.on_button_press("off")
        else:
            # Toggled on
            print(f"ON: {card_text}\nCommand: {command}")
            if self.current_element and self.current_element != element_card:
                self.current_element.active = False
            element_card.active = True
            self.current_element = element_card
            self.on_button_press(command)

    # Start the asyncio event loop in a separate thread
    def start_event_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    # Start the event loop and connect/scan for devices when the app starts
    def on_start(self):     
        Thread(target=self.start_event_loop, daemon=True).start()

        def connect_and_scan(dt):
            if self.loop:
                asyncio.run_coroutine_threadsafe(self.connect_to_device(), self.loop)
        Clock.schedule_once(connect_and_scan, 1.5)

    # Disconnect from the BLE device when the app stops
    def on_stop(self):
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.disconnect_from_device(), self.loop)

DemoApp().run()