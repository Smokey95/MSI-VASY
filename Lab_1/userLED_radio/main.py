from machine import Pin
import time
import xbee
# xbee.transmit(0x13, "10")
print(" >>> Blinking LED Radio Example\n")

led = Pin("D4", Pin.OUT, value=0)

def blink(n):
    while n > 0:
        led.value(0)
        time.sleep_ms(500)
        led.value(1)
        time.sleep_ms(500)
        n = n-1

xbee.atcmd('MY',0x13)
xbee.atcmd('CH',0x0C)
xbee.atcmd('ID',0x3339)

print('waiting to receive radio data')

while True:
    msg = xbee.receive()
    if msg:
        print(msg)
        payload = msg["payload"]
        if payload == b"exit":
            print("user requested exit")
            break
        try:
            payload = int(payload)
            blink(payload)
        except Exception as e:
            print("payload not an integer: {}".format(msg["payload"]))
