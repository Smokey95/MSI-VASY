# Default template for Digi projects
from xbee import transmit, receive, atcmd
from xbee_packet import XBeePacket, IDGenerator

DEST_ADDRES = [0xFFFF,    # Broadcast address
               0x13,      # destination client 1
               0x14]      # destination client 2

# Type SENDER, RECEIVER, INTERMEDIARY
TYPE        = "SENDER"

def send_flooding_paket(src_addr: str, dest_addr:str, id:int):
    flooding_packet = XBeePacket(1, src_addr, dest_addr, id)
    transmit(dest_addr, flooding_packet.to_bytearray())
    print("sending done, packet: " + str(flooding_packet))

def main():
    print("device started")

    id_gen = IDGenerator()

    mac_local = atcmd("MY")

    if TYPE == "SENDER":
        send_flooding_paket(mac_local, DEST_ADDRES[0], id_gen.get_next())
    elif TYPE == "RECEIVER":
        while True:
            msg = receive()
            if msg:
                print(msg)
    elif TYPE == "INTERMEDIARY":
        while True:
            msg = receive()
            if msg:
                print(msg)


if __name__ == "__main__":
    main()
