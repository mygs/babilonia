print("[NODEID] "..node.chipid())
----------------------
-------- UTILS -------
----------------------

function publish(status_dht, measured_temp, measured_humi)
  local parms = {}
  table.insert(parms, "id="..node.chipid())
  table.insert(parms, "&st="..status_dht)
  table.insert(parms, "&ct="..module.TEMPERATURE_SMA)
  table.insert(parms, "&mt="..measured_temp)
  table.insert(parms, "&mh="..measured_humi)
  table.insert(parms, "&sf="..fan())
  table.insert(parms, "&sl="..light())
  if(module.MQTT_STATUS == 0)then
    print("[MQTT CLIENT] Publishing")
    MQTTCLIENT:publish("/data", table.concat(parms,""), 0, 0)	-- publish
  else
    print("[MQTT CLIENT] Tried to publish, but NODE is disconnected")
  end
end


-- UPDATE PARAMETERS
function update()
  local parms = {}
  table.insert(parms, "?tag="..node.chipid())
  local url = table.concat(parms,"")
  http.get(url, nil, function(code, data)
      if (code < 0) then
        print("[UPDATE] NOK. Code "..code)
      else
        print("[UPDATE] OK")
      end

      local RES = {}
      if (data ~= nil)then
          for k, v in string.gmatch(data, "(%w+):([^;]*);*") do
              RES[k] = v
          end
      end
      if(RES.fan ~= nil)then
            fan(tonumber(RES.fan))
      end
      if(RES.light ~= nil)then
            light(tonumber(RES.light))
      end
      if(RES.temp ~= nil)then
            module.TEMPERATURE_THRESHOLD = tonumber(RES.temp)
      end
      if(RES.mclon ~= nil and RES.mcloff ~= nil and RES.mcctrl ~= nil)then
        if file.open("mask-cron.lua", "w") then
          file.writeline('module.MASK_CRON_LIGHT_ON=\"'..RES.mclon.."\"")
          file.writeline('module.MASK_CRON_LIGHT_OFF=\"'..RES.mcloff.."\"")
          file.writeline('module.MASK_CRON_CTRL=\"'..RES.mcctrl.."\"")
          file.close()
          print("Restarting NODE "..node.chipid())
          node.restart()
        end
      end

    end)
end
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
  return 1 - gpio.read(module.PIN_LIGHT)
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
  return 1 - gpio.read(module.PIN_FAN)
end

----------------------
----- INIT SETUP -----
----------------------
gpio.mode(module.PIN_FAN, gpio.OUTPUT)
gpio.mode(module.PIN_LIGHT, gpio.OUTPUT)
light(0)
fan(0)

----------------------
------ CONTROL -------
----------------------
function control()
  --local status, measured_temp, measured_temp_dec, measured_humi, measured_humi_dec = dht.read(module.PIN_DHT)
  local status = 7
  local measured_temp = 8
  local  measured_humi = 9
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
    publish(status,measured_temp,measured_humi)
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
