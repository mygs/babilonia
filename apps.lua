----------------------
----- VARIABLES ------
----------------------
-- check config file

----------------------
-------- UTILS -------
----------------------

-- CONSOLE AUDIT
-- @param func Function name
-- @param info Additional information
-- @return Console log audit
function audit(func, info)
  if (VERBOSE == true) then
    local log=""
    local tm = rtctime.epoch2cal(rtctime.get())
    log=string.format(FMT_TIME, tm["year"], tm["mon"], tm["day"], tm["hour"], tm["min"])
    print(log.." ["..func.."] "..info)
  end
end

-- SYNCRONIZE INTERNAL CLOCK (UTC)
function sync_clock()
  sntp.sync(SERVER_NTP, function()
    audit("SYNC CLOCK", "")
  end)
end

-- UPLOAD DATA TO GOOGLE SPREADSHEET
function upload(measured_temp, measured_humid, status_fan, status_light)
  collectgarbage("collect")
  local parms = {}
  table.insert(parms, DATAREPO)
  table.insert(parms, "?tag="..NODEID.."&ct="..TEMPERATURE_SMA)
  table.insert(parms, "&mt="..measured_temp.."&mh="..measured_humid)
  table.insert(parms, "&sf="..status_fan.."&sl="..status_light)
  parms = table.concat(parms,"")
  print("URL >>> "..parms)
  http.get(parms, nil, function(code, data)
      if (code < 0) then
        audit("UPLOAD","HTTPS request failed")
      else
        --print(code, data)
        audit("UPLOAD","HTTPS request success")
      end
    end)
end

--------------------------
--- SENSOR & ACTUATORS ---
--------------------------

-- SENSOR DHT
-- @return temp Temperature (Celsius)
-- @return humi Humidity (Percentage)
function tempHum()
  status, temp, humi, temp_dec, humi_dec = dht.read(PIN_DHT)
  if status == dht.ERROR_CHECKSUM then
    audit("DHT", "Checksum error.")
    return -1,-1,-1,-1
  elseif status == dht.ERROR_TIMEOUT then
    audit("DHT", "Timed out.")
    return -1,-1,-1,-1
  elseif status == dht.OK then
    audit("DHT", string.format("Temperature: %d.%02dC Humidity: %d.%02d%%",temp,temp_dec,humi,humi_dec))
    return temp,temp_dec,humi,humi_dec
  end
  audit("DHT", "Unknown status")
  return -1,-1,-1,-1
end

-- ACTUATOR LIGHT
-- @param switch 1 = ON / 0 = OFF
-- @return 1 = ON / 0 = OFF
function light(switch)
  if (switch == 1) then
    gpio.write(PIN_LIGHT, gpio.LOW)
    audit("LIGHT", "ON")
  elseif (switch == 0) then
    gpio.write(PIN_LIGHT, gpio.HIGH)
    audit("LIGHT", "OFF")
  end
  return 1 - gpio.read(PIN_LIGHT)
end

-- ACTUATOR FAN
-- @param switch 1 = ON / 0 = OFF
-- @return 1 = ON / 0 = OFF
function fan(switch)
  if (switch == 1) then
    gpio.write(PIN_FAN, gpio.LOW)
    audit("FAN", "ON")
  elseif (switch == 0) then
    gpio.write(PIN_FAN, gpio.HIGH)
    audit("FAN", "OFF")
  end
  return 1 - gpio.read(PIN_FAN)
end

----------------------
----- INIT SETUP -----
----------------------
sync_clock()
gpio.mode(PIN_FAN, gpio.OUTPUT)
gpio.mode(PIN_LIGHT, gpio.OUTPUT)
light(0)
fan(0)

----------------------
------ CONTROL -------
----------------------
-- CONTROL TEMPERATURE
function control_temperature()
  local measured_temp,measured_temp_dec,measured_humi,measured_humi_dec = tempHum()
  if (measured_temp ~= nil) then -- so, filter the value
    TEMPERATURE_SMA = TEMPERATURE_SMA - TEMPERATURE_SMA/TEMPERATURE_NSAMPLES
    TEMPERATURE_SMA = TEMPERATURE_SMA + measured_temp/TEMPERATURE_NSAMPLES
    audit("CONTROL", "Temperature (SMA)"..string.format("%02.2f",TEMPERATURE_SMA).."C")
    if (TEMPERATURE_SMA > TEMPERATURE_THRESHOLD) then
      fan(1)
    else
      fan(0)
    end
  upload(measured_temp, measured_humi, fan(), light())
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
cron.schedule(MASK_CRON_DHT, control_temperature)
cron.schedule(MASK_CRON_SYNC_CLOCK, sync_clock)

