# rangeTest local

## Dictionary `device_results`

`device_result` is a dictionary to store the RSSI results for each remote device and is initialised using dictionary comprehension.

### Exemplary initialisation:

    device_results = {
        0x13: {
            "success": 0,         # Counts the successful rounds
            "rssi": [],           # Saves the local RSSI values
            "remote_rssi": []     # Saves the RSSI values of the remote device
        }
    }