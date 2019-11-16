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

* MUX0 -> TUBE   I: 130g (glass+soil)
* MUX1 -> TUBE  II: 130g (glass+soil); 150g (glass+soil+water) ~ 20g (water)
* MUX2 -> TUBE III: 130g (glass+soil); 170g (glass+soil+water) ~ 40g (water)
* MUX3 -> TUBE  IV: XXXg (glass+water)


###### SET002
* Tube IV (glass only): 60.6g (reference)

* MUX3 -> TUBE   I: 130g (glass+soil)
* MUX1 -> TUBE  II: 130g (glass+soil); 160g (glass+soil+water) ~ 30g (water)
* MUX2 -> TUBE III: 130g (glass+soil); 181g (glass+soil+water) ~ 51g (water)
* MUX0 -> TUBE  IV: XXXg (glass+water)

###### SET003
* Tube IV (glass only): 60.6g (reference)
* MUX0 -> TUBE   I: 130g (glass+soil)
* MUX1 -> TUBE  II: 130g (glass+soil); 165g (glass+soil+water) ~ 35g (water)
* MUX2 -> TUBE III: air
* MUX3 -> TUBE  IV: XXXg (glass+water)

#### MESSAGE_ID
MESSAGE_ID | TEST CONDITIONS | OBS
---------- | --------------- |
air00001| No soil |
test0001| SET001 |
test0002| SET002 | data corrupted
test0003| SET003 |

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
		DATA->'$.MESSAGE_ID' ='test0003'
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
