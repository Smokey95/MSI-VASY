# Copyright 2017, Digi International Inc.
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
import digi.xbee.io
from digi.xbee.devices import XBeeDevice
from digi.xbee.io import IOLine, IOMode, IOValue
import time
import threading

from tensorflow.python.keras.engine.training_utils_v1 import is_composite_or_composite_value

PORT = "COM3"
BAUD_RATE = 115200

# XBee SMT Grove Developer Board shares a DIO
IO_LINE_IN_OUT = IOLine.DIO4_AD4

def main():
    print(" +----------------------------------------------+")
    print(" | XBee Python Library Get/Set Local DIO Sample |")
    print(" +----------------------------------------------+\n")

    stop = False
    th = None

    device = XBeeDevice(PORT, BAUD_RATE)

    try:
        device.open()
        print("open device successfully")
        def io_detection_callback():
            print("io_detection_callback thread started")
            # increase timeout (otherwise there will be timeout exceptions all the time)
            device.set_sync_ops_timeout(10)
            while not stop:
                io_mode = device.get_io_configuration(IO_LINE_IN_OUT)

                # as the XBee SMT Grove Developer Board shares a DIO the mode may have to be reconfigured
                if io_mode != IOMode.DIGITAL_IN:
                    print("IO_LINE_IN has wrong io_configuration")
                    device.set_io_configuration(IO_LINE_IN_OUT, IOMode.DIGITAL_IN)
                    print("io_configuration of IO_LINE_IN changed")
                    continue

                # Read the digital value from the input line.
                #print("read out IO_Value")
                io_value = device.get_dio_value(IO_LINE_IN_OUT)
                print("%s: %s" % (IO_LINE_IN_OUT, io_value))

                # change io_mode again to output signal to UserLED
                device.set_dio_value(IO_LINE_IN_OUT, IOMode.DIGITAL_OUT_HIGH)

                # Set the previous value to the output line.
                device.set_dio_value(IO_LINE_IN_OUT, io_value)

                # Set fix value to the output line.
                #device.set_dio_value(IO_LINE_IN, IOValue.LOW)
                #time.sleep(1)
                #device.set_dio_value(IO_LINE_IN, IOValue.HIGH)
                time.sleep(1)

                # change io_mode again to get input signal
                device.set_io_configuration(IO_LINE_IN_OUT, IOMode.DIGITAL_IN)

        th = threading.Thread(target=io_detection_callback)

        th.start()

        input()

    finally:
        stop = True
        if th is not None and th.is_alive():
            th.join()
        if device is not None and device.is_open():
            device.close()


if __name__ == '__main__':
    main()