----------------------
-- START WEB SERVER --
----------------------
srv=net.createServer(net.TCP)
srv:listen(80,function(conn)
    conn:on("receive", function(client,request)
      local _, _, method, path, vars = string.find(request, "([A-Z]+) (.+)?(.+) HTTP")
      if(method == nil)then
          _, _, method, path = string.find(request, "([A-Z]+) (.+) HTTP")
      end
      local _GET = {}
      if (vars ~= nil)then
          for k, v in string.gmatch(vars, "(%w+)=(%w+)&*") do
              _GET[k] = v
          end
      end
      audit("WEB SERVER", "receive connection")

      if(_GET.temp ~= nil)then
            TEMPERATURE_THRESHOLD = tonumber(_GET.temp)
      end
      if(_GET.light ~= nil)then
            light(tonumber(_GET.light))
      end
      if(_GET.fan ~= nil)then
            fan(tonumber(_GET.fan))
      end
      local header = {}
      table.insert(header, "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n<!DOCTYPE html>")
      table.insert(header, "<html><head><title>"..NODEID.."</title>")
      table.insert(header, "<link rel=\"shortcut icon\" type=\"image/png\" href=\"https://goo.gl/b1zr7A\"/>")
      table.insert(header, "<link href=\"https://goo.gl/mvSm33\" rel=\"stylesheet\" />")
      table.insert(header, "<link href=\"https://goo.gl/gnD6aH\" rel=\"stylesheet\" />")
      table.insert(header, "<link href=\"https://goo.gl/LTW3E6\" rel=\"stylesheet\" />")
      table.insert(header, "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"/>")
      table.insert(header, "</head><body><div class=\"container\">")
      header = table.concat(header,"")
      client:send(header)
      header = nil
      collectgarbage("collect")
      local sensorData = {}
      -- sensor data
      local temp,temp_dec,humi,humi_dec = tempHum()
      local tempStr = string.format("%d.%02d",temp,temp_dec)
      local humiStr = string.format("%d.%02d%%",humi,humi_dec)
      table.insert(sensorData, "<div class=\"panel panel-primary\">")
      table.insert(sensorData, " <div class=\"panel-heading\">Sensor data</div>")
      table.insert(sensorData, " <div class=\"panel-body\">")
      table.insert(sensorData, "  <div class=\"row\">")
      table.insert(sensorData, "   <label class=\"col-sm-2 text-right\">DHT Temperature &nbsp; <i class=\"wi wi-thermometer-exterior\"></i></label>")
      table.insert(sensorData, "   <div class=\"col-sm-1 text-left\">"..tempStr.."<i class=\"wi wi-celsius\"></i></div>")
      table.insert(sensorData, "  </div>")
      table.insert(sensorData, "  <div class=\"row\">")
      table.insert(sensorData, "    <label class=\"col-sm-2 text-right\">DHT Humidity &nbsp; <i class=\"wi wi-humidity\"></i></label>")
      table.insert(sensorData, "    <div class=\"col-sm-1 text-left\">"..humiStr.."</div>")
      table.insert(sensorData, "  </div>")
      table.insert(sensorData, " </div>")
      table.insert(sensorData, "</div>")
      sensorData = table.concat(sensorData,"")
      client:send(sensorData)
      sensorData = nil
      collectgarbage("collect")
      local calcData = {}
      -- calculate data
      local smaStr = string.format("%02.2f",TEMPERATURE_SMA)
      table.insert(calcData, "<div class=\"panel panel-info\">")
      table.insert(calcData, " <div class=\"panel-heading\">Calculate data</div>")
      table.insert(calcData, " <div class=\"panel-body\">")
      table.insert(calcData, "  <div class=\"row\">")
      table.insert(calcData, "   <label class=\"col-sm-2 text-right\">Temperature (SMA) &nbsp; <i class=\"wi wi-thermometer-exterior\"></i></label>")
      table.insert(calcData, "   <div class=\"col-sm-1 text-left\">"..smaStr.."<i class=\"wi wi-celsius\"></i></div>")
      table.insert(calcData, "  </div>")
      table.insert(calcData, " </div>")
      table.insert(calcData, "</div>")
      calcData = table.concat(calcData,"")
      client:send(calcData)
      calcData = nil
      collectgarbage("collect")
      local manualConf = {}
      -- manual configuration
      local thresholdStr = string.format("%02d",TEMPERATURE_THRESHOLD)
      table.insert(manualConf, "<form>")
      table.insert(manualConf, " <div class=\"panel panel-warning\">")
      table.insert(manualConf, "  <div class=\"panel-heading\">Manual configuration</div>")
      table.insert(manualConf, "  <div class=\"panel-body\">")
      table.insert(manualConf, "   <div class=\"row\">")
      table.insert(manualConf, "    <label class=\"col-sm-2 text-right\">Threshold &nbsp; <i class=\"wi wi-thermometer-exterior\"></i></label>")
      table.insert(manualConf, "    <div class=\"col-sm-2 text-left\">")
      table.insert(manualConf, "     <input type=\"number\" name=\"temp\" min=\"10\" max=\"30\" value=\""..thresholdStr.."\" onchange=\"form.submit()\">")
      table.insert(manualConf, "    <i class=\"wi wi-celsius\"></i></div>")
      table.insert(manualConf, "   </div>")
      table.insert(manualConf, "   <div class=\"row\">")
      table.insert(manualConf, "    <label class=\"col-sm-2 text-right\">Light &nbsp; <i class=\"wi wi-day-sunny\"></i></label>")
      table.insert(manualConf, "    <div class=\"col-sm-2 text-left\">")
      table.insert(manualConf, "     <input type=\"radio\" name=\"light\" value=\"1\" "..(light() == 1 and " checked" or "").." onchange=\"form.submit()\"> On")
      table.insert(manualConf, "     <input type=\"radio\" name=\"light\" value=\"0\" "..(light() == 0 and " checked" or "").." onchange=\"form.submit()\"> Off")
      table.insert(manualConf, "    </div>")
      table.insert(manualConf, "   </div>")
      table.insert(manualConf, "   <div class=\"row\">")
      table.insert(manualConf, "    <label class=\"col-sm-2 text-right\">Fan &nbsp; <i class=\"wi wi-strong-wind\"></i></label>")
      table.insert(manualConf, "    <div class=\"col-sm-2 text-left\">")
      table.insert(manualConf, "     <input type=\"radio\" name=\"fan\" value=\"1\" "..(fan() == 1 and " checked" or "").." onchange=\"form.submit()\"> On")
      table.insert(manualConf, "     <input type=\"radio\" name=\"fan\" value=\"0\" "..(fan() == 0 and " checked" or "").." onchange=\"form.submit()\"> Off")
      table.insert(manualConf, "    </div>")
      table.insert(manualConf, "  </div>")
      table.insert(manualConf, "  </div>")
      table.insert(manualConf, " </div>")
      table.insert(manualConf, "</form>")
      manualConf = table.concat(manualConf,"")
      client:send(manualConf)
      manualConf = nil
      collectgarbage("collect")
      local generalInfo = {}
      -- general information: print cron masks, pins finality, nodemcu ID (put in credentials.lua), etc.
      table.insert(generalInfo, "<div class=\"panel panel-info\">")
      table.insert(generalInfo, " <div class=\"panel-heading\">General information</div>")
      table.insert(generalInfo, " <div class=\"panel-body\">")

      table.insert(generalInfo, "  <div class=\"row\">")
      table.insert(generalInfo, "   <label class=\"col-sm-3 text-right\">Module <i class=\"fa fa-id-card\"></i></label>")
      table.insert(generalInfo, "   <div class=\"col-sm-3 text-left\">"..NODEID.."</div>")
      table.insert(generalInfo, "  </div>")

      table.insert(generalInfo, "  <div class=\"row\">")
      table.insert(generalInfo, "   <label class=\"col-sm-3 text-right\">SSID <i class=\"fa fa-wifi\"></i></label>")
      table.insert(generalInfo, "   <div class=\"col-sm-3 text-left\">"..SSID.."</div>")
      table.insert(generalInfo, "  </div>")

--      table.insert(generalInfo, "  <div class=\"row\">")
--      table.insert(generalInfo, "   <label class=\"col-sm-3 text-right\">NTP <i class=\"fa fa-server\"></i></label>")
--      table.insert(generalInfo, "   <div class=\"col-sm-3 text-left\">"..SERVER_NTP.."</div>")
--      table.insert(generalInfo, "  </div>")

--      table.insert(generalInfo, "  <div class=\"row\">")
--      table.insert(generalInfo, "   <label class=\"col-sm-3 text-right\">Cron Light ON <i class=\"wi wi-day-sunny\"></i></label>")
--      table.insert(generalInfo, "   <div class=\"col-sm-3 text-left\">"..MASK_CRON_LIGHT_ON.."</div>")
--      table.insert(generalInfo, "  </div>")

--      table.insert(bgeneralInfouf, "  <div class=\"row\">")
--      table.insert(generalInfo, "   <label class=\"col-sm-3 text-right\">Cron Light OFF <i class=\"wi wi-night-clear\"></i></label>")
--      table.insert(generalInfo, "   <div class=\"col-sm-3 text-left\">"..MASK_CRON_LIGHT_OFF.."</div>")
--      table.insert(generalInfo, "  </div>")

      table.insert(generalInfo, " </div>")
      table.insert(generalInfo, "</div>")

      table.insert(generalInfo, "</div></body></html>")
      generalInfo = table.concat(generalInfo,"")
      client:send(generalInfo)
      generalInfo = nil
      collectgarbage("collect")
    end)
    conn:on("sent", function (c) c:close() end)
end)
