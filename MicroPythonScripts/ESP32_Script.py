import bluetooth
from bluetooth import BLE, UUID, FLAG_READ, FLAG_WRITE
import struct
from machine import Pin
import neopixel
import time


def advertising_payload(name=None, services=None):
    payload = bytearray()

    # Add device name to the payload
    if name:
        payload += bytearray((len(name) + 1, 0x09)) + name.encode('utf-8')

    # Add service UUIDs to the payload
    if services:
        for uuid in services:
            # Use bytes() to convert UUID to raw bytes
            uuid_bytes = bytes(uuid)

            if len(uuid_bytes) == 16:  # 128-bit UUID
                payload += bytearray((17, 0x07)) + uuid_bytes
            elif len(uuid_bytes) == 2:  # 16-bit UUID
                payload += bytearray((3, 0x03)) + uuid_bytes
            else:
                raise ValueError("Unsupported UUID length")

    return payload


class BLEPeripheral:
    def __init__(self, num_pixels, pin):
        self.ble = BLE()
        self.ble.active(True)
        self.connected = False
        self.num_pixels = num_pixels
        self.np = neopixel.NeoPixel(Pin(pin), num_pixels)
        self.char_handle = None
        self.setup_services()
        self.start_advertising()

    def setup_services(self):
        service_uuid = UUID("3322271e-756a-443d-8a9d-2f90c7a73bf5")
        char_uuid = UUID("9b7a6e35-cb8d-473b-9346-15507d362aa3")
        char = (char_uuid, FLAG_WRITE | FLAG_READ)
        services = [(service_uuid, [char])]
        handles = self.ble.gatts_register_services(services)
        # Check for the structure of handles
        if len(handles) > 0:
            self.service_handle = handles[0][0]  # First element is the service handle
            self.char_handle = 0  # Assign a manual handle for the characteristic
            print(f"Service Handle: {self.service_handle}")
            print(f"Assigned Characteristic Handle: {self.char_handle}")
        else:
            raise ValueError("Service registration failed. Handles not returned.")

    def ble_callback(self, event, data):

        if event == 1:
            print("Device connected")
            self.connected = True
        elif event == 2:
            print("Device disconnected")
            self.connected = False
            self.ble.gap_advertise(100)
        elif event == 3:  # Write request
            handle, value = data
            print(f"Write received: handle={handle}, value={value}")
            print(f"Type of value: {type(value)}")  # Debugging: Print the type of value

            if handle == self.char_handle:
                try:
                    # Convert value to bytes if it's an integer
                    if isinstance(value, int):
                        value = bytes([value])  # Convert integer to bytes
                        print(f"Converted value to bytes: {value}")

                    # Ensure value is bytes or bytearray
                    if isinstance(value, (bytes, bytearray)):
                        print(f"Received data (hex): {value.hex()}")
                        print(f"Received data length: {len(value)}")
                        decoded_value = value.decode('utf-8')
                        print(f"Decoded data: {decoded_value}")
                        self.process_command(decoded_value)
                    else:
                        print(f"Unexpected data type: {type(value)}")
                except Exception as e:
                    print(f"Error processing data: {e}")

    def process_command(self, command):
        print(f"Processing command: {command}")
        try:
            r, g, b = map(int, command.split(","))
            self.set_color(r, g, b)

        except ValueError:
            print("Invalid command format. Expected: 'R,G,B'")

    def set_color(self, r, g, b):
        for i in range(self.num_pixels):
            self.np[i] = (r, g, b)
        time.sleep(2)
        self.np.write()

    def start_advertising(self):
        payload = advertising_payload(name="ESP32_BLE", services=[UUID("3322271e-756a-443d-8a9d-2f90c7a73bf5")])
        self.ble.gap_advertise(100, adv_data=payload)
        self.ble.irq(self.ble_callback)
        print("BLE is ready and advertising")


ble_peripheral = BLEPeripheral(10, 26)
ble_peripheral.set_color(0, 0, 0)
ble_peripheral.start_advertising()


