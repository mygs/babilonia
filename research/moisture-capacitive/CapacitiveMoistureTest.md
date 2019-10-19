## NODE SETUP
NODE_ID = oasis-397988


config message
```
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-397988\",\"MESSAGE_ID\": \"a12dc89b\",\"CONFIG\": {\"HEARTBEAT_PERIOD\": -1, \"SENSOR_COLLECT_DATA_PERIOD\": 300, \"PIN\":{\"0\": \"IDLE\",\"1\": \"IDLE\", \"2\": \"IDLE\", \"3\": \"IDLE\",\"4\": \"IDLE\",\"5\": \"IDLE\", \"6\": \"IDLE\",\"7\": \"IDLE\", \"8\": \"IDLE\"}}}"
```


status message capacitive
```
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-397988\", \"MESSAGE_ID\": \"a12dc89b\",\"STATUS\": [\"CAPACITIVEMOISTURE\"]}"
```
