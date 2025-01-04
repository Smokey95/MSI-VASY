# Default template for Digi projects
from xbee import transmit, receive, atcmd
from xbee_packet import XBeePacket, IDGenerator, XBeeMessage
from routing_table import RoutingTable, SHORTTICKS
from route_discovery import RouteDiscoveryTable
from utime import ticks_ms


MY_ADDRESS = 0x13
DEST_ADDRESS = 0x15
BLOCKED_ADDRESS = 0x15

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
        :param dest_addr: destination (device network address [MY]) of the message
        :param src_addr: source address or None if own address should be used as source
        :param msg: message to be sent
        :return:
        """
        if src_addr is None:
            src_addr = self.local_addr

        # get the route to destination and check if valid
        route_table_entry = self.routing_table.get_entry(dest_addr)
        if route_table_entry is None:
            print("Destination %s not found in routing table, initialize new route discovery" % hex(dest_addr))
            route_table_entry = self.__route_discovery(dest_addr, src_addr)

        # get next address to destination and send message
        next_hop_address = route_table_entry.get_next_hop_address()
        if next_hop_address == MY_ADDRESS:
            print(f"\033[91mError: next hop is own address: {hex(next_hop_address)}\033[0m")
            self.routing_table.delete_entries()
        else:
            print("next hop address: " + hex(next_hop_address))
            message = XBeeMessage(msg, src_addr, dest_addr)
            transmit(next_hop_address, message.to_bytearray())

    def __route_discovery(self, dest_addr: int, src_addr: int = None):
        """

        :param dest_addr:
        :param src_addr:
        :return:
        """
        print("start route discovery for destination %s" % hex(dest_addr))
        if src_addr is None:
            src_addr = self.local_addr

        # generate new route discovery package
        route_request = XBeePacket(2, src_addr, dest_addr, self.local_addr, self.id_generator.get_next(), 0)

        # add new entry to route discovery table
        self.route_discovery_table.add_or_update_entry((src_addr, dest_addr, route_request.get_identifier()), src_addr, 100, 100)
        transmit(BRODCAST_ADRESS, route_request.to_bytearray())
        route_discovery_start = ticks_ms()

        while True:
            if ticks_ms() - route_discovery_start > 1000:
                print("route discovery timed out")
                break
            msg = receive()
            if msg:
                response = XBeePacket.from_bytearray(msg['payload'])
                if response.get_type() == 2:
                    if response.get_src_addr() != self.local_addr:
                        print("Received a new RREQ while discovering route --> ignoring it")
                    else:
                        print("received my own RREQ while discovering route")

                if response.get_type() == 3:
                    print("recived an response to my route request:")
                    print(response)
                    resp_src_adrr = response.get_src_addr()
                    resp_dest_adrr = response.get_dest_addr()
                    resp_identifier = response.get_identifier()
                    resp_sender = response.get_sender()
                    route_discovery_entry = self.route_discovery_table.get_entry((resp_src_adrr, resp_dest_adrr, resp_identifier))
                    if route_discovery_entry is None:
                        print("received a RREP which is not in route discoverable table")
                        raise NotImplementedError # @todo: implement stuff
                    else:
                        print(f"\033[92madd entry to route discovery table with ({hex(resp_src_adrr)}, {hex(resp_dest_adrr)}, {resp_identifier}) and sender {hex(resp_sender)}\033[0m")
                        self.route_discovery_table.add_or_update_entry((resp_src_adrr, resp_dest_adrr, resp_identifier), resp_sender, response.get_path_cost(), 0)

        best_rrep = self.route_discovery_table.get_entry((src_addr, dest_addr, route_request.get_identifier()))
        print(best_rrep)
        self.routing_table.add_entry(dest_addr, best_rrep.get_sender())

        return self.routing_table.get_entry(dest_addr)



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


def init_device(type:str) -> (str, int):
    """
    initializes the device as sender, receiver or intermediary
    :param type: SENDER, RECEIVER or INTERMEDIARY
    """
    cmd_network_address = "MY"
    atcmd(cmd_network_address, MY_ADDRESS)

    if type == "2":
        type = "RECEIVER"
    else:
        type = "SENDER"

    local_addr = atcmd(cmd_network_address)
    print("device was initialized with the following parameters:")
    print(f"\tType: {type:<10}")
    print(f"\tAddress: {hex(local_addr)}")
    return type, local_addr


def main():

    # get information about device type
    (dev_type, local_addr) = init_device(input("enter device type: 1) Sender (default), 2) Receiver, or press Enter for default"))

    device = XBeeDevice(dev_type, local_addr, IDGenerator(), RoutingTable(), RouteDiscoveryTable())

    if device.get_device_type() == "SENDER":
        while True:
            input("Press enter to send Message to: " + hex(DEST_ADDRESS))
            device.send_msg(DEST_ADDRESS)
            userinput = input("press Enter to receive Message, R to print routing table: ")
            if userinput == "R":
                print(str(device.get_routing_table()))
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
        while True:
            msg = receive()
            if msg:
                print(msg['payload'])
                # List of decoding attempts, each with a decoding function and a label (to avoid nested try expect)
                decoders = [
                    (XBeePacket.from_bytearray, "XBeePacket"),
                    (XBeeMessage.from_bytearray, "XBeeMessage"),
                ]

                for decoder, decoder_name in decoders:
                    try:
                        packet = decoder(msg['payload'])
                        if packet.get_sender() == BLOCKED_ADDRESS:
                            print("\033[91mBlocked Message from sender: " + hex(packet.get_sender()) + "\033[0m")
                            break
                        if type(packet) == XBeeMessage:  # handle normal messages
                            dest_addr = packet.get_dest_addr()
                            if dest_addr == device.get_local_addr():
                                print(f"\033[92mreceived new msg of type {decoder_name} with payload:\033[0m")
                                print(f"\033[92m\t{str(packet)}\033[0m")
                            else:
                                print(f"received new msg of type {decoder_name} with destination {hex(dest_addr)}")
                                print(f"forward message to destination: ")
                                device.send_msg(dest_addr,None, packet.get_msg())
                        if type(packet) == XBeePacket:
                            print("received new XBeePacket")
                            if packet.get_type() == 2:
                                if packet.get_dest_addr() == device.get_local_addr():
                                    print(f"\033[92mreceived new msg of type {decoder_name}, i am the destination\033[0m")
                                    route_response = XBeePacket(3, packet.get_src_addr(), packet.get_dest_addr(), device.get_local_addr(), packet.get_identifier(), packet.get_path_cost())
                                    transmit(packet.get_sender(), route_response.to_bytearray())
                                else:
                                    print(f"received new msg of type {decoder_name}, i am NOT the destination")
                                    print(f"Broadcasting it with Destination {hex(packet.get_dest_addr())}")
                                    route_discovery = XBeePacket(2, packet.get_src_addr(), packet.get_dest_addr(), device.get_local_addr(), packet.get_identifier(), packet.get_path_cost())
                                    transmit(BRODCAST_ADRESS, route_discovery.to_bytearray())
                            if packet.get_type() == 3:
                                if packet.get_dest_addr() == device.get_local_addr():
                                    print("\033[91mRecieved a type 3 for me but iam currently not in route discovery mode\033[0m")
                                else:
                                    print(f"received new msg of type {decoder_name}, i am NOT the destination")
                                    print(f"Broadcasting it with Destination {hex(packet.get_dest_addr())}")
                                    route_discovery = XBeePacket(3, packet.get_src_addr(), packet.get_dest_addr(), device.get_local_addr(), packet.get_identifier(), packet.get_path_cost())
                                    transmit(packet.get_src_addr(), route_discovery.to_bytearray())

                        break
                    except ValueError:
                        pass
                else:
                    packet = msg['payload']
                    print(f"received msg of UNKNOWN type with payload:")
                    print(f"\t{str(packet)}")

                continue

if __name__ == "__main__":
    main()