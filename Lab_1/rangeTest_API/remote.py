from digi.xbee.devices import Raw802Device
from time import time
from struct import pack

comL = [13, 16]

class Device(Raw802Device):
    def __init__(self, com):
        Raw802Device.__init__(self,f"COM{com}", 115200)
        self.name = f"COM{com}"
        #self.device = Raw802Device(f"COM{com}", 115200)
        self.open()


        self.set_parameter('NI', f"COM{com}".encode())
        self.set_parameter('MY', bytearray.fromhex(f"{com}"))
        self.set_parameter('CH', bytes.fromhex("0C"))
        self.set_parameter('ID', bytes.fromhex("1111"))

        print(f"Name: {self.get_parameter('NI')}")
        print(f"Address:{self.get_parameter('MY')}")
        print(f"Channel: {self.get_parameter('CH')}")
        print(f"PAN ID: {self.get_parameter('ID')}")
        self.flush_queues()



deviceL=[]
for com in comL:
    print('Hallo')
    deviceL.append(Device(com))

print('Starting Remote Range Test')
t = time()
timeout = 10
while time()-t < timeout:
    for device in deviceL:
        msg = device.read_data()
        if msg:
            t = time()
            rssi = int(device.get_parameter("DB").hex(),16)
            remote_addr = msg.remote_device.get_16bit_addr()
            data = msg.data.decode()
            print(f"Device {device.name} received message {data} from {remote_addr.address.hex()} with RSSI {rssi}")
            device.send_data_16(remote_addr, pack('<B', rssi))
print('finished')
for device in deviceL:
    device.close()

