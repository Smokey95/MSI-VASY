import tkinter as tk
from tkinter import ttk
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress
from digi.xbee.io import IOLine, IOMode, IOValue

# Replace with your XBee device's serial port and baud rate
PORT        = "COM4"    # Update this with the actual port
BAUD_RATE   = 9600      # Default baud rate for XBee devices

# Addresses of the routers (replace with your XBee router MAC addresses)
ROUTER_1_ADDR = "0013A20041AE9D19"
ROUTER_2_ADDR = "0013A2004193C47B"
BROADCAST_ADDR = "FFFFFFFFFFFFFFFF"

LEVEL_CONTROL_CLUSTER       = 0x0008
ON_OFF_CLUSTER              = 0x0006
ENDPOINT_PC                 = 5
PROFILE_ID                  = 0x0104

# ZigBee network settings
PAN_ID      = "4242"    # Change to your desired PAN ID

# Initialize the XBee device
xbee_device = XBeeDevice(PORT, BAUD_RATE)


remote_device = RemoteXBeeDevice(xbee_device, XBee64BitAddress.from_hex_string(ROUTER_1_ADDR))


# XBee SMT Grove Developer Board shares a DIO
IO_LINE_IN_OUT = IOLine.DIO4_AD4
xbee_device.open()
xbee_device.set_dio_value(IO_LINE_IN_OUT, IOValue.HIGH)
xbee_device.close()


def test_toggle_user_led():
    """
    Toggles the USER LED on the connected XBee device.
    """
    try:
        # Open the device if not already open
        if not xbee_device.is_open():
            xbee_device.open()

        #xbee_device.set_dio_value(IO_LINE_IN_OUT, IOValue.LOW)
        # Send a remote AT command to toggle the USER LED
        led_state = xbee_device.get_dio_value(IO_LINE_IN_OUT)

        if led_state == IOValue.LOW:  # Assuming USER LED is currently ON
            print("Turning USER LED OFF...")
            xbee_device.set_dio_value(IO_LINE_IN_OUT, IOValue.HIGH)  # Set to HIGH (OFF)
        else:
            print("Turning USER LED ON...")
            xbee_device.set_dio_value(IO_LINE_IN_OUT, IOValue.LOW)   # Set to LOW (ON)

        xbee_device.write_changes()  # Save the changes
        print("USER LED state changed successfully.")

    except Exception as e:
        print(f"Error toggling USER LED: {e}")

    finally:
        xbee_device.close()

def test_send_message_to_router():

    device          = XBeeDevice(PORT, BAUD_RATE)
    router_address  = [ROUTER_1_ADDR, ROUTER_2_ADDR]
    message         = "Hello Router"

    for address in router_address:
        try:
            # Open the device
            device.open()

            # Send a test message to Router
            print(f"Sending message to {address}: {message}")
            # Create a remote XBee device object for the target router
            remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string(address))
            device.send_data(remote_device, message)
            print("Message sent successfully!")

        except Exception as e:
            print(f"Error sending message: {e}")

        finally:
            device.close()

def test_remote_LED():

    try:
        # Open the device
        xbee_device.open()

        # Send a test message to Router
        xbee_device.send_expl_data(remote_device, b'\x01', 0, 5, ON_OFF_CLUSTER, PROFILE_ID)
        print("On/off cluster send to device {remote_device}, endpoint {endpoint} with error: {e}")
        print("Message sent successfully!")


    except Exception as e:
        print(f"Error: {e}")

    finally:
        if xbee_device.is_open():
            xbee_device.close()

def configure_coordinator():
    device = XBeeDevice(PORT, BAUD_RATE)

    try:
        # Open the device
        device.open()

        # Set the PAN ID
        pan_id = bytes.fromhex(PAN_ID)
        device.set_pan_id(pan_id)
        device.set_parameter("CE", bytes.fromhex("01"))

        device.write_changes()

        print(f"Coordinator configured with PAN ID {PAN_ID}.")

    finally:
        if device.is_open():
            device.close()


class LEDControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LED Control Panel")

        # Frame for test code
        test_frame = ttk.LabelFrame(root, text="Test Area")
        test_frame.grid(column=0, row=0)

        # Test Button
        test_button = ttk.Button(test_frame, text="Toggle USER LED", command=test_toggle_user_led)
        test_button.grid(row=0, column=0, padx=10, pady=10)

        test_msg = ttk.Button(test_frame, text="Send message to router", command=test_send_message_to_router)
        test_msg.grid(row=0, column=1, padx=10, pady=10)

        test_connection = ttk.Button(test_frame, text="Test remote LED", command=test_remote_LED)
        test_connection.grid(row=0, column=2, padx=10, pady=10)

        # Frame for color selection
        color_frame = ttk.LabelFrame(root, text="Select LED Color")
        color_frame.grid(row=1, column=0, padx=10, pady=10)


    #def submit_data(self):


if __name__ == "__main__":

    # configure network settings
    configure_coordinator()

    root = tk.Tk()
    app = LEDControlApp(root)
    root.mainloop()

    # Close the XBee device when the application exits
    if xbee_device.is_open():
        xbee_device.close()
