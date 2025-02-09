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
        
        # Extract the integer handle values from the nested tuples
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


    def bipolar(self):
        self.set_color(0,0,255,2,14)
        self.set_color(0,0,255,3,23,34)
        print("Bipolar printed")
        
    def process_command(self, command):
        try:
            print("made it into process command function")
            print(f"{command}")
            if command == "bipolar":
                self.bipolar()
            if command == "off":
                self.turn_off()
            if command == "transverse":
                self.transverse()
# #             if command == "infant":
#                 infant()
#             if command == "sphenoidal":
#                 sphenoidal()
#             if command == "brain death":
#                 brain_death()
#             if command == "hatband":
#                 hatband()
#             if command == "eeg electrodes":
#                 eeg_electrodes()   
#             else:
#                 anterio_posterior()


                
        except Exception as commandError:
            print(f"Error in command matching: {commandError}")
            
    def set_color(self, r, g, b, controlVariable, LED_ID = 0, LED_ID2 = 0):
        
        #for individual LEDs
        if controlVariable == 1:
            self.np[LED_ID] = (r, g, b)
        
        # for range from 0
        if controlVariable == 2:
            print(f"made it to control var")

            for i in range(LED_ID):
                self.np[i] = (r, g, b)
            self.np.write()
            print(f"Color set to RGB({r}, {g}, {b})")
        
        # for ranges not from 0
        if controlVariable == 3:
            print(f"made it to c-var 3")
            for i in range(LED_ID, LED_ID2):
                self.np[i] = (r, g, b)
            self.np.write()
        
        
    
    def start_advertising(self):
        name = "ESP32_BLE"
        service_uuid = UUID("3322271e-756a-443d-8a9d-2f90c7a73bf5")
        payload = advertising_payload(name=name, services=[service_uuid])
        self.ble.gap_advertise(100, adv_data=payload)
        self.ble.irq(self.ble_callback)
        print("BLE is ready and advertising")
    
    def transverse():
        self.set_color(255,0,0,1,5)
        self.set_color(255,0,0,1,9)
        self.set_color(255,0,0,3,12,19)
        self.set_color(255,0,0,1,23)
        self.set_color(255,0,0,1,24)
        self.set_color(255,0,0,1,27)
        self.set_color(255,0,0,1,30)
        self.set_color(255,0,0,1,42)
        self.set_color(255,0,0,3,46,50)

# Initialize the peripheral
ble_peripheral = BLEPeripheral(50, 26)

ButtonPin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=SwitchHandler)



