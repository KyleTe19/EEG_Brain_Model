import bluetooth
from bluetooth import BLE, UUID, FLAG_READ, FLAG_WRITE
import struct
from machine import Pin
import neopixel
import time

#D0:   GPIO21 pin0
#D1:   GPIO22 pin1
#D2:   GPIO14 pin2
#D3:   GPIO32 pin3
#D4:   GPIO15 pin4
#D5:   GPIO33 pin5

ButtonPin = Pin(27, Pin.IN, Pin.PULL_DOWN)
PowerRelayControl = Pin(12, Pin.OUT)



def SwitchHandler(pin):
    if pin.value() == 1:
        PowerRelayControl.on()
        print(f"Button Value = {pin.value()}")
        print(f"Power Relay Value = {PowerRelayControl.value()}")
    else:
        ble_peripheral.turn_off()
        time.sleep(2)
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
    def __init__(self, num_pixels, pin0, pin1, pin2, pin3, pin4, pin5):
        self.ble = BLE()
        self.ble.active(True)
        self.connected = False
        self.num_pixels = num_pixels
        self.np0 = neopixel.NeoPixel(Pin(pin0), num_pixels)
        self.np1 = neopixel.NeoPixel(Pin(pin1), num_pixels)
        self.np2 = neopixel.NeoPixel(Pin(pin2), num_pixels)
        self.np3 = neopixel.NeoPixel(Pin(pin3), num_pixels)
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
            self.np0[i] = (0,0,0)
            self.np1[i] = (0,0,0)
            self.np2[i] = (0,0,0)
            self.np3[i] = (0,0,0)
        self.np0.write()
        self.np1.write()
        self.np2.write()
        self.np3.write()

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


    def bipolar(self, r, g, b):


        #np0 = 192  total LEDs
        #np1 = 69  total  LEDs
        #np2 = 79  total  LEDs
        #np3 = 159  total LEDs
        self.set_color(r, g, b, 1, self.np3, 48)
        self.set_color(r, g, b, 1, self.np3, 31)
        self.set_color(r, g, b, 1, self.np3, 11)
        self.set_color(r, g, b, 1, self.np3, 70)
        self.set_color(r, g, b, 1, self.np3, 63)
        self.set_color(r, g, b, 1, self.np3, 76)
        self.set_color(r, g, b, 1, self.np3, 40)
        self.set_color(r, g, b, 3, self.np3, 84, 112) # right side of bipolar
        self.set_color(r, g, b, 3, self.np3, 116, 141)# left side of bipolar
        self.set_color(r, g, b, 3, self.np3, 145, 159)
        self.set_color(r, g, b, 2, self.np0, 62) # bottom of the brain


        self.np0.write()
        self.np2.write()
        self.np3.write()
        print("Bipolar montage set to color:", (r, g, b))


    def transverse(self, r, g, b):

        # bottom
        self.set_color(r, g, b, 3, self.np0, 176, 186)
        self.set_color(r, g, b, 3, self.np0, 111, 116)
        self.set_color(r, g, b, 3, self.np0, 116, 120)
        self.set_color(r, g, b, 3, self.np0, 120, 135)
        self.set_color(r, g, b, 3, self.np0, 138, 143)
        self.set_color(r, g, b, 1, self.np0, 80)
        self.set_color(r, g, b, 3, self.np0, 82, 89)
        self.set_color(r, g, b, 3, self.np0, 150, 156)
        self.set_color(r, g, b, 1, self.np0, 159)
        self.set_color(r, g, b, 1, self.np0, 106)
        self.set_color(r, g, b, 1, self.np0, 12)
        self.set_color(r, g, b, 1, self.np0, 6)
        self.set_color(r, g, b, 1, self.np0, 19)
        self.set_color(r, g, b, 1, self.np0, 0)
        self.set_color(r, g, b, 1, self.np0, 67)
        self.set_color(r, g, b, 1, self.np0, 43)
        self.set_color(r, g, b, 1, self.np0, 35)
        self.set_color(r, g, b, 1, self.np0, 48)
        self.set_color(r, g, b, 3, self.np0, 160, 167)


        # top
        self.set_color(r, g, b, 2, self.np3, 83)
        self.set_color(r, g, b, 1, self.np3, 112)
        self.set_color(r, g, b, 1, self.np3, 116)
        self.np0.write()
        self.np3.write()
        print("Transverse montage set to color:", (r, g, b))


        self.np0.write()
        self.np2.write()
        self.np3.write()
        self.np1.write()
        print("Transverse montage set to color:", (r, g, b))

    def hatband(self, r, g, b):
        self.set_color(r, g, b, 1, self.np3, 48)
        self.set_color(r, g, b, 1, self.np3, 31)
        self.set_color(r, g, b, 1, self.np3, 63)
        self.set_color(r, g, b, 1, self.np3, 76)
        self.set_color(r, g, b, 3, self.np3, 84, 145) #
        self.set_color(r, g, b, 2, self.np0, 55) # bottom of the brain


        self.np2.write()
        self.np3.write()
        self.np0.write()
        self.np1.write()
        print("Hatband montage set to color:", (r, g, b))

    def temporal(self, r, g, b):

        # top of temporal pole
        self.set_color(r, g, b, 1, self.np3, 48)
        self.set_color(r, g, b, 1, self.np3, 31)
        self.set_color(r, g, b, 1, self.np3, 63)
        self.set_color(r, g, b, 1, self.np3, 76)
        self.set_color(r, g, b, 3, self.np3, 92, 112)
        self.set_color(r, g, b, 3, self.np3, 116, 134)

        # bottom of temporal pole
        self.set_color(r, g, b, 3, self.np0, 89, 107)
        self.set_color(r, g, b, 3, self.np0, 70, 82)
        self.set_color(r, g, b, 3, self.np0, 62, 70)
        self.set_color(r, g, b, 3, self.np0, 107, 111)
        self.set_color(r, g, b, 2, self.np0, 7)
        self.set_color(r, g, b, 3, self.np0, 13, 26)
        self.set_color(r, g, b, 3, self.np0, 143, 147)
        self.set_color(r, g, b, 3, self.np0, 26, 43)
        self.set_color(r, g, b, 3, self.np0, 156, 159)
        self.set_color(r, g, b, 1, self.np0, 176)
        self.set_color(r, g, b, 3, self.np0, 48, 55)

        self.np2.write()
        self.np3.write()
        self.np0.write()
        self.np1.write()
        print("Temporal Pole montage set to color:", (r, g, b))

    def cz_ref(self, r, g, b):
        #top of brain
        self.set_color(r, g, b, 2, self.np2, 81)
        self.set_color(r, g, b, 3, self.np3, 23, 56)
        self.set_color(r, g, b, 1, self.np1, 10)
        self.set_color(r, g, b, 1, self.np1, 15)
        self.set_color(r, g, b, 1, self.np1, 5)
        self.set_color(r, g, b, 1, self.np3, 124)
        self.set_color(r, g, b, 1, self.np3, 129)
        self.set_color(r, g, b, 3, self.np3, 77, 83)
        self.set_color(r, g, b, 3, self.np1, 41, 69)
        self.set_color(r, g, b, 1, self.np3, 115)
        self.set_color(r, g, b, 1, self.np3, 111)
        self.set_color(r, g, b, 1, self.np1, 39)
        self.set_color(r, g, b, 1, self.np3, 93)
        self.set_color(r, g, b, 1, self.np1, 30)
        self.set_color(r, g, b, 1, self.np3, 102)
        self.set_color(r, g, b, 1, self.np1, 25)



        #bottom of brain

        self.set_color(r, g, b, 1, self.np0, 192)
        self.set_color(r, g, b, 1, self.np0, 10)
        self.set_color(r, g, b, 1, self.np0, 12)
        self.set_color(r, g, b, 1, self.np0, 19)

        self.set_color(r, g, b, 1, self.np0, 6)
        self.set_color(r, g, b, 1, self.np0, 106)
        self.set_color(r, g, b, 1, self.np0, 189)
        self.set_color(r, g, b, 1, self.np0, 16)
        self.set_color(r, g, b, 1, self.np0, 81)

        self.set_color(r, g, b, 1, self.np0, 37)
        self.set_color(r, g, b, 1, self.np0, 35)
        self.set_color(r, g, b, 1, self.np0, 43)
        self.set_color(r, g, b, 1, self.np0, 48)
        self.set_color(r, g, b, 1, self.np0, 137)
        self.set_color(r, g, b, 1, self.np0, 89)



        self.np0.write()
        self.np1.write()
        self.np2.write()
        self.np3.write()
        print("Cz Referential montage set to color:", (r, g, b))

    def ear_ref(self, r, g, b):
        self.set_color(r, g, b, 2, 50)



        #top
        self.set_color(r, g, b, 3, self.np3, 0, 7)   # f3
        self.set_color(r, g, b, 3, self.np3, 12, 40) # fz
        self.set_color(r, g, b, 3, self.np3, 50, 55) # c3
        self.set_color(r, g, b, 3, self.np3, 56, 70) # pz
        self.set_color(r, g, b, 3, self.np3, 77, 82) # p3
        self.set_color(r, g, b, 1, self.np1, 26)

        #bottom
        self.set_color(r, g, b, 3, self.np0, 62, 66)
        self.set_color(r, g, b, 1, self.np0, 6)


        self.set_color(r, g, b, 3, self.np0, 111, 116)
        self.set_color(r, g, b, 1, self.np0, 13)


        self.set_color(r, g, b, 1, self.np0, 190)
        self.set_color(r, g, b, 1, self.np0, 19)


        self.set_color(r, g, b, 3, self.np0, 150, 158)


        self.set_color(r, g, b, 3, self.np0, 138, 143)
        self.set_color(r, g, b, 3, self.np0, 157, 160)

        self.set_color(r, g, b, 1, self.np0, 36)
        self.set_color(r, g, b, 1, self.np0, 136)
        self.set_color(r, g, b, 1, self.np0, 89)
        self.set_color(r, g, b, 1, self.np0, 67)
        self.set_color(r, g, b, 1, self.np0, 49)
        self.set_color(r, g, b, 1, self.np0, 43)
        self.set_color(r, g, b, 3, self.np0, 82, 89)
        self.set_color(r, g, b, 1, self.np0, 80)

        self.set_color(r, g, b, 3, self.np0, 116, 135)
        self.set_color(r, g, b, 3, self.np0, 160, 186)


        self.np0.write()
        self.np1.write()
        self.np2.write()
        self.np3.write()
        print("Ear Referential montage set to color:", (r, g, b))

    def large(self, r, g, b):
        self.set_color(r, g, b, 1, self.np3, 48)
        self.set_color(r, g, b, 1, self.np3, 31)
        self.set_color(r, g, b, 1, self.np3, 11)
        self.set_color(r, g, b, 1, self.np3, 70)
        self.set_color(r, g, b, 1, self.np3, 63)
        self.set_color(r, g, b, 1, self.np3, 76)
        self.set_color(r, g, b, 1, self.np3, 40)
        self.set_color(r, g, b, 3, self.np3, 84, 112) # right side of bipolar
        self.set_color(r, g, b, 3, self.np3, 116, 141)# left side of bipolar
        self.set_color(r, g, b, 3, self.np3, 145, 159)
        self.set_color(r, g, b, 2, self.np0, 55) # bottom of the brain


        self.np0.write()
        self.np2.write()
        self.np3.write()
        print("Large baby montage set to color:" (r, g, b))

    def small(self, r, g, b):

        # TOP

        self.set_color(r, g, b, 3, self.np3, 23, 56)
        self.set_color(r, g, b, 3, self.np3, 84, 112) # right side of top
        self.set_color(r, g, b, 3, self.np3, 116, 141) # left side of top
        self.set_color(r, g, b, 3, self.np1, 41, 69)


        # BOTTOM

        #right side connections from tp9 to top

        self.set_color(r, g, b, 3, self.np0, 0, 27)
        self.set_color(r, g, b, 1, self.np0, 106)
        self.set_color(r, g, b, 1, self.np0, 12)
        self.set_color(r, g, b, 3, self.np0, 111, 116)
        self.set_color(r, g, b, 1, self.np3, 63)

        #left side connections from tp10 to top

        self.set_color(r, g, b, 1, self.np0, 89)
        self.set_color(r, g, b, 3, self.np0, 138, 143)
        self.set_color(r, g, b, 3, self.np0, 27, 55)
        self.set_color(r, g, b, 1, self.np3, 76)


        # ROC and LOC to top
        self.set_color(r, g, b, 3, self.np0, 168, 176)






        self.np0.write()
        self.np1.write()
        self.np2.write()
        self.np3.write()
        print("Small baby montage set to color:" (r, g, b))

    def eci(self, r, g, b):

        # Top
        self.set_color(r, g, b, 2, self.np3, 112)
        self.set_color(r, g, b, 3, self.np3, 116, 140)
        self.set_color(r, g, b, 3, self.np1, 10, 20)
        self.set_color(r, g, b, 3, self.np1, 30, 41)



        # BOTTOM
        self.set_color(r, g, b, 3, self.np0, 89, 107)
        self.set_color(r, g, b, 3, self.np0, 0, 26)
        self.set_color(r, g, b, 3, self.np0, 26, 55)





        self.np3.write()
        self.np1.write()
        self.np2.write()
        self.np0.write()
        print("ECI montage set to color:" (r, g, b))


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
                "red": (75, 0, 0),
                "blue": (0, 0, 75),
                "green": (0, 75, 0),
                "yellow": (75, 75, 0),
                "white": (75, 75, 75),
                "purple": (70, 0, 70),
                "orange": (76, 85, 0),
            }

            # Check if the color exists
            if color_name not in color_map:
                print(f"Unknown color: {color_name}")
                return

            r, g, b = color_map[color_name]  # Get RGB values

            # Call the appropriate function with the selected color

            # check to see if this function causes delays or issues with accurate propagation
            self.turn_off()

            if montage_name == "bipolar":
                self.bipolar(r, g, b)
            elif montage_name == "transverse":
                self.transverse(r, g, b)
            elif montage_name == "hatband":
                self.hatband(r, g, b)
            elif montage_name == "temporal":
                self.temporal(r, g, b)
            elif montage_name == "cz_ref":
                self.cz_ref(r, g, b)
            elif montage_name == "ear_ref":
                self.ear_ref(r, g, b)
            elif montage_name == "large":
                self.large(r, g, b)
            elif montage_name == "small":
                self.small(r, g, b)
            elif montage_name == "eci":
                self.eci(r, g, b)
            elif montage_name == "off":
                self.turn_off()
            else:
                print(f"Unknown montage: {montage_name}")

        except Exception as commandError:
            print(f"Error in command processing: {commandError}")


    def set_color(self, r, g, b, controlVariable, dataline, LED_ID = 0, LED_ID2 = 0):
        print(f"Setting LED {LED_ID} to RGB({r}, {g}, {b}) with controlVariable {controlVariable}")

        #for individual LEDs
        if controlVariable == 1:
            dataline[LED_ID] = (r, g, b)


        # for range from 0
        elif controlVariable == 2:
            print(f"made it to control var")

            for i in range(LED_ID):
                dataline[i] = (r, g, b)
            print(f"Color set to RGB({r}, {g}, {b})")


        # for ranges not from 0
        elif controlVariable == 3:
            print(f"made it to c-var 3")
            for i in range(LED_ID, LED_ID2):
                dataline[i] = (r, g, b)



    def start_advertising(self):
        name = "ESP32_BLE"
        service_uuid = UUID("3322271e-756a-443d-8a9d-2f90c7a73bf5")
        payload = advertising_payload(name=name, services=[service_uuid])
        self.ble.gap_advertise(100, adv_data=payload)
        self.ble.irq(self.ble_callback)
        print("BLE is ready and advertising")



# Initialize the peripheral
ble_peripheral = BLEPeripheral(525, 21, 22, 14, 32, 15, 33)

ButtonPin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=SwitchHandler)







