## NODE SETUP
NODE_ID = oasis-397988


### Configuration
```
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-397988\",\"MESSAGE_ID\": \"a12dc89b\",\"CONFIG\": {\"HEARTBEAT_PERIOD\": 2000000000, \"SENSOR_COLLECT_DATA_PERIOD\": 2000000000, \"PIN\":{\"A\": \"CAPACITIVEMOISTURE\", \"0\": \"IDLE\",\"1\": \"IDLE\", \"2\": \"IDLE\", \"3\": \"IDLE\",\"4\": \"IDLE\",\"5\": \"IDLE\", \"6\": \"IDLE\",\"7\": \"IDLE\", \"8\": \"IDLE\"}}}"
```
* Heart beat and Sensor collect data period 2000000000 ms ~ 555 hrs ~ 23 days


### Messaging

#### Test Tube
as of 19/10/2019
* TUBE I (dry): 145g (glass+soil)
* TUBE II (semiwet): 145g (glass+soil) + 20g (water) = 165g
* TUBE III (almowet1): 145g (glass+soil) + 40g (water) = 185g
* TUBE I (wet): 145g (glass+soil) + ... 80?
* TUBE IV (water): 125g (glass+water)



#### MESSAGE_ID
TEST | MESSAGE_ID
---- | ----------
Water| water001
Dry| dry00001
Semi wet| semiwet1
Wet| wet00001
Air| air00001

#### Request
```
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-397988\", \"MESSAGE_ID\": \"a12dc89b\",\"STATUS\": [\"CAPACITIVEMOISTURE\"]}"
```
#### Response
```
{"NODE_ID":"oasis-397988","NODE_IP":"192.168.2.102","FIRMWARE_VERSION":"eef666c","MESSAGE_ID":"a12dc89b","DATA":{"CAPACITIVEMOISTURE":301}}
```
