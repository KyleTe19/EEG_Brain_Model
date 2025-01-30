from kivymd.app import MDApp
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

BLE_ADDRESS = "70:b8:f6:67:64:a6"
CHAR_UUID = "9b7a6e35-cb8d-473b-9346-15507d362aa3"


class DemoApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loop = None  # Will hold the asyncio event loop
        self.ble_client = None  # BLE client instance

    def build(self):
        # Create screen object
        screen = Screen()

        # Create main layout for buttons and labels
        grid_layout = GridLayout(cols=2, spacing=20, padding=20)

        # Helper function to create button with label
        def create_button_with_label(icon, text, command):
            layout = BoxLayout(orientation="vertical", size_hint=(None, None), size=("100dp", "120dp"))
            button = MDFloatingActionButton(icon=icon, size_hint=(None, None), size=("56dp", "56dp"))
            label = MDLabel(
                text=text,
                halign="center",
                theme_text_color="Secondary",
                size_hint=(1, None),
                height="20dp",
            )
            # Use functools.partial to pass the specific command
            button.bind(on_release=partial(self.on_button_press, command))
            layout.add_widget(button)
            layout.add_widget(label)
            return layout

        # Add buttons with corresponding labels and commands
        grid_layout.add_widget(create_button_with_label("android", "Antero Posterior", "255,0,0"))
        grid_layout.add_widget(create_button_with_label("android", "Bipolar", "\x01"))
        grid_layout.add_widget(create_button_with_label("android", "Transverse", "command3"))
        grid_layout.add_widget(create_button_with_label("android", "Infant", "command4"))
        grid_layout.add_widget(create_button_with_label("android", "Sphenoidal", "command5"))
        grid_layout.add_widget(create_button_with_label("android", "Brain Death", "command6"))
        grid_layout.add_widget(create_button_with_label("android", "Heat Band", "command7"))
        grid_layout.add_widget(create_button_with_label("android", "EEG Electrodes", "command8"))
        grid_layout.add_widget(create_button_with_label("android", "Stop Button", "commandStop"))

        # Add layout to the screen
        screen.add_widget(grid_layout)

        return screen

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
                test_command = command.encode('utf-8')
                print(f"Here is the encoded teste command: {test_command}")
                await self.ble_client.write_gatt_char(CHAR_UUID, command.encode('utf-8'), response=True)
                print(f"Sent command: {command}")
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print("Not connected to ESP32. Cannot send command.")


    def on_button_press(self, command, *args):
        """ Trigger send_command when a button is pressed. """
        print(f"Button pressed, sending command: {command}")

        # Ensure command is a string
        if not isinstance(command, str):
            print(f"Error: Command is not a string: {command}")
            return

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


# Run application
DemoApp().run()

