from machine import Pin
import time

# Defines the user LED pin (D4)
led_pin = Pin("D4", Pin.OUT)
led_pin.value(1)

def process_user_input():
    """
    reads in user input to turn on/off onboard LED
    """
    user_input = input("Type 'ON' to turn the LED on or 'OFF' to turn it off: ").strip().upper()

    if user_input == "ON":
        led_pin.value(0)    # Set to 0 to turn the LED ON (active-low)
        print("+ LED ON")
    elif user_input == "OFF":
        led_pin.value(1)     # Set to 1 to turn the LED OFF
        print("- LED OFF")
    else:
        print("Invalid input!")

# Infinite loop to blink the LED
while True:
    process_user_input()
    time.sleep_ms(100)