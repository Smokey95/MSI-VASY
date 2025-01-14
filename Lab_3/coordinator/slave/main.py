import xbee
from machine import I2C, Pin

PAN_ID = "4242"

def configure_network():
    print("Konfiguriere das Netzwerk...")
    try:
        # PAN-ID setzen
        xbee.atcmd("ID", bytes.fromhex(PAN_ID))
        xbee.atcmd("WR")
        print(f"PAN-ID erfolgreich gesetzt: {PAN_ID}")
    except Exception as e:
        print(f"Fehler beim Setzen der PAN-ID: {e}")

LED_PIN_RED = 3
LED_PIN_GREEN = 5
LED_PIN_BLUE = 6
LED_PIN_WHITE = 9

i2c = I2C(1, freq=100000)
arduino_address = 8

# value of 1 ist turned off
user_led = Pin('D4', Pin.OUT, value=1)
user_led.value(1)
status_led = False
configure_network()

data = bytearray([LED_PIN_RED, 0])
i2c.writeto(arduino_address, data)
while True:
    try:
        frame = xbee.receive()

        if not frame:
            continue

        print(frame)

        dest_ep = frame['dest_ep']
        payload = int.from_bytes(frame['payload'], 'big')
        cluster = frame['cluster']
        #broadcast = frame['sender_eui']

        brightness = 0

        if cluster == 0x0006:
            # on / off
            if payload == 0:
                brightness = 0
            elif payload == 1:
                brightness = 255
            else:
                print('wrong payload for cluster')
                continue

        elif cluster == 0x0008:
            if payload < 0 or payload > 255:
                print('payload not valid for cluster')
                continue

            brightness = payload

        else:
            print('not supported cluster')
            continue

        if dest_ep == 1:
            # controller 1 -> Red
            data = bytearray([LED_PIN_RED, brightness])
            i2c.writeto(arduino_address, data)

        elif dest_ep == 2:
            # controller 2 -> green blue
            data = bytearray([LED_PIN_GREEN, brightness])
            i2c.writeto(arduino_address, data)

            data = bytearray([LED_PIN_BLUE, brightness])
            i2c.writeto(arduino_address, data)

        elif dest_ep == 3:
            # controller 3 -> red, green, blue, white
            data = bytearray([LED_PIN_RED, brightness])
            i2c.writeto(arduino_address, data)

            data = bytearray([LED_PIN_GREEN, brightness])
            i2c.writeto(arduino_address, data)

            data = bytearray([LED_PIN_BLUE, brightness])
            i2c.writeto(arduino_address, data)

            data = bytearray([LED_PIN_WHITE, brightness])
            i2c.writeto(arduino_address, data)

        elif dest_ep == 4:
            # xbee other
            data = bytearray([LED_PIN_RED, brightness])
            i2c.writeto(arduino_address, data)

            data = bytearray([LED_PIN_GREEN, brightness])
            i2c.writeto(arduino_address, data)

            data = bytearray([LED_PIN_BLUE, brightness])
            i2c.writeto(arduino_address, data)

            data = bytearray([LED_PIN_WHITE, brightness])
            i2c.writeto(arduino_address, data)

            if status_led:
                user_led.value(1)
                status_led = False
            else:
                user_led.value(0)
                status_led = True

        elif dest_ep == 5:
            # xbee pc user button
            data = bytearray([LED_PIN_BLUE, brightness])
            i2c.writeto(arduino_address, data)

    except Exception as e:
        print(e)
