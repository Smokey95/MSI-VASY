from digi.xbee.devices import Raw802Device
from digi.xbee.models.address import XBee16BitAddress

from utility.network_utility import Packet

PRINT_SPACE = 34

DEST_ADDRES = [0xFFFF,    # Broadcast address
               0x13,      # destination client 1
               0x14]      # destination client 2

def connect_source_device(com_port = "COM4", baud_rate = 115200) -> Raw802Device:
    """
    opens the communication to a connected XBee device
    :param com_port: communication port (default COM3)
    :param baud_rate: baudrate (default 115200)
    :return: Raw802Device
    """
    device = Raw802Device(com_port, baud_rate)
    device.open()

    device.set_parameter('NI', "intermediary".encode())
    device.set_parameter('MY', bytearray.fromhex("13"))
    device.set_parameter('CH', bytes.fromhex("0C"))
    device.set_parameter('ID', bytes.fromhex("6969"))

    print("Connection to intermediary device opened!")
    print("Intermediary device has the following parameters:")
    print(f"{'  Node Identifier [NI]: ':<{PRINT_SPACE}}{'%s' %  (device.get_parameter('NI').decode('utf8'))}")
    print(f"{'  16-bit Network Address [MY]: ':<{PRINT_SPACE}}{'0x%s' % (device.get_parameter('MY').hex())}")
    print(f"{'  Operating Channel [CH]: ':<{PRINT_SPACE}}{'0x%s' % (device.get_parameter('CH').hex())}")
    print(f"{'  Extended PAN ID [ID]: ':<{PRINT_SPACE}}{'0x%s' % (device.get_parameter('ID').hex())}")

    return device

def close_source_device(device: Raw802Device):
    device.close()
    print("Connection to source device closed!")


def main():

    print("main")

    # open connection to connected device
    device = connect_source_device()

    try:

        device.flush_queues()
        print("Connection to intermediary device opened!")

        while True:
            xbee_message = device.read_data()
            if xbee_message is not None:
                packet = Packet.from_bytearray(xbee_message.data)
                print(packet)
                #print("From %s >> %s" % (xbee_message.remote_device.get_64bit_addr(), xbee_message.data.decode()))

        print("Waiting for data...\n")
        input()

    finally:
        if device is not None and device.is_open():
            device.close()

if __name__ == "__main__":
    main()