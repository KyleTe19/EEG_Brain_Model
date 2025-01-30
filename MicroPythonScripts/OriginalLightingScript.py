import time
from machine import Pin
import neopixel
import bluetooth
from bluetooth import BLE, UUID
import struct

FLAG_WRITE = 0x0002
FLAG_READ = 0x0008
FLAG_NOTIFY = 0x0010


# Helper function to create advertising payload
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


# Initialize BLE
ble = BLE()
ble.active(False)
ble.active(True)

# Set up the GPIO pin
pin1 = Pin(26, Pin.OUT)  # Pin 26,  10 lights
# pin2 = Pin(25, Pin.OUT)# Pin 25,  5 lights

num_pixels = 15  # Number of LEDs in the chain
# num_pixels2 = 5

# Initialize the Neopixel object
np1 = neopixel.NeoPixel(pin1, num_pixels)


# np2 = neopixel.NeoPixel(pin2, num_pixels2)


# Function to set LED color
def set_color1(r, g, b):
    for i in range(num_pixels):  # Loop through all 10 LEDs
        np1[i] = (r, g, b)  # Set the color of the current LED
        np1.write()  # Send data to all LEDs
        # time.sleep(1)
        # np[i] = (0, 0, 0)
        # un commenting the two above lines will make the leds light up individually and go through the red-green-blue


# def set_color2(r, g, b):
# for i in range(num_pixels2):  # Loop through all 10 LEDs
# np2[i] = (r, g, b)# Set the color of the current LED
# np2.write()  # Send data to all LEDs
# time.sleep(1)
# np[i] = (0, 0, 0)
# un commenting the two above lines will make the leds light up individually and go through the red-green-blue
# Example: Set the LED to red
set_color1(0, 0, 0)

time.sleep(2)

set_color1(255, 0, 0)  # Red

time.sleep(2)

set_color1(0, 0, 0)


# Wait for 1 second

# Example: Set the LED to green
# set_color1(0, 255, 0)
# set_color2(0, 255, 0)
# time.sleep(2)  # Wait for 1 second

# Example: Set the LED to blue
# set_color1(0, 0, 255)  # Blue
# set_color2(0, 0, 255)
# time.sleep(2)


def ble_callback(event, data):
    global CHAR_HANDLE
    print(f"BLE event: {event}, data: {data}")

    if event == 1:  # Central connected
        print("Device connected")
    elif event == 2:  # Central disconnected
        print("Device disconnected")
        ble.gap_advertise(100)  # Restart advertising
    elif event == 3:  # Write request
        handle, value = data
        print(f"Received write request. Handle: {handle}, Value: {value}")
        print(CHAR_HANDLE)

        if handle == CHAR_HANDLE:
            print(f"Received data: {value.decode('utf-8')}")
            process_command(value.decode('utf-8'))


def process_command(command):
    # Process commands to control Neopixels
    print(f"Received command: {command}")
    if command == "command1":
        set_color1(255, 0, 0)  # Set chain 1 to red
    elif command == "command2":
        set_color1(0, 255, 0)  # Set chain 1 to green
    elif command == "command3":
        set_color1(0, 0, 255)  # Set chain 1 to blue
    elif command == "command4":
        set_color1(0, 0, 0)  # Turn off chain 1
    elif command == "commandStop":
        set_color1(0, 0, 0)  # Turn off chain 1 completely
    else:
        print("Unknown command")


# Register BLE service

# Define the service and characteristic UUIDs
SERVICE_UUID = UUID("3322271e-756a-443d-8a9d-2f90c7a73bf5")
CHAR_UUID = UUID("9b7a6e35-cb8d-473b-9346-15507d362aa3")
print(SERVICE_UUID)

# Define the characteristic with read/write permissions
CHAR = (CHAR_UUID, FLAG_READ | FLAG_WRITE)

# Register the service and characteristic
services = [(SERVICE_UUID, [CHAR])]
print("Services Structure: ", services)
handles = ble.gatts_register_services(services)

# Print the handles to check if registration was successful
print(f"Handles after registration: {handles}")

# Check the structure of the handles
if handles:
    print(f"First handle: {handles[0]}")
else:
    print("No handles returned after registration.")

# Check if we have valid handles for the service and characteristic
if len(handles) > 0 and len(handles[0]) > 1:
    service_handle = handles[0][0]  # Handle for the service itself
    CHAR_HANDLE = handles[0][1][0]  # Handle for the first characteristic
    print(f"Service Handle: {service_handle}")
    print(f"Characteristic Handle: {CHAR_HANDLE}")
else:
    CHAR_HANDLE = None
    print("Characteristic handle is None.")

print(f"Characteristic Handle: {CHAR_HANDLE}")

# Start advertising
name = "ESP32_BLE"
ble.gap_advertise(100, adv_data=advertising_payload(name=name, services=[SERVICE_UUID]))

# Set BLE IRQ callback
ble.irq(ble_callback)

print("BLE is ready and advertising...")

# Main loop
while True:
    time.sleep(1)





