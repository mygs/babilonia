require("config")
MQTTCLIENT = nil
function conn_pub_sub(client)
	print ("[MQTT] Connected")
	MQTTCLIENT:subscribe("/cfg",0,
		function(conn)
			print("[MQTT] Subscribe success")
			local parms = {}
			table.insert(parms, "id:"..node.chipid())
			table.insert(parms, ";mode:"..module.MODE)
			if file.exists("remote.reboot") then
				table.insert(parms, ";rb:1")
				file.remove("remote.reboot")
			else
				table.insert(parms, ";rb:0")
			end
			if(module.BABILONIA_STATUS == 1) then
				print("[APP] Starting Babilonia App")
				if(module.MODE == 3) then
					require("moi")
				elseif(module.MODE == 2) then
					require("moistureTest")
				else
					require("apps")
				end
				MQTTCLIENT:publish("/online", table.concat(parms,""), 0, 0)	-- request conf.
			else
				print("[APP] Babilonia App already started")
				node.restart() -- FIXME: if reach this point, node lost communication
			end
		end)
	module.MQTT_STATUS = 0;
end
function do_mqtt_connect()
	print("[MQTT] Making connection.")
	MQTTCLIENT:connect(module.BABILONIA_SERVER,1883, 0,
  	conn_pub_sub,
    function(client, reason)
      print("[MQTT] Cannot connect. Reason: "..reason)
      module.MQTT_STATUS = 1;
      print("[MQTT] Trying again within "..module.SLEEP_TIME_MQTT.." secs")
      tmr.create():alarm(module.SLEEP_TIME_MQTT*1000, tmr.ALARM_SINGLE, do_mqtt_connect)
    end
  )
end
function handle_mqtt_error()
	module.MQTT_STATUS = 1;
	print("[MQTT] Disconnected, reconnecting....")
	MQTTCLIENT = nil
	--MQTTCLIENT:close()
	--do_mqtt_connect()
	createMqttConnection()
end
function createMqttConnection()
	print("[MQTT] Instantiating ")
	MQTTCLIENT = mqtt.Client(module.ID, module.SLEEP_TIME_MQTT)
	MQTTCLIENT:on("connect", conn_pub_sub)
	MQTTCLIENT:on("offline", handle_mqtt_error)
	do_mqtt_connect()
end
function startup()
	sntp.sync(module.BABILONIA_SERVER,  -- Sync clock for schedule
		function()
			if(module.BABILONIA_STATUS == 1) then
				print('[CLOCK] Sync OK')
				createMqttConnection()
			else
				print('[CLOCK] ReSync OK')
			end
		end,
		function()
			print('[CLOCK] Sync Failed.')
			startup()
		end,
		1 -- autorepeat
		)
end
function prepare_startup()
    if file.open("init.lua") == nil then
        print("init.lua not found")
    else
        file.close("init.lua")
				startup()
    end
end
wifi_connect_event = function(T)
  print("[WIFI] Connected to "..T.SSID)
  if disconnect_ct ~= nil then disconnect_ct = nil end
end
wifi_got_ip_event = function(T)
  print("[WIFI] IP: "..T.IP)
	if(module.BABILONIA_STATUS == 1) then
  	print("[WIFI] You have "..module.SLEEP_TIME_WIFI.."s to abort")
  	tmr.create():alarm(module.SLEEP_TIME_WIFI*1000, tmr.ALARM_SINGLE, prepare_startup)
	else
		print("[WIFI] Connection recovered procedures done!")
	end
end
wifi_disconnect_event = function(T)
  if T.reason == wifi.eventmon.reason.ASSOC_LEAVE then
    return
  end
  local total_tries = 20   --consider AP reboot duration.
  print("\n[WIFI] Connection to "..T.SSID.." failed!")
  for key,val in pairs(wifi.eventmon.reason) do
    if val == T.reason then
      print("[WIFI] Disconnect reason: "..val.."("..key..")")
      break
    end
  end
  if disconnect_ct == nil then
    disconnect_ct = 1
  else
    disconnect_ct = disconnect_ct + 1
  end
  if disconnect_ct < total_tries then
    print("[WIFI] Retrying connection...(attempt "..(disconnect_ct+1).." of "..total_tries..")")
  else
    print("[WIFI] Aborting connection and restarting NODE!")
		node.restart()
  end
end
wifi.eventmon.register(wifi.eventmon.STA_CONNECTED, wifi_connect_event)
wifi.eventmon.register(wifi.eventmon.STA_GOT_IP, wifi_got_ip_event)
wifi.eventmon.register(wifi.eventmon.STA_DISCONNECTED, wifi_disconnect_event)
print("[WIFI] Connecting")
wifi.setmode(wifi.STATION)
wifi.setphymode(wifi.PHYMODE_G)
wifi.sta.config({ssid=module.SSID, pwd=module.PASSWORD})
