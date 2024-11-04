# rangeTest remote
The code provided here is attended for a XBee RSSI range test to run on the remote devices.
## `receive()`
- [Documentation/Source](https://www.digi.com/resources/documentation/digidocs/90002219/reference/r_function_receive.htm?TocPath=XBee%20module%7CXBee%20MicroPython%20module%20on%20the%20XBee3%20Zigbee%20RF%20Module%7C_____3)

Use this function to return a single entry from the receive queue.
This function accepts no parameters, and returns either **None** when there is no packet waiting, or a dictionary containing the following entries:

    sender_nwk:     16-bit network address of the sending node (absent on DigiMesh devices)
    sender_eui64:   the 64-bit address (as a bytearray) of the sending node. (None if no 64-bit address is present)
    source_ep:      the source endpoint as an integer
    dest_ep:        the destination endpoint as an integer
    cluster:        the cluster id as an integer
    profile:        the profile id as an integer
    broadcast:      either True or False depending on whether the frame was broadcast or unicast
    payload:        a bytes object of the payload (intentional selection of bytes object over string since the payload can contain binary data)

**Note that this receive function is non blocking**

## `transmit()`
- [Documentation/Source](https://www.digi.com/resources/documentation/digidocs/90002219/reference/r_function_transmit.htm?tocpath=XBee%20module%7CXBee%20MicroPython%20module%20on%20the%20XBee%203%20RF%C2%A0Modules%7C_____5)

Use this function to transmit a packet to a specified destination address. This function either succeeds and returns None, or raises an exception. For exception description see full documentation.

    xbee.transmit(dest, payload[, source_ep][, dest_ep][, cluster][, profile][, bcast_radius][, tx_options])

The transmit values are defined like:

    dest:           destination address of the message, and accepts any of the following (see doc for further information)
    payload:        parameter should be a string or bytes object
    source_ep:      optional 8-bit Source Endpoint for the transmission, defaulting to xbee.ENDPOINT_DIGI_DATA
    dest_ep:        optional 8-bit Destination Endpoint for the transmission, defaulting to xbee.ENDPOINT_DIGI_DATA.
    cluster:        optional 16-bit Cluster ID for the transmission, defaulting to xbee.CLUSTER_DIGI_SERIAL_DATA.
    profile:        optional 16-bit Cluster ID for the transmission, defaulting to xbee.PROFILE_DIGI_XBEE.
    bcast_radius:   optional 8-bit value to set the maximum number of hops a broadcast transmission can traverse. Default is 0.
    tx_options:     optional 8-bit bitfield that configures advanced transmission options. See the protocol-specific user guide for TX Options usage.

## `atcmd()`
- [Documentation/Source](https://www.digi.com/resources/documentation/digidocs/90002219/reference/r_function_atcmd.htm?tocpath=XBee%20module%7CXBee%20MicroPython%20module%20on%20the%20XBee%203%20RF%C2%A0Modules%7C_____1)

Use this function to set or query an AT command on the XBee device.

    xbee.atcmd(cmd[, value])

The atcmd values are defined like:
    
    cmd:            parameter is a two-character string that represents the command
    value:          parameter is optional (see documation/source for further information)

- [XBee AT Command References](https://widi.lecturer.pens.ac.id/Praktikum/Praktikum%20Mikro/XBee_ZB_ZigBee_AT_Commands.pdf)
- [AT commands that do not work in MicroPython](https://www.digi.com/resources/documentation/digidocs/90002219/Default.htm#reference/r_unavailable_at.htm?Highlight=AT%20Commands)