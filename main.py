from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock
from kivymd.uix.screen import Screen
from kivymd.uix.menu import MDDropdownMenu
from kivy.properties import BooleanProperty, StringProperty
from android.permissions import request_permissions, Permission, check_permission
from jnius import autoclass, cast

# BLE Constants
BLE_ADDRESS = "70:B8:F6:67:64:A6" # MAC address of specific ESP32 being connected to. Change if switching microcontrollers
CHAR_UUID = "9b7a6e35-cb8d-473b-9346-15507d362aa3"
SERVICE_UUID = "3322271E-756A-443D-8A9D-2F90C7A73BF5"

# Java Classes  
BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
BluetoothGatt = autoclass('android.bluetooth.BluetoothGatt')
Context = autoclass('android.content.Context')
UUID = autoclass('java.util.UUID')
LocationManager = autoclass('android.location.LocationManager')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
MyGattCallback = autoclass('org.montage.ble.MyGattCallback')
BluetoothManager = autoclass('android.bluetooth.BluetoothManager')
BluetoothProfile = autoclass('android.bluetooth.BluetoothProfile')



class MainScreen(Screen):
    is_connected = BooleanProperty(False)
    status_text = StringProperty("Disconnected")

class DemoApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ble_client = None
        self.characteristic = None
        self.current_element = None
        self.menu = None
        self.color_map = {}

        # Command map
        # Structure: "Text Name (found in ui.kv)": "[command sent to ESP32]"
        self.command_map = {
            "Bipolar": "bipolar", 
            "Transverse": "transverse",
            "Hatband": "hatband",
            "Temporal": "temporal",
            "Cz Referential": "cz_ref",
            "Ear Referential": "ear_ref",
            "Large Baby": "large",
            "Small Baby": "small",
            "ECI": "eci"
        }

    def build(self):
        def on_permissions_callback(permissions, grants):

            print("Permissions callback executed")
            for i, grant in enumerate(grants):
                if not grant:
                    print(f"Permission denied: {permissions[i]}")

            if all(grants):
                print("All permissions granted")
                if self.is_location_enabled():
                    Clock.schedule_once(lambda dt: self.connect_to_device(), 1)
                else:
                    print("Please enable location services manually.")
                    self.get_main_screen().status_text = "Enable Location Services"
            else:
                print("Some permissions were denied")
                self.get_main_screen().status_text = "Permission Denied"

        request_permissions([
            Permission.ACCESS_BACKGROUND_LOCATION,
            Permission.ACCESS_FINE_LOCATION,
            Permission.BLUETOOTH,
            Permission.BLUETOOTH_ADMIN,
        ], on_permissions_callback)

        return Builder.load_file("ui.kv")

    def get_main_screen(self):
        return self.root.get_screen("main")

    def is_location_enabled(self):
        try:
            context = self.get_context()
            location_manager = cast('android.location.LocationManager',
                                    context.getSystemService(Context.LOCATION_SERVICE))
            return (location_manager.isProviderEnabled(LocationManager.GPS_PROVIDER) or
                    location_manager.isProviderEnabled(LocationManager.NETWORK_PROVIDER))
        except Exception as e:
            print(f"Location check failed: {e}")
            return False

    def check_permissions(self):
        required = [
            Permission.ACCESS_FINE_LOCATION,
            Permission.BLUETOOTH,
            Permission.BLUETOOTH_ADMIN,
            Permission.ACCESS_BACKGROUND_LOCATION
        ]
        return all(check_permission(p) for p in required)

    # update -- checks connectivity status 
    def check_connection(self, dt):
        try:
            context = self.get_context()
            manager = cast('android.bluetooth.BluetoothManager',
                        context.getSystemService(Context.BLUETOOTH_SERVICE))
            device = self.ble_client.getDevice()
            state = manager.getConnectionState(device, BluetoothProfile.GATT)

            if state == BluetoothProfile.STATE_CONNECTED:
                print("Device connected.")
                screen = self.get_main_screen()
                screen.status_text = "Connected"
                screen.is_connected = True

                if not hasattr(self, '_services_discovered'):
                    self.ble_client.discoverServices()
                    self._services_discovered = True
                    Clock.schedule_interval(self.poll_for_service, 1)

                # Stop polling for initial connection
                Clock.unschedule(self.check_connection)

                # Start monitoring connection health
                Clock.schedule_interval(self.monitor_connection, 5)

        except Exception as e:
            print(f"Connection check failed: {e}")


    def monitor_connection(self, dt):
        try:
            context = self.get_context()
            manager = cast('android.bluetooth.BluetoothManager',
                        context.getSystemService(Context.BLUETOOTH_SERVICE))
            device = self.ble_client.getDevice()
            state = manager.getConnectionState(device, BluetoothProfile.GATT)

            if state != BluetoothProfile.STATE_CONNECTED:
                print("Device disconnected!")

                screen = self.get_main_screen()
                screen.status_text = "Disconnected"
                screen.is_connected = False

                # Stop monitoring connection
                Clock.unschedule(self.monitor_connection)

                # Clear service discovery flag
                if hasattr(self, '_services_discovered'):
                    del self._services_discovered

                # Try reconnecting after delay
                Clock.schedule_once(lambda dt: self.connect_to_device(), 2)

        except Exception as e:
            print(f"Monitor connection check failed: {e}")

    # update -- checks status - looking for service UUID
    def poll_for_service(self, dt):
        try:
            service = self.ble_client.getService(UUID.fromString(SERVICE_UUID))
            if service:
                print("Service found!")
                self.characteristic = service.getCharacteristic(UUID.fromString(CHAR_UUID))
                
                if self.characteristic:
                    print("Characteristic set!")
                    screen = self.get_main_screen()
                    screen.status_text = "Ready"
                    screen.is_connected = True
                    Clock.unschedule(self.poll_for_service)
                else:
                    print("Characteristic not found - still polling...")
            else:
                print("Service not found - still polling...")
        except Exception as e:
            print(f"Service polling error: {e}")
            # Continue polling unless we've tried too many times
            if hasattr(self, '_poll_count'):
                self._poll_count += 1
                if self._poll_count > 10:  # Stop after 10 attempts
                    Clock.unschedule(self.poll_for_service)
                    self.get_main_screen().status_text = "Discovery Failed"
            else:
                self._poll_count = 1


    def connect_to_device(self):
        screen = self.get_main_screen()

        if not self.check_permissions():
            screen.status_text = "Missing Permissions"
            return

        if not self.is_location_enabled():
            screen.status_text = "Location Off"
            return

        try:
            adapter = BluetoothAdapter.getDefaultAdapter()
            if not adapter.isEnabled():
                screen.status_text = "Bluetooth Off"
                return

            device = adapter.getRemoteDevice(BLE_ADDRESS)

            # 🚨 Disconnect previous GATT client if it exists
            if self.ble_client is not None:
                print("Closing old GATT connection before reconnecting...")
                try:
                    self.ble_client.disconnect()
                    self.ble_client.close()
                except Exception as e:
                    print(f"Error closing GATT: {e}")
                self.ble_client = None  # Clear the reference

            self.gatt_callback = MyGattCallback()
            self.ble_client = device.connectGatt(
                self.get_context(),
                False,
                self.gatt_callback
            )

            screen.status_text = "Connecting..."
            Clock.schedule_interval(self.check_connection, 1)

        except Exception as e:
            print(f"Connection failed: {e}")
            screen.status_text = "Connection Failed"


    # update -- checks for UUID characteristic -- mostly here for debugging - i don't think this is being called amymore
    def get_characteristic(self, dt):
        try:
            service = self.ble_client.getService(UUID.fromString(SERVICE_UUID))
            if service is not None:
                characteristic = service.getCharacteristic(UUID.fromString(CHAR_UUID))
                if characteristic is not None:
                    self.characteristic = characteristic
                    print("Characteristic set!")
                    self.get_main_screen().status_text = "Ready"
                else:
                    print("Characteristic not found.")
                    self.get_main_screen().status_text = "No Characteristic"
            else:
                print("Service not found.")
                self.get_main_screen().status_text = "No Service"
        except Exception as e:
            print(f"Error getting characteristic: {e}")
            self.get_main_screen().status_text = "Service Discovery Failed"


    # update -- i don't think this is being called either 
    def on_connection_state_change(self, gatt, status, new_state):
        screen = self.get_main_screen()
        if new_state == 2:
            screen.is_connected = True
            screen.status_text = "Connected"
            gatt.discoverServices()
        else:
            screen.is_connected = False
            screen.status_text = "Not Connected"

    def on_services_discovered(self, gatt, status):
        screen = self.get_main_screen()
        if status == 0:
            service = gatt.getService(UUID.fromString(SERVICE_UUID))
            if service:
                self.characteristic = service.getCharacteristic(UUID.fromString(CHAR_UUID))
                if self.characteristic:
                    screen.status_text = "Ready"
                else:
                    screen.status_text = "No Characteristic"
            else:
                screen.status_text = "No Service"
        else:
            screen.status_text = "Service Discovery Failed"

    def on_toggle_press(self, element_card):
        card_text = element_card.text.strip()
        command = self.command_map.get(card_text)
        if command is None:
            print(f"No command mapped for {card_text}")
            return

        if element_card.active:
            # Toggled Off
            print(f"OFF: {card_text}")
            element_card.active = False
            if self.current_element == element_card:
                self.current_element = None
            self.send_command("off", element_card)
        else:
            # Toggled on
            print(f"ON: {card_text}\nCommand: {command}")
            if self.current_element and self.current_element != element_card:
                self.current_element.active = False
            element_card.active = True
            self.current_element = element_card
            self.send_command(command, element_card)

    def send_command(self, command, element_card):
        screen = self.get_main_screen()
        if not screen.is_connected:
            print("Not connected - command not sent")
            return

        selected_color = self.color_map.get(element_card.text, "blue")
        full_command = f"{command} {selected_color}"

        try:
            self.characteristic.setValue(full_command.encode('utf-8'))
            self.ble_client.writeCharacteristic(self.characteristic)
            print(f"Sent: {full_command}")
        except Exception as e:
            print(f"Failed to send command: {e}")

    # show color selection dropdown menu
    def show_color_menu(self, instance, card):
        colors = ["red", "blue", "green", "yellow", "white", "purple", "orange"]
        menu_items = [{
            "viewclass": "OneLineListItem",
            "text": color,
            "on_release": lambda x=color: self.assign_color_to_card(card, x),
        } for color in colors]

        self.menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    # assign selected color to the button 
    def assign_color_to_card(self, card, color):
        self.color_map[card.text] = color
        print(f"Assigned color {color} to {card.text}")
        if card.active:
            command = self.command_map.get(card.text.strip())
            if command:
                self.send_command(command, card)
        self.menu.dismiss()

    def get_context(self):
        return PythonActivity.mActivity.getApplicationContext()

    def on_stop(self):
        if hasattr(self, 'ble_client') and self.ble_client:
            self.ble_client.disconnect()

if __name__ == '__main__':
    DemoApp().run()