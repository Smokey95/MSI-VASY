# Task 2.2.2
# Local sender

from xbee import transmit, receive, atcmd
import time


def current_time():
    return time.ticks_ms() / 1000


def send_message(target_addr, data, interval_between_transmissions):
    transmit(target_addr, data)
    time.sleep_ms(interval_between_transmissions)


def process_response(device_results):
    response = receive()
    if response:
        rssi_local = atcmd("DB")
        sender = response["sender_nwk"]
        rssi_remote = response["payload"][1]
        if sender in device_results:
            device_results[sender]["rssi"].append(rssi_local)
            device_results[sender]["remote_rssi"].append(rssi_remote)
            return sender
    return None


def main():
    try:                                                                                                                # get user input
        rounds = int(input("Enter the number of test runs: "))
    except ValueError:
        print("Invalid input! Default value of 20 laps is used.")
        rounds = 20

    remote_nodes            = [0x13]                                                                                    # list of remote node addresses
    response_wait_timeout   = 0.1                                                                                       # timeout for remote response
    pause_between_rounds    = 1                                                                                         # time between two RSSI commands
    message_length          = 40

    test_message            = '0' * message_length                                                                      # message to trigger RSSI response from remote nodes

    device_results          = {addr: {"success": 0, "rssi": [], "remote_rssi": []} for addr in remote_nodes}            # create dictionary for results

    for round_num in range(rounds): # ---------------------------------------------------------------------------------- request
        print("round {} started".format(round_num + 1))
        received_addresses = []

        for target_addr in remote_nodes:                                                                                # send message to trigger RSSI response to all remote clients
            send_message(target_addr, test_message, 100)

        start_time = current_time()
        while current_time() - start_time < response_wait_timeout:                                                      # process responses from all remote devices
            responder = process_response(device_results)
            if responder and responder not in received_addresses:
                received_addresses.append(responder)

        for addr in remote_nodes:                                                                                       # check which remote devices respond
            if addr in received_addresses:
                device_results[addr]["success"] += 1

        print("round {} finished - answers received: {}/{}".format(round_num + 1, len(received_addresses),
                                                                     len(remote_nodes)))
        time.sleep(pause_between_rounds)

    for addr, stats in device_results.items(): # ----------------------------------------------------------------------- print results
        success_rate = stats["success"] / rounds * 100
        if stats["rssi"]:
            rssi_min = min(stats["rssi"])
            rssi_avg = sum(stats["rssi"]) / len(stats["rssi"])
            rssi_max = max(stats["rssi"])
        else:
            rssi_min = rssi_avg = rssi_max = 0

        if stats["remote_rssi"]:
            remote_rssi_min = min(stats["remote_rssi"])
            remote_rssi_avg = sum(stats["remote_rssi"]) / len(stats["remote_rssi"])
            remote_rssi_max = max(stats["remote_rssi"])
        else:
            remote_rssi_min = remote_rssi_avg = remote_rssi_max = 0

        print("results for device {}:".format(hex(addr)))
        print("  success rate: {:.1f}%".format(success_rate))
        print("  local RSSI: Min={}, Medium={:.2f}, Max={}".format(rssi_min, rssi_avg, rssi_max))
        print("  remote RSSI: Min={}, Medium={:.2f}, Max={}".format(remote_rssi_min, remote_rssi_avg, remote_rssi_max))

if __name__ == "__main__":
    main()