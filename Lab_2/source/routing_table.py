from utime import ticks_ms

LONGTICKS   = 100000000   #~27 hours, could be used as default value for route validity
SHORTTICKS  = 100        # could be used for testing and debugging

class RoutingTableEntry:

    def __init__(self, destination_address:int, next_hop_address:int):
        self.destination_address    = destination_address
        self.next_hop_address       = next_hop_address
        self.timestamp              = ticks_ms()

    def update_timestamp(self):
        """
        update the timestamp to the current time.
        """
        self.timestamp = ticks_ms()

    def get_timestamp(self):
        """
        return the current timestamp.
        :return: int ticks in ms
        """
        return self.timestamp

    def get_next_hop_address(self):
        """
        return the next hop address
        :return: next hop address
        """
        return self.next_hop_address

    def __str__(self):
        def int_to_hex(i):
            return  "0x{:07x}".format(i)
              #"| dest_addr | next_addr | timestamp |\n"
        return "| %s | %s | %9d |" % (int_to_hex(self.destination_address), int_to_hex(self.next_hop_address), self.timestamp)


class RoutingTable:
    def __init__(self, diff_ticks=LONGTICKS):
        """
        initialize a new routing table.
        :param timeout: ticks in ms till a routing entry will be discarded
        """
        self.entries = {}
        self.timeout = diff_ticks

    def add_entry(self, destination_address, next_hop_address):
        """
        add a new entry
        :param destination_address: destination address (key).
        :param next_hop_address: address of the next hop.
        """
        if destination_address in self.entries:
            print(f"Updating entry for destination address {hex(destination_address)}")
            self.entries[destination_address].next_hop_address = next_hop_address
            self.entries[destination_address].update_timestamp()
        else:
            print(f"Adding new entry for destination address {hex(destination_address)} with next hop_address {hex(next_hop_address)}")
            self.entries[destination_address] = RoutingTableEntry(destination_address, next_hop_address)

    def __remove_entry(self, destination_address):
        """
        remove an entry from the table.
        :param destination_address: Destination address (key).
        """
        if destination_address in self.entries:
            del self.entries[destination_address]
            print(f"Removed entry for {destination_address}")
        else:
            print(f"No entry found for {destination_address}")

    def get_entry(self, destination_address):
        """
        retrieve an entry from the table (if present) and update the timestamp. the method will also check if the entry
        is still valid (according to timeout) and will remove it, if not.
        :param destination_address: destination address (key).
        :return: RoutingTableEntry object or None if not found/invalid.
        """
        #print(f"DEBUG: request for destination address {hex(destination_address)}")
        entry = self.entries.get(destination_address)
        #print(f"DEBUG: entry is {entry}")

        # entry not in table
        if entry is None:
            return None

        # check if entry is still valid
        if (entry.get_timestamp() + self.timeout) < ticks_ms():
            self.__remove_entry(destination_address)
            return None
        else:
            entry.update_timestamp()
            return entry


    def cleanup_expired_entries(self):
        """
        remove entries that have been inactive longer than the timeout.
        """
        current_time = ticks_ms()
        expired_keys = [
            key for key, entry in self.entries.items()
            if (entry.get_timestamp() + self.timeout) < current_time
        ]

        for key in expired_keys:
            print(f"Removing expired entry for {key}")
            del self.entries[key]

    def delete_entries(self):
        """
        remove entries that have been inactive longer than the timeout.
        """
        expired_keys = [
            key for key, entry in self.entries.items()
        ]

        for key in expired_keys:
            print(f"Removing expired entry for {key}")
            del self.entries[key]

    def __str__(self):
        if not self.entries:
            return "routing table is empty."
        ret_val = "ROUTING TABLE\n"
        ret_val += "-------------------------------------\n"
        ret_val += "| dest_addr | next_addr | timestamp |\n"
        ret_val += "-------------------------------------\n"
        ret_val += ret_val.join(str(entries) for entries in self.entries.values())
        ret_val += "\n"
        return ret_val
