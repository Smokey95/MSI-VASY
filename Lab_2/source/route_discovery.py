from utime import ticks_ms

class RouteDiscoveryEntry:
    def __init__(self, process_id, sender_address, forward_cost, residual_cost=None, expiration_time=None):
        """
        represents a single entry in the route discovery table.
        :param process_id: Tuple (source_address, destination_address, identifier) identifying the RREQ process.
        :param sender_address: Address of the node that sent the "best" RREQ.
        :param forward_cost: Path cost from source to this node.
        :param residual_cost: Path cost from this node to the destination (optional, filled after RREP).
        :param expiration_time: Time when the entry expires (optional).
        """
        self.process_id         = process_id
        self.sender_address     = sender_address
        self.forward_cost       = forward_cost
        self.residual_cost      = residual_cost
        self.expiration_time    = expiration_time

    def update(self, sender_address, forward_cost):
        """
        update the entry with a new sender address and forward cost if it's better.
        :param sender_address: New sender address.
        :param forward_cost: New forward cost.
        """
        self.sender_address = sender_address
        self.forward_cost   = forward_cost

    def get_sender(self):
        return self.sender_address

    def __str__(self):
        """
        readable representation of a route discovery table entry.
        """
        # | p-id | send_addr | forw_cost | resi_cost | expire |
        return "| %s | %s | %s |" % (self.process_id, self.sender_address, self.forward_cost)
        #return (f"Process ID: {self.process_id}, Sender: {self.sender_address}, "
        #        f"Forward Cost: {self.forward_cost}, Residual Cost: {self.residual_cost}, "
        #        f"Expiration Time: {self.expiration_time}")


class RouteDiscoveryTable:
    def __init__(self, timeout=60):
        """
        initialize the route discovery table.
        :param timeout: Time in seconds after which an entry is considered expired.
        """
        self.entries = {}
        self.timeout = timeout

    def add_or_update_entry(self, process_id, sender_address, forward_cost, link_cost):
        """
        Add a new entry or update an existing one with better forward costs.
        :param process_id: Tuple (source_address, destination_address, identifier).
        :param sender_address: Address of the node that sent the RREQ.
        :param forward_cost: Current path cost.
        :param link_cost: Cost of the link to the previous hop.
        """
        #updated_cost = forward_cost + link_cost
        updated_cost = link_cost

        if process_id in self.entries:
            # Update only if the new RREQ has lower forward cost
            entry = self.entries[process_id]
            if updated_cost < entry.forward_cost:
                print(f"Updating entry for {process_id} with better forward cost: {updated_cost}")
                entry.update(sender_address, updated_cost)
        else:
            print(f"RouteDiscoveryTable: Adding new entry for {hex(process_id[0])}, {hex(process_id[1])}, {hex(process_id[2])} and sender {hex(sender_address)}")
            expiration_time = self._calculate_expiration_time()
            self.entries[process_id] = RouteDiscoveryEntry(
                process_id, sender_address, updated_cost, expiration_time=expiration_time
            )

    def remove_entry(self, process_id):
        """
        Remove an entry from the table.
        :param process_id: Process ID (tuple of source, destination, identifier).
        """
        if process_id in self.entries:
            del self.entries[process_id]
            print(f"Removed entry for {process_id}")
        else:
            print(f"No entry found for {process_id}")

    def get_entry(self, process_id):
        """
        Retrieve an entry from the table.
        :param process_id: Process ID (tuple of source, destination, identifier).
        :return: RouteDiscoveryEntry object or None if not found.
        """
        return self.entries.get(process_id)

    def cleanup_expired_entries(self, current_time):
        """
        Remove entries that have expired based on the timeout.
        :param current_time: Current system time in relative ticks (e.g., from utime.ticks_ms()).
        """
        expired_keys = [
            key for key, entry in self.entries.items()
            if current_time - entry.expiration_time > self.timeout
        ]
        for key in expired_keys:
            print(f"Removing expired entry for {key}")
            del self.entries[key]

    def _calculate_expiration_time(self):
        """
        Calculate the expiration time for a new entry.
        :return: Expiration time relative to system start.
        """
        from utime import ticks_ms
        return ticks_ms()

    def __str__(self):
        """Readable representation of the entire route discovery table."""
        if not self.entries:
            return "Route discovery table is empty."
        return "\n".join(str(entry) for entry in self.entries.values())