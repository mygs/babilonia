print("[NODEID] "..node.chipid())
-------- UTILS -------
function publish(topic, data)
  if(module.MQTT_STATUS == 0)then
    print("[MQTT] Publishing")
    MQTTCLIENT:publish(topic,data, 0, 0)	-- publish
  else
    print("[MQTT] Not connected")
  end
end

function publish()
  -- power ON moisture sensors
  gpio.write(module.PIN_SENSORS_SWITCH, gpio.HIGH)
  tmr.delay(module.SLEEP_TIME_MOISTURE) -- time to moisture computes its values
  -- analogic 0 to 1024, where:
  -- [WET] low resistance  --- digital = 0 & led = ON
  -- [DRY] high resistance --- digital = 1 & led = OFF
  local analogic = adc.read(module.PIN_MOISTURE_A)
  -- power OFF sensors
  gpio.write(module.PIN_SENSORS_SWITCH, gpio.LOW)
  print("[Moisture]"..analogic)
  local parms = {}
  table.insert(parms, "id:"..node.chipid())
  table.insert(parms, ";value:"..analogic)
  publish("/moisture", table.concat(parms,""))
end

-- UPDATE PARAMETERS
function update(data)
  local RES = {}
  for k, v in string.gmatch(data, "(%w+):([^;]*);*") do
      RES[k] = v
  end
  -- id=NULL means broadcast
  if (RES.id == nil or tonumber(RES.id) == node.chipid()) then
    if (RES.setup ~= nil) then
      local setup = tonumber(RES.setup)
      if     setup == 10 then gpio.write(module.PIN_SENSORS_SWITCH, gpio.HIGH)
      elseif setup == 11 then gpio.write(module.PIN_SENSORS_SWITCH, gpio.LOW)
      end
    end
    if (RES.cmd ~= nil) then
          local cmd = tonumber(RES.cmd)

          if     cmd == 0 then reboot()
          elseif cmd == 1 then publish()
          elseif cmd == 2 then collectgarbage()
          elseif cmd == 3 then publish("/env", "heap: "..node.heap())
          elseif cmd == 4 then publish("/env", "info: "..node.info())
          else                 print("command not found")
          end
    end
  end
end

MQTTCLIENT:on("message",
function(conn, topic, data)
   print("[MQTT] MSG Received!")
   if (topic ~= nil and data ~= nil) then
     if (topic == "/cfg") then
         update(data)
     end
   end
end)

----- INIT SETUP -----
print("[SETUP] Started")
  -- power OFF sensors
gpio.write(module.PIN_SENSORS_SWITCH, gpio.LOW)
adc.force_init_mode(adc.INIT_ADC)
gpio.mode(module.PIN_MOISTURE_A, gpio.INPUT)
cron.schedule(module.MASK_CRON_CTRL,  function(e) publish() end)
collectgarbage()
print("[SETUP] Completed")
module.BABILONIA_STATUS = 0
