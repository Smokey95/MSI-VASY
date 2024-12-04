# Default template for Digi projects
from xbee import transmit, receive, atcmd
from xbee_packet import XBeePacket, IDGenerator

DEST_ADDRES = 0x01
BRODCAST_ADRESS = 0xFFFF

# Type SENDER, RECEIVER, INTERMEDIARY
TYPE        = "RECEIVER"
knownPackages = []
knownAckPackages = []


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

def main():
    print("device started")

    id_gen = IDGenerator()

    mac_local = atcmd("MY")
    print("My Adress: "+ str(mac_local))

    if TYPE == "SENDER":
        while True:
            send_flooding_paket(mac_local, DEST_ADDRES, mac_local, id_gen.get_next())
            input("Press Enter to receive Message...")
            msg = receive()
            if msg:
                packet = XBeePacket.from_bytearray(msg['payload'])
                print("Empfangen: " + str(packet))
            input("Press Enter to Send Message...")
    elif TYPE == "RECEIVER":
        while True:
            msg = receive()
            if msg:
                packet = XBeePacket.from_bytearray(msg['payload'])
                print(packet)
                if mac_local == packet.get_dest_addr() and packet.get_type() == 0:
                    print("ich bin empfaenger")
                    send_flooding_paket(mac_local,packet.get_src_addr(),mac_local,packet.get_identifier(),0,1)
                    knownAckPackages.append(XBeePacket(1, mac_local, packet.get_src_addr(), mac_local, packet.get_identifier(), 0))
                elif packet.get_type() == 0 and not check_packet_in_known_packets(packet, knownPackages):
                    print("paket ist neu ")
                    knownPackages.append(packet)
                    send_flooding_paket(packet.get_src_addr(), packet.get_dest_addr(), mac_local,
                                        packet.get_identifier(), packet.get_path_cost()+1)
                elif packet.get_type() == 1 and not check_packet_in_known_packets(packet, knownAckPackages):
                    print("paket ist neu ack")
                    knownAckPackages.append(packet)
                    send_flooding_paket(packet.get_src_addr(), packet.get_dest_addr(), mac_local,
                                        packet.get_identifier(), packet.get_path_cost()+1)




if __name__ == "__main__":
    main()
