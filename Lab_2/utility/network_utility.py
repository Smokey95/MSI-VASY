from digi.xbee.models.address import XBee16BitAddress

class NetworkHeader:

    FLOODING    = 0
    ACK         = 1

    def __init__(self, type_field = 0, src_addr = "0x00", dest_addr = "0x00", identifier = "NON"):
        """
        Create a NetworkHeader object.
        :param type_field: 0 = Flooding, 1 = ACK
        :param src_addr: MAC address of source node
        :param dest_addr: MAC address of destination node
        :param identifier: unique identifier for source and destination pair
        """
        self.type_field = type_field
        self.src_addr = XBee16BitAddress.from_hex_string(src_addr)
        self.dest_addr = XBee16BitAddress.from_hex_string(dest_addr)
        self.identifier = identifier

    def to_bytearray(self) -> bytearray:
        """
        Converts the NetworkHeader instance to a bytearray for XBee payload.
        """
        # Serialize attributes into bytes
        header = bytearray()
        #header.extend(self.src_addr.to_bytes(2, 'big'))    # 2 bytes for source_id                      # Add payload as-is
        header.extend(self.type_field.to_bytes(1, 'big'))
        header.extend(self.src_addr)
        header.extend(self.dest_addr)
        header.extend(self.identifier.encode())
        return header

    @classmethod
    def from_bytearray(cls, payload: bytearray) -> "NetworkHeader":
        """
        Creates a NetworkHeader instance from a bytearray.
        :param payload: The bytearray to parse.
        :return: A NetworkHeader instance.
        """
        # Extract type_field (1 byte)
        type_field = payload[0]

        # Extract src_addr (2 bytes)
        src_addr = XBee16BitAddress(payload[1:3])  # Create from raw bytes

        # Extract dest_addr (2 bytes)
        dest_addr = XBee16BitAddress(payload[3:5])  # Create from raw bytes

        # Extract identifier (remaining bytes)
        identifier = payload[5:].decode()  # Decode the remaining bytes as a string

        # Return a new instance of NetworkHeader
        return cls(type_field=type_field, src_addr=str(src_addr), dest_addr=str(dest_addr), identifier=identifier)

    def get_type_field(self):
        return self.type_field

    def get_src_addr(self) -> XBee16BitAddress:
        """
        get the source MAC address
        :return: XBee16BitAddress object
        """
        return self.src_addr

    def get_dest_addr(self) -> XBee16BitAddress:
        """
        get the destination MAC address
        :return:
        """
        return self.dest_addr

    def get_identifier(self):
        return self.identifier

    def __str__(self):
        return "NetworkHeader([type_field: " + str(self.type_field) + "], src_addr: " + str(self.src_addr) + ", dest_addr: " + str(self.dest_addr) + "], identifier: " + str(self.identifier) + "])"
