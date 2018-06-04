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

function publish_data(status_dht, measured_temp, measured_humi, mma, mmb, mmc)
  local parms = {}
  table.insert(parms, "id:"..node.chipid())
  table.insert(parms, ";sd:"..status_dht)
  table.insert(parms, ";ct:"..string.format("%02.2f",module.TEMPERATURE_SMA))
  table.insert(parms, ";mt:"..measured_temp)
  table.insert(parms, ";mh:"..measured_humi)
  table.insert(parms, ";mma:"..mma)
  table.insert(parms, ";mmb:"..mmb)
  table.insert(parms, ";mmc:"..mmc)
  table.insert(parms, ";sf:"..fan())
  table.insert(parms, ";sl:"..light())
  publish("/data", table.concat(parms,""))
end
-- SAVE NODE CONFIGURATION
function save_configuration()
  -- remove old configuration set
  if file.exists("nconfig.lua") then
    file.remove("nconfig.lua")
  end
  if file.open("nconfig.lua", "w+") then
    -- writing new parameters
    file.writeline('module.TEMPERATURE_THRESHOLD='..module.TEMPERATURE_THRESHOLD)
    file.writeline('module.MASK_CRON_LIGHT_ON=\"'..module.MASK_CRON_LIGHT_ON.."\"")
    file.writeline('module.MASK_CRON_LIGHT_OFF=\"'..module.MASK_CRON_LIGHT_OFF.."\"")
    file.writeline('module.MASK_CRON_CTRL=\"'..module.MASK_CRON_CTRL.."\"")
    file.close()
  end

end
-- REBOOT NODE KEEPING CURRENT CONFIGURATION
function reboot()
  save_configuration()
  -- flaged as remote reboot
  if file.open("remote.reboot", "w") then
    file.close()
  end
  print("Restarting NODE "..node.chipid())
  node.restart()
end
-- UPDATE PARAMETERS
function update(data)
  local RES = {}
  for k, v in string.gmatch(data, "(%w+):([^;]*);*") do
      RES[k] = v
  end
  -- id=NULL means broadcast
  if (RES.id == nil or tonumber(RES.id) == node.chipid()) then
    if (RES.fan ~= nil) then
          fan(tonumber(RES.fan))
          local parms = {}
          table.insert(parms, "id:"..node.chipid())
          table.insert(parms, ";sf:"..fan())
          publish("/cmd-ack", table.concat(parms,""))
    end
    if (RES.light ~= nil) then
          light(tonumber(RES.light))
          local parms = {}
          table.insert(parms, "id:"..node.chipid())
          table.insert(parms, ";sl:"..light())
          publish("/cmd-ack", table.concat(parms,""))
    end
    if (RES.temp ~= nil) then
          module.TEMPERATURE_THRESHOLD = tonumber(RES.temp)
    end
    if (RES.mclon ~= nil) then
      module.MASK_CRON_LIGHT_ON=RES.mclon
    end
    if (RES.mcloff ~= nil) then
      module.MASK_CRON_LIGHT_OFF=RES.mcloff
    end
    if (RES.mcctrl ~= nil) then
      module.MASK_CRON_CTRL=RES.mcctrl
    end
    if (RES.cmd ~= nil) then
          local cmd = tonumber(RES.cmd)

          if     cmd == 0 then reboot()
          elseif cmd == 1 then control()
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
--- SENSOR & ACTUATORS ---
-- ACTUATOR LIGHT
-- @param switch 1 = ON / 0 = OFF
-- @return 1 = ON / 0 = OFF
function light(switch)
  if (switch == 1) then
    gpio.write(module.PIN_LIGHT, gpio.LOW)
    print("[LIGHT] ON")
    if file.open("light.on", "w") then
      file.close()
    end
  elseif (switch == 0) then
    gpio.write(module.PIN_LIGHT, gpio.HIGH)
    print("[LIGHT] OFF")
    if file.exists("light.on") then
      file.remove("light.on")
    end
  end
  return 1 - gpio.read(module.PIN_LIGHT)
