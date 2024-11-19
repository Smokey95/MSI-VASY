from digi.xbee.devices import Raw802Device
from digi.xbee.models.address import XBee16BitAddress
from struct import pack, unpack
from time import time, sleep

device = Raw802Device("COM3", 115200)

device.open()

device.set_parameter('NI', "COM15".encode())
device.set_parameter('MY', bytearray.fromhex("15"))
device.set_parameter('CH', bytes.fromhex("0C"))
device.set_parameter('ID', bytes.fromhex("1111"))

print("Node Identifier [NI]: " + str(device.get_parameter('NI')))
print("16-bit Network Address [MY]: " + device.get_parameter('MY'))
print("Operating Channel [CH]: " + device.get_parameter('CH'))
print("Extended PAN ID [ID]: " + device.get_parameter('ID'))

print('Starting Remote Range Test')

dest_addr = [13, 16]
packets = 50
inter_dest_delay_s = 0.1
inter_round_delay_s = 1
num_bytes = 4
payload = '0'*num_bytes

measurements = dict()

print('Starting range test with %d measurements' % packets)

for i in range(packets):
    for addr in dest_addr:
        print('Sending packet to address %d' % addr)
        device.send_data_16(XBee16BitAddress.from_hex_string(f'{addr}'), payload)
        sleep(inter_dest_delay_s)
    counter = 0
    flags = []
    t = time()
    while True:
        msg = device.read_data()
        if msg:
            t = time()
            rssi = int(device.get_parameter("DB").hex(),16)
            remote_addr = msg.remote_device.get_16bit_addr().address.hex()
            remote_rssi = unpack('<B', msg.data[0:1])[0]
            print(f'Received response from {remote_addr} with RSSI={rssi}, Remote-RSSI={remote_rssi}')
            measurements[(i, remote_addr)] = (rssi, remote_rssi)
            if not remote_addr in flags:
                flags.append(remote_addr)
                counter = counter+1
            else:
                print("Received response from {remote_addr} twice")
            if counter >= (len(dest_addr)-1)*2:
                print(f'Round {i}: All responses received')
                break
        if time()-t > inter_round_delay_s:
            print('Round %d: breaking round with %d responses' % (i, counter))
            break

print('Finished')

rssiD = dict()
remote_rssiD = dict()
for key, val in measurements.items():
    (i, src)=key
    l_rssi,r_rssi=val

    if src in rssiD:
        rssiD[src].append(l_rssi)
    else:
        rssiD[src] = [l_rssi]
    if src in remote_rssiD:
        remote_rssiD[src].append(r_rssi)
    else:
        remote_rssiD[src] = [r_rssi]

for src, L in rssiD.items():
    print(f"Rssi stats for {src}: Num={len(L)}, Min={min(L)}, Mean={sum(L)/len(L):.2f}, Max={max(L)}")
for src, L in remote_rssiD.items():
    print(f"Remote Rssi stats for {src}: Num={len(L)}, Min={min(L)}, Mean={sum(L)/len(L):.2f}, Max={max(L)}")

