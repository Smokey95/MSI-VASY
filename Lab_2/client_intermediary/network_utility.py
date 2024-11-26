import time

class Packet:

    # Packet type definitions
    packet_type =  [0,  # Flooding
                    1,  # Acknowledge (ACK)
                    2,  # Route Request (RREQ)
                    3]  # Route Reply (RREP)


    def __init__(self, type_field = 0, src_addr = 0x00, dest_addr = 0x00, identifier = 0x00, path_cost = 0x00):
        """
        Create a network packet.
        :param type_field: 0 = Flooding, 1 = ACK, 2 = RREQ, 3 = RREP
        :param src_addr: MAC address of source node
        :param dest_addr: MAC address of destination node
        :param identifier: keep empty to create unique identifier for this packet
        :param path_cost: path cost from source node to destination node
        """
        self.type           = type_field.to_bytes(1, 'big')
        self.src_addr       = src_addr.to_bytes(2, 'big')
        self.dest_addr      = dest_addr.to_bytes(2, 'big')
        if identifier == 0x00:
            self.identifier = self.__generate_id().to_bytes(2, 'big')
        else:
            self.identifier = identifier.to_bytes(2, 'big')
        self.path_cost      = path_cost.to_bytes(2, 'big')

    def to_bytearray(self) -> bytearray:
        """
        Converts the NetworkHeader instance to a bytearray for XBee payload.
        """
        # Serialize attributes into bytes
        header = bytearray()

        header.extend(self.type)
        header.extend(self.src_addr)
        header.extend(self.dest_addr)
        header.extend(self.identifier)
        if self.type == self.packet_type[2] or self.type == self.packet_type[3]:
            header.extend(self.path_cost)
        return header

    @classmethod
    def from_bytearray(cls, payload: bytearray) -> "Packet":
        """
        Creates a network Packet instance from a bytearray (payload).\n
        Raises ValueError if payload is not in a legal "Packet" format.
        :param payload: The bytearray to parse.
        :return: A NetworkHeader instance.
        """
        # check if payload is of legal packet size
        if len(payload) != 7 and len(payload) != 9:
            raise ValueError("payload is not from type: Packet")

        # Extract type_field (1 byte)
        type_field = payload[0]

        # check if payload contains legal packet type
        if type_field not in cls.packet_type:
            raise ValueError("invalid packet type")

        # Extract src_addr (2 bytes)
        src_addr = int.from_bytes(payload[1:3], "big")  # Create from raw bytes

        # Extract dest_addr (2 bytes)
        dest_addr = int.from_bytes(payload[3:5], "big")  # Create from raw bytes

        # Extract identifier (remaining bytes)
        identifier = int.from_bytes(payload[5:7], "big")  # Decode the remaining bytes as a string

        # Extract path cost if type is RREQ or RREP, else 0x00
        path_cost = 0x00
        if type_field == cls.packet_type[2] or type_field == cls.packet_type[3]:
            path_cost = int.from_bytes(payload[7:9], "big")

        # Return a new instance of network packet
        return cls(type_field, src_addr, dest_addr, identifier, path_cost)

    def get_type(self) -> int:
        """
        returns the type of the packet.\n
        0 = Flooding\n
        1 = Acknowledge (ACK)\n
        2 = Route Request (RREQ)\n
        3 = Route Reply (RREP)\n
        :return: int - type of the packet.
        """
        return int.from_bytes(self.type, "big")

    def is_flooding(self):
        """
        returns true if the packet is a Flooding.
        :return: bool
        """
        return int.from_bytes(self.type, "big") == self.packet_type[0]

    def is_ack(self):
        """
        returns true if the packet is Acknowledge (ACK)
        :return: bool
        """
        return int.from_bytes(self.type, "big") == self.packet_type[1]

    def is_route_request(self):
        """
        returns true if the packet is Route Request (RREQ)
        :return: bool
        """
        return int.from_bytes(self.type, "big") == self.packet_type[2]

    def is_route_reply(self):
        """
        returns true if the packet is Route Reply (RREP)
        :return: bool
        """
        return int.from_bytes(self.type, "big") == self.packet_type[3]

    def get_src_addr(self) -> int:
        """
        get the source MAC address
        :return: str source address
        """
        return int.from_bytes(self.src_addr, "big")

    def get_dest_addr(self) -> int:
        """
        get the destination MAC address
        :return: str destination address
        """
        return int.from_bytes(self.dest_addr, "big")

    def get_flooding_addr(self) -> str:
        """
        get the flooding MAC address
        :return: returns the current flooding MAC address (mostly 0xFFFF)
        """
        return "0xFFFF"

    def get_identifier(self) -> str:
        return self.identifier.hex()

    def __generate_id(self):
        """
        generate a unique id using a time based pseudo-random approach as micropython does not support "random" module...
        :return:
        """
        magic_start_bits    = 0xC000   # Magic start bits: every id starts with 1100

        # Generate a 12-bit random number
        seed = time.ticks_us() # get "random" time ticks as seed
        seed_12 = seed & 0x0FFF # extract lower 12 bits

        random_value = magic_start_bits | seed_12

        # Combine magic start bits with random value
        return random_value


    def __str__(self):
        return "Packet([type_field: " + str(self.type) + "], [src_addr: 0x" + str(self.src_addr) + "], [dest_addr: 0x" + str(self.dest_addr) + "], [identifier: " + str(self.identifier) + "], [path_cost: 0x" + str(self.path_cost) + "]"