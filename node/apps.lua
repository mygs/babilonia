print("[NODEID] "..node.chipid())
----------------------
-------- UTILS -------
----------------------
function publish(topic, data)
  if(module.MQTT_STATUS == 0)then
    print("[MQTT CLIENT] Publishing")
    MQTTCLIENT:publish(topic,data, 0, 0)	-- publish
  else
    print("[MQTT CLIENT] Tried to publish, but NODE is still disconnected")
  end
end

function publish_data(status_dht, measured_temp, measured_humi)
  local parms = {}
  table.insert(parms, "id:"..node.chipid())
  table.insert(parms, ";st:"..status_dht)
  table.insert(parms, ";ct:"..string.format("%02.2f",module.TEMPERATURE_SMA))
  table.insert(parms, ";mt:"..measured_temp)
  table.insert(parms, ";mh:"..measured_humi)
  table.insert(parms, ";sf:"..fan())
  table.insert(parms, ";sl:"..light())
  publish("/data", table.concat(parms,""))
end

-- UPDATE PARAMETERS
function update(data)
  local RES = {}
  for k, v in string.gmatch(data, "(%w+):([^;]*);*") do
      RES[k] = v
  end
  if(RES.id == nil or tonumber(RES.id) == node.chipid())then
    if(RES.fan ~= nil)then
          fan(tonumber(RES.fan))
    end
    if(RES.light ~= nil)then
          light(tonumber(RES.light))
    end
    if(RES.cmd ~= nil)then
          local cmd = tonumber(RES.cmd)

          if     cmd == 0 then node.restart()
          elseif cmd == 1 then control()
          elseif cmd == 2 then collectgarbage()
          elseif cmd == 3 then publish("/env", "heap: "..node.heap())
          elseif cmd == 4 then publish("/env", "info: "..node.info())
          else                 print("command not found")
          end
    end

    if(RES.temp ~= nil)then
          module.TEMPERATURE_THRESHOLD = tonumber(RES.temp)
    end
    if(RES.mclon ~= nil and RES.mcloff ~= nil and RES.mcctrl ~= nil)then
      if file.open("nconfig.lua", "w") then
        file.writeline('module.LIGHT='..light())
        file.writeline('module.FAN='..fan())
        file.writeline('module.TEMPERATURE_THRESHOLD='..module.TEMPERATURE_THRESHOLD)
        file.writeline('module.MASK_CRON_LIGHT_ON=\"'..RES.mclon.."\"")
        file.writeline('module.MASK_CRON_LIGHT_OFF=\"'..RES.mcloff.."\"")
        file.writeline('module.MASK_CRON_CTRL=\"'..RES.mcctrl.."\"")
        file.close()
        print("Restarting NODE "..node.chipid())
        node.restart()
      end
    end
  end
end

MQTTCLIENT:on("message",
function(conn, topic, data)
   print("[MQTT CLIENT] Message Received...")
   if(topic ~= nil and data ~= nil) then
     if(topic == "/cmd") then
       update(data)
     end
   end
end)

--------------------------
--- SENSOR & ACTUATORS ---
--------------------------
-- ACTUATOR LIGHT
-- @param switch 1 = ON / 0 = OFF
-- @return 1 = ON / 0 = OFF
function light(switch)
  if (switch == 1) then
    gpio.write(module.PIN_LIGHT, gpio.LOW)
    print("[LIGHT] ON")
  elseif (switch == 0) then
    gpio.write(module.PIN_LIGHT, gpio.HIGH)
    print("[LIGHT] OFF")
  end
  module.LIGHT = 1 - gpio.read(module.PIN_LIGHT)
  return module.LIGHT
end

-- ACTUATOR FAN
-- @param switch 1 = ON / 0 = OFF
-- @return 1 = ON / 0 = OFF
function fan(switch)
  if (switch == 1) then
    gpio.write(module.PIN_FAN, gpio.LOW)
    print("[FAN] ON")
  elseif (switch == 0) then
    gpio.write(module.PIN_FAN, gpio.HIGH)
    print("[FAN] OFF")
  end
  module.FAN = 1 - gpio.read(module.PIN_FAN)
  return module.FAN
end

----------------------
----- INIT SETUP -----
----------------------
gpio.mode(module.PIN_FAN, gpio.OUTPUT)
gpio.mode(module.PIN_LIGHT, gpio.OUTPUT)
light(module.LIGHT)
fan(module.FAN)

----------------------
------ CONTROL -------
----------------------
function control()
  local status, measured_temp, measured_temp_dec, measured_humi, measured_humi_dec = dht.read(module.PIN_DHT)
  if (status == dht.OK) then -- so, filter the value
    module.TEMPERATURE_SMA = module.TEMPERATURE_SMA - module.TEMPERATURE_SMA/module.TEMPERATURE_NSAMPLES
    module.TEMPERATURE_SMA = module.TEMPERATURE_SMA + measured_temp/module.TEMPERATURE_NSAMPLES
    print("[CONTROL] Temp "..string.format("%02.2f",module.TEMPERATURE_SMA).."C")
    if (module.TEMPERATURE_SMA > module.TEMPERATURE_THRESHOLD) then
      fan(1)
    else
      fan(0)
    end
  end
    publish_data(status,measured_temp,measured_humi)
end
-----------------------
-- SCHEDULE ROUTINES --
-----------------------
cron.schedule(module.MASK_CRON_LIGHT_ON, function(e)
  light(1)
end)
cron.schedule(module.MASK_CRON_LIGHT_OFF, function(e)
  light(0)
end)
cron.schedule(module.MASK_CRON_CTRL, control)

-- free memory by destroying local variables
module.MASK_CRON_LIGHT_ON = nil
module.MASK_CRON_LIGHT_OFF = nil
module.MASK_CRON_CTRL = nil
collectgarbage()
