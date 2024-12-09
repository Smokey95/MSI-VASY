# Default template for Digi projects
from xbee import transmit, receive, atcmd
from xbee_packet import XBeePacket, IDGenerator, XBeeMessage
from routing_table import RoutingTable, SHORTTICKS
from route_discovery import RouteDiscoveryTable

SOURCE_ADDRES   = 0x15
DEST_ADDRES     = [0x13, 0x14]
BRODCAST_ADRESS = 0xFFFF

knownPackages = []
knownAckPackages = []

class XBeeDevice:

    def __init__(self, type:str, local_addr:int, id_generator:IDGenerator, routing_table:RoutingTable, route_discovery_table:RouteDiscoveryTable):
        """

        :param type:
        :param local_addr:
        :param id_generator:
        :param routing_table:
        :param route_discovery_table:
        """
        if type not in ["SENDER", "RECEIVER", "INTERMEDIARY"]:
            raise ValueError("Type must be either SENDER or RECEIVER or INTERMEDIARY")
        self.type                   = type
        self.local_addr             = local_addr
        self.id_generator           = id_generator
        self.routing_table          = routing_table
        self.route_discovery_table = route_discovery_table

    def get_device_type(self):
        return self.type

    def get_local_addr(self):
        return self.local_addr

    def get_routing_table(self):
        return self.routing_table

    def send_msg(self, dest_addr: int, src_addr: int = None,  msg: str = "Hello World!"):
        """
        sends a message to a destination node in network
        :param src_addr:
        :param dest_addr:
        :param msg:
        :return:
        """
        if src_addr is None:
            src_addr = self.local_addr

        # get the route to destination and check if valid
        route_table_entry = self.routing_table.get_entry(dest_addr)
        if route_table_entry is None:
            print("error: destination %s not found in routing table, initialize new route discovery" % hex(dest_addr))
            return
            # @todo: add route discovery process

        # get next address to destination and send message
        next_hop_address = route_table_entry.get_next_hop_address()
        message = XBeeMessage(msg, src_addr, dest_addr)
        transmit(next_hop_address, message.to_bytearray())

def send_flooding_paket(src_addr: str, dest_addr:str, sender_addr:int, id:int, path_cost:int = 0x00,type:int = 0):
    flooding_packet = XBeePacket(type, src_addr, dest_addr, sender_addr, id, path_cost)
    transmit(BRODCAST_ADRESS, flooding_packet.to_bytearray())
    print("sending done, packet: " + str(flooding_packet))


def check_packet_in_known_packets(packet: XBeePacket, knownPackets: list) -> bool:
    # Werte aus dem zu prüfenden Paket extrahieren
    src_addr = packet.get_src_addr()
    dest_addr = packet.get_dest_addr()
    identifier = packet.get_identifier()

    # Iteration durch die Liste knownPackets
    for known_packet in knownPackets:
        if (known_packet.get_src_addr() == src_addr and
                known_packet.get_dest_addr() == dest_addr and
                int.from_bytes(known_packet.identifier, "big") == identifier):
            return True  # Paket ist bereits bekannt

    return False  # Paket ist neu


def init_device(type:str) -> (str,int):
    """
    initializes the device as sender, receiver or intermediary
    :param type: SENDER, RECEIVER or INTERMEDIARY
    """
    cmd_network_address = "MY"

    if type == "2":
        type = "RECEIVER"
        atcmd(cmd_network_address, DEST_ADDRES[0])
    elif type == "3":
        type = "INTERMEDIARY"
        atcmd(cmd_network_address, DEST_ADDRES[1])
    else:
        type = "SENDER"
        atcmd(cmd_network_address, SOURCE_ADDRES)

    local_addr  = atcmd(cmd_network_address)
    print(f"device was initialized with the following parameters:")
    print(f"\tType: {type:<10}")
    print(f"\tAddress: {hex(local_addr)}")
    return (type, local_addr)


