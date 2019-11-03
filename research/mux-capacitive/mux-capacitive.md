## NODE SETUP
NODE_ID = oasis-397988


### Configuration
```
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-397988\",\"MESSAGE_ID\": \"test-muxcap\",\"CONFIG\": {\"HEARTBEAT_PERIOD\": 2000000000, \"SENSOR_COLLECT_DATA_PERIOD\": 2000000000, \"PIN\":{\"A\": \"CAPACITIVEMOISTURE\", \"0\": \"IDLE\",\"1\": \"IDLE\", \"2\": \"IDLE\", \"3\": \"IDLE\",\"4\": \"IDLE\",\"5\": \"SW.A\", \"6\": \"SW.B\",\"7\": \"SW.C\", \"8\": \"IDLE\"}}}"
```
* Heart beat and Sensor collect data period 2000000000 ms ~ 555 hrs ~ 23 days


### Messaging
monitoring
```
mosquitto_sub -h 192.168.2.1 -t "#" -v | grep oasis-397988
mosquitto_sub -h 192.168.1.70 -t "#" -v | grep oasis-397988

```
request
```
 mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-397988\", \"MESSAGE_ID\": \"a12dc89b\",\"STATUS\": [\"CAPACITIVEMOISTURE\"]}"
```

#### Test Tube


###### SET001
As of 03/Nov/2019 10AM
* Tube IV (glass only): 60.6g (reference)

* TUBE   I: 130g (glass+soil)
* TUBE  II: 130g (glass+soil); 150g (glass+soil+water) ~ 20g (water)
* TUBE III: 130g (glass+soil); 170g (glass+soil+water) ~ 40g (water)
* TUBE  IV: XXXg (glass+water)

###### SET00?
* Tube IV (glass only): 60.6g (reference)
* TUBE   I: ?
* TUBE  II: ?
* TUBE III: ?
* TUBE  IV: ?

#### MESSAGE_ID
MESSAGE_ID | TEST CONDITIONS
---------- | ----------
air00001| No soil
test0001| SET001


#### Query to extract data

```
SELECT	TIMESTAMP,
		DATA->'$.DATA.CAPACITIVEMOISTURE.MUX0' AS MUX0,
        DATA->'$.DATA.CAPACITIVEMOISTURE.MUX1' AS MUX1,
        DATA->'$.DATA.CAPACITIVEMOISTURE.MUX2' AS MUX2,
        DATA->'$.DATA.CAPACITIVEMOISTURE.MUX3' AS MUX3,
        DATA->'$.DATA.CAPACITIVEMOISTURE.MUX4' AS MUX4,
        DATA->'$.DATA.CAPACITIVEMOISTURE.MUX5' AS MUX5,
        DATA->'$.DATA.CAPACITIVEMOISTURE.MUX6' AS MUX6,
        DATA->'$.DATA.CAPACITIVEMOISTURE.MUX7' AS MUX7
FROM farmland.OASIS_DATA
WHERE 	NODE_ID='oasis-397988' AND
		DATA->'$.MESSAGE_ID' ='air00001'
ORDER BY TIMESTAMP ASC;
```


#### Request
```
mosquitto_pub -h 192.168.2.1 -t "/oasis-inbound" -m "{\"NODE_ID\": \"oasis-397988\", \"MESSAGE_ID\": \"a12dc89b\",\"STATUS\": [\"CAPACITIVEMOISTURE\"]}"
```
#### Response
```
{"NODE_ID":"oasis-397988","NODE_IP":"192.168.2.102","FIRMWARE_VERSION":"eef666c","MESSAGE_ID":"a12dc89b","DATA":{"CAPACITIVEMOISTURE":301}}
```
