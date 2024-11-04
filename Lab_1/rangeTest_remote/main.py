# task 2.2.2 Range Test
# this file contains the code for the remote device

import utime
from xbee import transmit, receive, atcmd

print('> starting range test: remote')

address_sender      = 0x01                                                                                              # MY setting in xBee Studio: Settings > Address > MY
timeout_duration    = 120                                                                                               # timeout to break loop after x seconds

def check_on_timeout(start_time) -> bool:
    if utime.ticks_diff(utime.ticks_ms(), start_time) > (timeout_duration * 1000):  # check on timeout
        print("Timeout reached, no message received.")
        return True
    return False

def main():
    start_time = utime.ticks_ms()                                                                                       # get timestamp for timeout tracking

    while True:
        msg = receive()
        if msg:
            if msg.get('sender_nwk') == address_sender:                                                                 # check 16-bit network address of sender
                rssi = atcmd("DB")                                                                                      # AT-command to get RSSI value from last paket
                print("received message from sender (ID:%d) with RSSI: %d" % (msg["sender_nwk"], rssi))
                transmit(msg["sender_nwk"], bytes([msg["broadcast"], rssi]))                                            # pass the received broadcast value and the rssi value as payload to sender
                print('send RSSI done')
                start_time = utime.ticks_ms()                                                                           # reset timeout watchdog
            else:
                print("received message from unknown sender")
        if check_on_timeout(start_time):                                                                                # check on timeout
            break

if __name__ == "__main__":
    main()