def main():

    # get information about device type
    (dev_type, local_addr) = init_device(input("enter device type: 1) Sender (default), 2) Receiver, 3) Intermediary or press Enter for default"))

    device = XBeeDevice(dev_type, local_addr, IDGenerator(), RoutingTable(), RouteDiscoveryTable())
    #id_gen                  = IDGenerator()
    #routing_table           = RoutingTable()
    #route_discvery_table    = RouteDiscoveryTable()

    if device.get_device_type() == "SENDER":
        # debug: add destination to routing table without RREQ
        device.routing_table.add_entry(DEST_ADDRES[0], DEST_ADDRES[0])
        device.routing_table.add_entry(DEST_ADDRES[1], DEST_ADDRES[0])

        while True:
            in_destination = input("enter destination device or press enter to send message to default (device 0)...")
            #send_flooding_paket(local_addr, DEST_ADDRES, local_addr, id_gen.get_next())
            #send_msg(local_addr, DEST_ADDRES[1], routing_table)
            if in_destination == "1":
                device.send_msg(DEST_ADDRES[1])
            else:
                device.send_msg(DEST_ADDRES[0])

            userinput = input("press Enter to receive Message, R to print routing table: ")
            if userinput == "R":
                print(str(device.get_device_type()))
            #debug
            elif userinput == "r":
                x = device.get_routing_table().get_entry(DEST_ADDRES[0])
            elif userinput == "clean":
                device.get_routing_table().cleanup_expired_entries()
            else:
                msg = receive()
                if msg:
                    packet = XBeePacket.from_bytearray(msg['payload'])
                    print("received new package: " + str(packet))
                else:
                    print("no message received")

    elif device.get_device_type() == "RECEIVER":
        # MAINLOOP
        while True:
            msg = receive()
            if msg:

                # List of decoding attempts, each with a decoding function and a label (to avoid nested try expect)
                decoders = [
                    (XBeePacket.from_bytearray, "XBeePacket"),
                    (XBeeMessage.from_bytearray, "XBeeMessage"),
                ]

                for decoder, decoder_name in decoders:
                    try:
                        packet = decoder(msg['payload'])
                        if type(packet) == XBeeMessage:
                            dest_addr = packet.get_dest_addr()
                            if dest_addr == device.get_local_addr():
                                print(f"received new msg of type {decoder_name} with payload:")
                                print(f"\t{str(packet)}")
                            else:
                                print(f"received new msg of type {decoder_name} with destination {hex(dest_addr)}")
                                print(f"forward message to destination")
                                device.send_msg(dest_addr)
                        break
                    except ValueError:
                        pass
                else:
                    packet = msg['payload']
                    print(f"received msg of UNKNOWN type with payload:")
                    print(f"\t{str(packet)}")

                continue

                if local_addr == packet.get_dest_addr() and packet.get_type() == 0:
                    print("ich bin empfaenger")
                    send_flooding_paket(local_addr,packet.get_src_addr(),local_addr,packet.get_identifier(),0,1)
                    knownAckPackages.append(XBeePacket(1, local_addr, packet.get_src_addr(), local_addr, packet.get_identifier(), 0))
                elif packet.get_type() == 0 and not check_packet_in_known_packets(packet, knownPackages):
                    print("paket ist neu ")
                    knownPackages.append(packet)
                    send_flooding_paket(packet.get_src_addr(), packet.get_dest_addr(), local_addr,
                                        packet.get_identifier(), packet.get_path_cost()+1)
                elif packet.get_type() == 1 and not check_packet_in_known_packets(packet, knownAckPackages):
                    print("paket ist neu ack")
                    knownAckPackages.append(packet)
                    send_flooding_paket(packet.get_src_addr(), packet.get_dest_addr(), local_addr,
                                        packet.get_identifier(), packet.get_path_cost()+1)




if __name__ == "__main__":
    main()
