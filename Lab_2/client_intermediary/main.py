from xbee import transmit, receive, atcmd
import time

from network_utility import Packet


def main():
    print("started intermediary client")

    mac_local = atcmd("MY")
    print("local mac address: {}".format(mac_local))

    while(True):
        msg = receive()
        if msg:
            payload = Packet.from_bytearray(msg.get("payload"))
            print("received payload {}".format(payload))

            if payload.is_flooding():
                print("flooding...")
                if payload.get_dest_addr() == mac_local:
                    print("i am dest of flooding")
                elif payload.get_dest_addr() != mac_local:
                    print("i am NOT dest of flooding")



if __name__ == '__main__':
    main()