from digi.xbee.devices import Raw802Device
from digi.xbee.models.address import XBee16BitAddress

from utility.network_utility import NetworkHeader

PRINT_SPACE = 34

DEST_ADDRES = [0xFFFF,    # Broadcast address
               0x13,      # destination client 1
               0x14]      # destination client 2

def connect_source_device(com_port = "COM3", baud_rate = 115200) -> Raw802Device:
    """
    opens the communication to a connected XBee device
    :param com_port: communication port (default COM3)
    :param baud_rate: baudrate (default 115200)
    :return: Raw802Device
    """
    device = Raw802Device(com_port, baud_rate)
    device.open()

    device.set_parameter('NI', "sender".encode())
    device.set_parameter('MY', bytearray.fromhex("15"))
    device.set_parameter('CH', bytes.fromhex("0C"))
    device.set_parameter('ID', bytes.fromhex("6969"))

    print("Connection to sender device opened!")
    print("Sender device has the following parameters:")
    print(f"{'  Node Identifier [NI]: ':<{PRINT_SPACE}}{'%s' %  (device.get_parameter('NI').decode('utf8'))}")
    print(f"{'  16-bit Network Address [MY]: ':<{PRINT_SPACE}}{'0x%s' % (device.get_parameter('MY').hex())}")
    print(f"{'  Operating Channel [CH]: ':<{PRINT_SPACE}}{'0x%s' % (device.get_parameter('CH').hex())}")
    print(f"{'  Extended PAN ID [ID]: ':<{PRINT_SPACE}}{'0x%s' % (device.get_parameter('ID').hex())}")

    return device

def close_source_device(device: Raw802Device):
    device.close()
    print("Connection to source device closed!")

def send_flooding_paket(device: Raw802Device, dest_address:str):
    flooding_packet = NetworkHeader(1, int.from_bytes(device.get_parameter('CH'), "big"), dest_address)
    #flooding_packet = NetworkHeader(1, 0x0c, dest_address)
    device.send_data_16(XBee16BitAddress.from_hex_string(flooding_packet.get_dest_addr()), flooding_packet.to_bytearray())
    print("sending done, packet: " + str(flooding_packet))

def main():
    print("main")
    # open connection to connected device
    src_device = connect_source_device()

    #send first flooding
    send_flooding_paket(src_device, DEST_ADDRES[1])

    # close connecition to connected device
    close_source_device(src_device)

if __name__ == "__main__":
    main()