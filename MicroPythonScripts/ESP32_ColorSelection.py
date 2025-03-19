# CURRENT VERSION
# uses app dropdown for color selection

import bluetooth
from bluetooth import BLE, UUID, FLAG_READ, FLAG_WRITE
import struct
from machine import Pin
import neopixel
import time


ButtonPin = Pin(36, Pin.IN, Pin.PULL_DOWN)
PowerRelayControl = Pin(12, Pin.OUT)

    

def SwitchHandler(pin):
    if pin.value() == 1:
        PowerRelayControl.on()
        print(f"Button Value = {pin.value()}")
        print(f"Power Relay Value = {PowerRelayControl.value()}")
    else:
        ble_peripheral.turn_off()
        time.sleep(3)
        PowerRelayControl.off()
        print(f"Button Value On Depress = {pin.value()}")
        print(f"Power Relay Value On Depress = {PowerRelayControl.value()}")
        
    

def advertising_payload(name=None, services=None):
    payload = bytearray()
    if name:
        payload += bytearray((len(name) + 1, 0x09)) + name.encode('utf-8')
    if services:
        for uuid in services:
            uuid_bytes = bytes(uuid)
            if len(uuid_bytes) == 16:
                payload += bytearray((17, 0x07)) + uuid_bytes
            elif len(uuid_bytes) == 2:
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
        self.service_handle = None
        self.char_handle = None
        self.setup_services()
        self.start_advertising()

    def setup_services(self):
        # Define UUIDs
        service_uuid = UUID("3322271e-756a-443d-8a9d-2f90c7a73bf5")
        char_uuid = UUID("9b7a6e35-cb8d-473b-9346-15507d362aa3")
        
        # Define characteristic
        char = (char_uuid, FLAG_WRITE | FLAG_READ)
        services = [(service_uuid, [char])]
        
        # Register services
        handles = self.ble.gatts_register_services(services)
        print(f"Handles received: {handles}")  # Debug print
        
        # Extract integer handle values from the nested tuples
        if handles and len(handles) > 0 and len(handles[0]) > 0:
            self.service_handle = handles[0][0]  # Extract the integer
            self.char_handle = 16  # We know this is the characteristic handle from debug output
            print(f"Service Handle: {self.service_handle}")
            print(f"Char Handle: {self.char_handle}")
        else:
            raise ValueError("Failed to register services")
        
    def turn_off(self):
        for i in range(self.num_pixels):
            self.np[i] = (0,0,0)
        self.np.write()
        print ("Color set to zero")
        

    def ble_callback(self, event, data):
        if event == 1:  # Connect
            print("Device connected")
            self.connected = True
            
        elif event == 2:  # Disconnect
            print("Device disconnected")
            self.connected = False
            self.start_advertising()
            
        elif event == 3:  # Write
            handle, value = data
           

            print(f"Write event - handle: {handle}, value: {value}")
            # Read the value using the characteristic handle
            buffer = self.ble.gatts_read(self.char_handle)
            command = buffer.decode()
            print(f"Raw buffer received: {buffer}")
            print(f"Decoded command: {command}")
            self.process_command(command)
