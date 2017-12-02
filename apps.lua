local count_ctrl = 0
----------------------
-------- UTILS -------
----------------------

-- UPLOAD DATA TO GOOGLE SPREADSHEET
function upload(status_dht, measured_temp, measured_humid)
  local parms = {}
  table.insert(parms, DATAREPO)
  table.insert(parms, "?tag="..NODEID.."&st="..status_dht.."&ct="..TEMPERATURE_SMA)
  table.insert(parms, "&mt="..measured_temp.."&mh="..measured_humid)
  table.insert(parms, "&sf="..fan().."&sl="..light())
  parms = table.concat(parms,"")
  http.get(parms, nil, function(code, data)
      if (code < 0) then
        print("[UPLOAD] NOK. Code "..code)
      else
        print("[UPLOAD] OK")
      end
    end)
  --collectgarbage()
end


-- UPDATE PARAMETERS
function update()
  http.get(DATAREPO.."?tag="..NODEID, nil, function(code, data)
      if (code < 0) then
        print("[UPDATE] NOK. Code "..code)
      else
        print("[UPDATE] OK")
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
              TEMPERATURE_THRESHOLD = tonumber(RES.temp)
        end
        if(RES.ruu ~= nil)then
          RATIO_CTRL_UPDATE_UPLOAD = tonumber(RES.ruu)
        end
        if(RES.mclon ~= nil and RES.mcloff ~= nil and RES.mcctrl ~= nil)then
          if file.open("mask-cron.lua", "w") then
            file.writeline('MASK_CRON_LIGHT_ON=\"'..RES.mclon.."\"")
            file.writeline('MASK_CRON_LIGHT_OFF=\"'..RES.mcloff.."\"")
            file.writeline('MASK_CRON_CTRL=\"'..RES.mcctrl.."\"")
            file.close()
            node.restart()
          end
        end
      end
    end)
    --collectgarbage()
end
--------------------------
--- SENSOR & ACTUATORS ---
--------------------------
-- ACTUATOR LIGHT
-- @param switch 1 = ON / 0 = OFF
-- @return 1 = ON / 0 = OFF
function light(switch)
  if (switch == 1) then
    gpio.write(PIN_LIGHT, gpio.LOW)
    print("[LIGHT] ON")
  elseif (switch == 0) then
    gpio.write(PIN_LIGHT, gpio.HIGH)
    print("[LIGHT] OFF")
  end
  return 1 - gpio.read(PIN_LIGHT)
end

-- ACTUATOR FAN
-- @param switch 1 = ON / 0 = OFF
-- @return 1 = ON / 0 = OFF
function fan(switch)
  if (switch == 1) then
    gpio.write(PIN_FAN, gpio.LOW)
    print("[FAN] ON")
  elseif (switch == 0) then
    gpio.write(PIN_FAN, gpio.HIGH)
    print("[FAN] OFF")
  end
  return 1 - gpio.read(PIN_FAN)
end

----------------------
----- INIT SETUP -----
----------------------
gpio.mode(PIN_FAN, gpio.OUTPUT)
gpio.mode(PIN_LIGHT, gpio.OUTPUT)
light(0)
fan(0)

----------------------
------ CONTROL -------
----------------------
function control()
  local status, measured_temp,measured_temp_dec,measured_humi,measured_humi_dec = dht.read(PIN_DHT)
  if (status == dht.OK) then -- so, filter the value
    TEMPERATURE_SMA = TEMPERATURE_SMA - TEMPERATURE_SMA/TEMPERATURE_NSAMPLES
    TEMPERATURE_SMA = TEMPERATURE_SMA + measured_temp/TEMPERATURE_NSAMPLES
    print("[CONTROL] Temp "..string.format("%02.2f",TEMPERATURE_SMA).."C")
    if (TEMPERATURE_SMA > TEMPERATURE_THRESHOLD) then
      fan(1)
    else
      fan(0)
    end
  end
  if (count_ctrl >= RATIO_CTRL_UPDATE_UPLOAD) then
    upload(status,measured_temp,measured_humi)
    count_ctrl = 1
  else
    update()
    count_ctrl = count_ctrl + 1
  end
end
-----------------------
-- SCHEDULE ROUTINES --
-----------------------
cron.schedule(MASK_CRON_LIGHT_ON, function(e)
  light(1)
end)
cron.schedule(MASK_CRON_LIGHT_OFF, function(e)
  light(0)
end)
cron.schedule(MASK_CRON_CTRL, control)

MASK_CRON_LIGHT_ON = nil
MASK_CRON_LIGHT_OFF = nil
MASK_CRON_CTRL = nil
collectgarbage()