end
-- ACTUATOR FAN
-- @param switch 1 = ON / 0 = OFF
-- @return 1 = ON / 0 = OFF
function fan(switch)
  if (switch == 1) then
    gpio.write(module.PIN_FAN, gpio.LOW)
    print("[FAN] ON")
    if file.open("fan.on", "w") then
      file.close()
    end
  elseif (switch == 0) then
    gpio.write(module.PIN_FAN, gpio.HIGH)
    print("[FAN] OFF")
    if file.exists("fan.on") then
      file.remove("fan.on")
    end
  end
  return  1 - gpio.read(module.PIN_FAN)
end
-- ACTUATOR SPRINKLE
function sprinkle()
  print("[SPRINKLE] ON")
  gpio.write(module.PIN_PUMP_SOLENOID, gpio.HIGH)
  tmr.delay(module.SLEEP_TIME_SPRINKLE)
  gpio.write(module.PIN_PUMP_SOLENOID, gpio.LOW)
  print("[SPRINKLE] OFF")
end
------ CONTROL -------
function control()
  -- power ON moisture sensors
  gpio.write(module.PIN_SENSORS_SWITCH, gpio.HIGH)
  local status, measured_temp, measured_humi, measured_temp_dec, measured_humi_dec = dht.read(module.PIN_DHT)
  tmr.delay(module.SLEEP_TIME_MOISTURE) -- time to moisture computes its values
  -- analogic 0 to 1024, where:
  -- [WET] mmx < 500 --- digital = 0 & led = ON
  -- [DRY] mmx > 500 --- digital = 1 & led = OFF
  local mma = gpio.read(module.PIN_MOISTURE_A)
  local mmb = gpio.read(module.PIN_MOISTURE_B)
  local mmc = gpio.read(module.PIN_MOISTURE_C)
  -- power OFF sensors
  gpio.write(module.PIN_SENSORS_SWITCH, gpio.LOW)
  if (status == dht.OK) then -- so, filter the value
    module.TEMPERATURE_SMA = module.TEMPERATURE_SMA - module.TEMPERATURE_SMA/module.TEMPERATURE_NSAMPLES
    module.TEMPERATURE_SMA = module.TEMPERATURE_SMA + measured_temp/module.TEMPERATURE_NSAMPLES
  end
  local  temp_str = string.format("%02.2f",module.TEMPERATURE_SMA)
  print("[CTRL] Temp: "..temp_str.."C | Moisture:["..mma..","..mmb..","..mmc.."]")
  publish_data(status,measured_temp,measured_humi, mma, mmb, mmc)
  if (module.MODE == 0) then -- indoor
    if (module.TEMPERATURE_SMA > module.TEMPERATURE_THRESHOLD) then
      fan(1)
    else
      fan(0)
    end
  elseif (module.MODE == 1) then -- outdoor
    if (mma == 1 or mmb == 1 or mmc == 1) then
      sprinkle()
    end
  end
end
----- INIT SETUP -----
print("[SETUP] Started")

gpio.mode(module.PIN_FAN, gpio.OUTPUT)
gpio.mode(module.PIN_LIGHT, gpio.OUTPUT)
gpio.mode(module.PIN_MOISTURE_A, gpio.INPUT)
gpio.mode(module.PIN_MOISTURE_B, gpio.INPUT)
gpio.mode(module.PIN_MOISTURE_C, gpio.INPUT)
-- power OFF sensors
gpio.write(module.PIN_SENSORS_SWITCH, gpio.LOW)
-- power OFF pump or solenoid
gpio.write(module.PIN_PUMP_SOLENOID, gpio.LOW)

if (module.MODE == 0) then -- indoor
  if file.exists("fan.on") then fan(1) else fan(0) end
  if file.exists("light.on") then light(1) else light(0) end
  cron.schedule(module.MASK_CRON_LIGHT_ON, function(e) light(1) end)
  cron.schedule(module.MASK_CRON_LIGHT_OFF, function(e) light(0) end)
elseif (module.MODE == 1) then -- outdoor
  gpio.write(module.PIN_FAN, gpio.LOW)
  gpio.write(module.PIN_LIGHT, gpio.LOW)
end
cron.schedule(module.MASK_CRON_CTRL, control)
collectgarbage()
print("[SETUP] Completed")