#                         else:
#                             # Handle as single byte
#                             byte_value = buffer[0]
#                             print(f"Received byte value: {byte_value}")
#                             if byte_value == 1:
#                                 #self.set_color(255, 0, 0)
#                                 print(f"String Decoding Failed")
#                                 
#                     except UnicodeError:
#                         # Handle as raw bytes if decode fails
#                         byte_value = buffer[0]
#                         print(f"Received raw byte: {byte_value}")
#                         if byte_value == 1:
#                           #  self.set_color(255, 0, 0)
#                           print(f"Unicode Error: Byte Value = 1")
#             except Exception as e:
#                 print(f"Error in callback: {e}")
#


    def bipolar(self, r, g, b):
        self.set_color(r, g, b, 2, 14)
        self.set_color(r, g, b, 3, 20, 34)
        self.set_color(r, g, b, 3, 37, 44)
        self.np.write()
        print("Bipolar montage set to color:", (r, g, b))

        
    def transverse(self, r, g, b):
        self.set_color(r, g, b, 2, 4)
        self.set_color(r, g, b, 3, 10, 19)
        self.set_color(r, g, b, 3, 34, 38)
        self.set_color(r, g, b, 3, 45, 50)
        self.np.write()
        print("Transverse montage set to color:", (r, g, b))

    def infant(self, r, g, b):
        self.set_color(r, g, b, 2, 50)
        self.np.write()
        print("Infant montage set to color:", (r, g, b))

    def sphenoidal(self, r, g, b):
        self.set_color(r, g, b, 2, 50)
        self.np.write()
        print("Sphenoidal montage set to color:", (r, g, b))
    
    def antero_posterior(self, r, g, b):
        self.set_color(r, g, b, 2, 50)
        self.np.write()
        print("Antero-Posterior set to color:", (r, g, b))

    def hatband(self, r, g, b):
        self.set_color(r, g, b, 2, 50)
        self.np.write()
        print("Hatband montage set to color:", (r, g, b))
        
    def brain_death(self, r, g, b):
        self.set_color(r, g, b, 2, 50)
        self.np.write()
        print("Brain Death montage set to color:" (r, g, b))
    
    def electrodes(self, r, g, b):
        self.set_color(r, g, b, 2, 50)
        self.np.write()
        print("Electrode montage set to color:" (r, g, b))

        
    def process_command(self, command):
        try:
            print("Received command:", command)

            # Split the command into parts
            parts = command.split()  # Expects "montage color"
            if len(parts) < 2:
                print("Invalid command format. Expected: 'montage color'")
                return
            
            montage_name = parts[0].lower()  # First part is the montage name
            color_name = parts[1].lower()    # Second part is the color

            # Define RGB color mappings
            color_map = {
                "red": (255, 0, 0),
                "blue": (0, 0, 255),
                "green": (0, 255, 0),
                "yellow": (255, 255, 0),
                "white": (255, 255, 255),
                "purple": (128, 0, 128),
                "orange": (255, 165, 0),
            }

            # Check if the color exists
            if color_name not in color_map:
                print(f"Unknown color: {color_name}")
                return
            
            r, g, b = color_map[color_name]  # Get RGB values

            # Call the appropriate function with the selected color
            if montage_name == "bipolar":
                self.bipolar(r, g, b)
            elif montage_name == "transverse":
                self.transverse(r, g, b)
            elif montage_name == "infant":
                self.infant(r, g, b)
            elif montage_name == "sphenoidal":
                self.sphenoidal(r, g, b)
            elif montage_name == "hatband":
                self.hatband(r, g, b)
            elif montage_name == "anteroposterior":
                self.antero_posterior(r, g, b)
            elif montage_name == "brain_death":
                self.brain_death(r, g, b)
            elif montage_name == "electrodes":
                self.electrodes(r, g, b)
            elif montage_name == "off":
                self.turn_off()
            else:
                print(f"Unknown montage: {montage_name}")

        except Exception as commandError:
            print(f"Error in command processing: {commandError}")

            
    def set_color(self, r, g, b, controlVariable, LED_ID = 0, LED_ID2 = 0):
        print(f"Setting LED {LED_ID} to RGB({r}, {g}, {b}) with controlVariable {controlVariable}")

        #for individual LEDs
        if controlVariable == 1:
            self.np[LED_ID] = (r, g, b)
            
        # for range from 0
        if controlVariable == 2:
            print(f"made it to control var")

            for i in range(LED_ID):
                self.np[i] = (r, g, b)
            print(f"Color set to RGB({r}, {g}, {b})")
        
        # for ranges not from 0
        if controlVariable == 3:
            print(f"made it to c-var 3")
            for i in range(LED_ID, LED_ID2):
                self.np[i] = (r, g, b)
        
    
    def start_advertising(self):
        name = "ESP32_BLE"
        service_uuid = UUID("3322271e-756a-443d-8a9d-2f90c7a73bf5")
        payload = advertising_payload(name=name, services=[service_uuid])
        self.ble.gap_advertise(100, adv_data=payload)
        self.ble.irq(self.ble_callback)
        print("BLE is ready and advertising")
    


# Initialize the peripheral
ble_peripheral = BLEPeripheral(50, 26)

ButtonPin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=SwitchHandler)






