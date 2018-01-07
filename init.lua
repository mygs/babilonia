-- load configurations
require("config")
MQTTCLIENT = nil
------------------------------------------------------------------------------
---------------------------------- MQTT --------------------------------------
------------------------------------------------------------------------------
-- Establish a connection to the MQTT broker with the configured parameters.

function do_mqtt_connect()
	print("[MQTT CLIENT] Making connection. BROKER:"..module.BROKER..":".. module.PORT)
	MQTTCLIENT:connect(module.BROKER, module.PORT, 0,
    function(client)
      print ("[MQTT CLIENT] Connected")
      local reqConf = "id="..node.chipid()
      MQTTCLIENT:publish("/online", reqConf, 0, 0)	-- request conf.

      MQTTCLIENT:subscribe({["/cfg"]=0,
                            ["/cmd"]=1}
                            ,0,
      function(conn)
        print("[MQTT CLIENT] Subscribe success")
      end)
      module.MQTT_STATUS = 0;
    end,
    function(client, reason)
      print("[MQTT CLIENT] Cannot connect. Failed reason: "..reason)
      module.MQTT_STATUS = 1;
      print("[MQTT CLIENT] Trying again within "..module.SLEEP_TIME.." seconds")
      tmr.create():alarm(module.SLEEP_TIME*1000, tmr.ALARM_SINGLE, do_mqtt_connect)
    end
  )
end

-- Reconnect to MQTT when we receive an "offline" message.
function handle_mqtt_error()
	print("[MQTT CLIENT] Disconnected, reconnecting....")
  module.MQTT_STATUS = 1;
	do_mqtt_connect()
end
-- createMqttConnection() instantiates the MQTT control object, sets up callbacks,
-- connects to the broker, and then uses the timer to send sensor data.
-- This is the "main" function in this library. This should be called
-- from init.lua (which runs on the ESP8266 at boot), but only after
-- it's been vigorously debugged.
--
-- Note: once you call this from init.lua the only way to change the
-- program on your ESP8266 will be to reflash the NodeCMU firmware!

function createMqttConnection()
	-- Instantiate a global MQTT client object
	print("[MQTT CLIENT] Instantiating ")
	MQTTCLIENT = mqtt.Client(module.ID, module.SLEEP_TIME)

	-- Set up the event callbacks
	print("[MQTT CLIENT] Setting up callbacks")
	MQTTCLIENT:on("connect",
      function(client)
        print ("[MQTT CLIENT] Connected")
        local reqConf = "id="..node.chipid()
        MQTTCLIENT:publish("/online", reqConf, 0, 0)	-- request conf.

        MQTTCLIENT:subscribe("/conf",0,
        function(conn)
          print("[MQTT CLIENT] Subscribe success")
        end)
        module.MQTT_STATUS = 0;
      end)
	MQTTCLIENT:on("offline", handle_mqtt_error)

	-- Connect to the Broker
	do_mqtt_connect()
end

------------------------------------------------------------------------------
--------------------------------- STARTUP ------------------------------------
------------------------------------------------------------------------------
function startup()
    if file.open("init.lua") == nil then
        print("init.lua deleted or renamed")
    else
        print("Starting Babilonia App")
        file.close("init.lua")
        -- the actual application is stored in 'apps'
        sntp.sync("pool.ntp.br", function() -- sntp sync is for schedule
          createMqttConnection()
          require("apps")
        end)
    end
end

------------------------------------------------------------------------------
--------------- Define WiFi station event callbacks --------------------------
------------------------------------------------------------------------------
wifi_connect_event = function(T)
  print("Connection to AP("..T.SSID..") established!")
  print("Waiting for IP address...")
  if disconnect_ct ~= nil then disconnect_ct = nil end
end
------------------------------------------------------------------------------
wifi_got_ip_event = function(T)
  -- Note: Having an IP address does not mean there is internet access!
  -- Internet connectivity can be determined with net.dns.resolve().
  print("Wifi connection is ready! IP address is: "..T.IP)
  print("Startup will resume momentarily, you have "..module.SLEEP_TIME.." seconds to abort.")
  print("Waiting...")
  tmr.create():alarm(module.SLEEP_TIME*1000, tmr.ALARM_SINGLE, startup)
end
------------------------------------------------------------------------------
wifi_disconnect_event = function(T)
  if T.reason == wifi.eventmon.reason.ASSOC_LEAVE then
    --the station has disassociated from a previously connected AP
    return
  end
  -- total_tries: how many times the station will attempt to connect to the AP.
  --  Should consider AP reboot duration.
  local total_tries = 100
  print("\nWiFi connection to AP("..T.SSID..") has failed!")

  --There are many possible disconnect reasons, the following iterates through
  --the list and returns the string corresponding to the disconnect reason.
  for key,val in pairs(wifi.eventmon.reason) do
    if val == T.reason then
      print("Disconnect reason: "..val.."("..key..")")
      break
    end
  end

  if disconnect_ct == nil then
    disconnect_ct = 1
  else
    disconnect_ct = disconnect_ct + 1
  end
  if disconnect_ct < total_tries then
    print("Retrying connection...(attempt "..(disconnect_ct+1).." of "..total_tries..")")
  else
    wifi.sta.disconnect()
    print("Aborting connection to AP!")
    disconnect_ct = nil
  end
end
------------------------------------------------------------------------------
--------------- Register WiFi Station event callbacks ------------------------
------------------------------------------------------------------------------
wifi.eventmon.register(wifi.eventmon.STA_CONNECTED, wifi_connect_event)
wifi.eventmon.register(wifi.eventmon.STA_GOT_IP, wifi_got_ip_event)
wifi.eventmon.register(wifi.eventmon.STA_DISCONNECTED, wifi_disconnect_event)

print("Connecting to WiFi access point...")
wifi.setmode(wifi.STATION)
wifi.setphymode(wifi.PHYMODE_G)
wifi.sta.config({ssid=module.SSID, pwd=module.PASSWORD})
-- wifi.sta.connect() not necessary because config() uses auto-connect=true by default
