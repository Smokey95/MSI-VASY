from xbee import transmit, receive
import time

from network_utility import NetworkHeader

def debug_test_package():
    test_flooding_package = NetworkHeader(0, "0x69", "0x420", "OF")
    print(test_flooding_package)

def main():
    print("Hello World")
    debug_test_package()

    while(True):
        msg = receive()
        if msg:
            print(msg)


if __name__ == '__main__':
    main()