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
--------------------------
--- SENSOR & ACTUATORS ---
--------------------------

-- SENSOR DHT
-- @return temp Temperature (Celsius)
-- @return humi Humidity (Percentage)
function tempHum(silent)
  status, temp, humi, temp_dec, humi_dec = dht.read(PIN_DHT)
  if status == dht.ERROR_CHECKSUM then
    audit("DHT", "Checksum error.")
    return -1,-1,-1,-1
  elseif status == dht.ERROR_TIMEOUT then
    audit("DHT", "Timed out.")
    return -1,-1,-1,-1
--  elseif status == dht.OK then
  end
  audit("DHT", string.format("Temperature: %d.%02dC Humidity: %d.%02d%%",temp,temp_dec,humi,humi_dec))
  return temp,temp_dec,humi,humi_dec
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
  local measured_temp = tempHum()
  if (measured_temp ~= nil) then -- so, filter the value
    TEMPERATURE_SMA = TEMPERATURE_SMA - TEMPERATURE_SMA/TEMPERATURE_NSAMPLES
    TEMPERATURE_SMA = TEMPERATURE_SMA + measured_temp/TEMPERATURE_NSAMPLES
    audit("CONTROL", "Temperature (SMA)"..string.format("%02.2f",TEMPERATURE_SMA).."C")
    if (TEMPERATURE_SMA > TEMPERATURE_THRESHOLD) then
      fan(1)
    else
      fan(0)
    end
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

      local buf = "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n<!DOCTYPE html>"
      buf = buf.."<html><head><title>"..NODEID.."</title>"
      buf = buf.."<link rel=\"shortcut icon\" type=\"image/png\" href=\"https://goo.gl/b1zr7A\"/>"
      buf = buf.."<link href=\"https://goo.gl/mvSm33\" rel=\"stylesheet\" />"
      buf = buf.."<link href=\"https://goo.gl/gnD6aH\" rel=\"stylesheet\" />"
      buf = buf.."<link href=\"https://goo.gl/LTW3E6\" rel=\"stylesheet\" />"
      buf = buf.."<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"/>"
      buf = buf.."</head><body><div class=\"container\">"

      -- sensor data
      local temp,temp_dec,humi,humi_dec = tempHum()
      local tempStr = string.format("%d.%02d",temp,temp_dec)
      local humiStr = string.format("%d.%02d%%",humi,humi_dec)
      buf = buf.."<div class=\"panel panel-primary\">"
      buf = buf.." <div class=\"panel-heading\">Sensor data</div>"
      buf = buf.." <div class=\"panel-body\">"
      buf = buf.."  <div class=\"row\">"
      buf = buf.."   <label class=\"col-sm-2 text-right\">DHT Temperature &nbsp; <i class=\"wi wi-thermometer-exterior\"></i></label>"
      buf = buf.."   <div class=\"col-sm-1 text-left\">"..tempStr.."<i class=\"wi wi-celsius\"></i></div>"
      buf = buf.."  </div>"
      buf = buf.."  <div class=\"row\">"
      buf = buf.."    <label class=\"col-sm-2 text-right\">DHT Humidity &nbsp; <i class=\"wi wi-humidity\"></i></label>"
      buf = buf.."    <div class=\"col-sm-1 text-left\">"..humiStr.."</div>"
      buf = buf.."  </div>"
      buf = buf.." </div>"
      buf = buf.."</div>"
      -- calculate data
      local smaStr = string.format("%02.2f",TEMPERATURE_SMA)
      buf = buf.."<div class=\"panel panel-info\">"
      buf = buf.." <div class=\"panel-heading\">Calculate data</div>"
      buf = buf.." <div class=\"panel-body\">"
      buf = buf.."  <div class=\"row\">"
      buf = buf.."   <label class=\"col-sm-2 text-right\">Temperature (SMA) &nbsp; <i class=\"wi wi-thermometer-exterior\"></i></label>"
      buf = buf.."   <div class=\"col-sm-1 text-left\">"..smaStr.."<i class=\"wi wi-celsius\"></i></div>"
      buf = buf.."  </div>"
      buf = buf.." </div>"
      buf = buf.."</div>"
      -- manual configuration
      local thresholdStr = string.format("%02d",TEMPERATURE_THRESHOLD)
      buf = buf.."<form>"
      buf = buf.." <div class=\"panel panel-warning\">"
      buf = buf.."  <div class=\"panel-heading\">Manual configuration</div>"
      buf = buf.."  <div class=\"panel-body\">"
      buf = buf.."   <div class=\"row\">"
      buf = buf.."    <label class=\"col-sm-2 text-right\">Threshold &nbsp; <i class=\"wi wi-thermometer-exterior\"></i></label>"
      buf = buf.."    <div class=\"col-sm-2 text-left\">"
      buf = buf.."     <input type=\"number\" name=\"temp\" min=\"10\" max=\"30\" value=\""..thresholdStr.."\" onchange=\"form.submit()\">"
      buf = buf.."    <i class=\"wi wi-celsius\"></i></div>"
      buf = buf.."   </div>"
      buf = buf.."   <div class=\"row\">"
      buf = buf.."    <label class=\"col-sm-2 text-right\">Light &nbsp; <i class=\"wi wi-day-sunny\"></i></label>"
      buf = buf.."    <div class=\"col-sm-2 text-left\">"
      buf = buf.."     <input type=\"radio\" name=\"light\" value=\"1\" "..(light() == 1 and " checked" or "").." onchange=\"form.submit()\"> On"
      buf = buf.."     <input type=\"radio\" name=\"light\" value=\"0\" "..(light() == 0 and " checked" or "").." onchange=\"form.submit()\"> Off"
      buf = buf.."    </div>"
      buf = buf.."   </div>"
      buf = buf.."   <div class=\"row\">"
      buf = buf.."    <label class=\"col-sm-2 text-right\">Fan &nbsp; <i class=\"wi wi-strong-wind\"></i></label>"
      buf = buf.."    <div class=\"col-sm-2 text-left\">"
      buf = buf.."     <input type=\"radio\" name=\"fan\" value=\"1\" "..(fan() == 1 and " checked" or "").." onchange=\"form.submit()\"> On"
      buf = buf.."     <input type=\"radio\" name=\"fan\" value=\"0\" "..(fan() == 0 and " checked" or "").." onchange=\"form.submit()\"> Off"
      buf = buf.."    </div>"
      buf = buf.."  </div>"
      buf = buf.." </div>"
      buf = buf.."</form>"
      -- general information: print cron masks, pins finality, nodemcu ID (put in credentials.lua), etc.
      buf = buf.."<div class=\"panel panel-info\">"
      buf = buf.." <div class=\"panel-heading\">General information</div>"
      buf = buf.." <div class=\"panel-body\">"

      buf = buf.."  <div class=\"row\">"
      buf = buf.."   <label class=\"col-sm-3 text-right\">Module <i class=\"fa fa-id-card\"></i></label>"
      buf = buf.."   <div class=\"col-sm-3 text-left\">"..NODEID.."</div>"
      buf = buf.."  </div>"

      buf = buf.."  <div class=\"row\">"
      buf = buf.."   <label class=\"col-sm-3 text-right\">SSID <i class=\"fa fa-wifi\"></i></label>"
      buf = buf.."   <div class=\"col-sm-3 text-left\">"..SSID.."</div>"
      buf = buf.."  </div>"

--      buf = buf.."  <div class=\"row\">"
--      buf = buf.."   <label class=\"col-sm-3 text-right\">NTP <i class=\"fa fa-server\"></i></label>"
--      buf = buf.."   <div class=\"col-sm-3 text-left\">"..SERVER_NTP.."</div>"
--      buf = buf.."  </div>"

--      buf = buf.."  <div class=\"row\">"
--      buf = buf.."   <label class=\"col-sm-3 text-right\">Cron Light ON <i class=\"wi wi-day-sunny\"></i></label>"
--      buf = buf.."   <div class=\"col-sm-3 text-left\">"..MASK_CRON_LIGHT_ON.."</div>"
--      buf = buf.."  </div>"

--      buf = buf.."  <div class=\"row\">"
--      buf = buf.."   <label class=\"col-sm-3 text-right\">Cron Light OFF <i class=\"wi wi-night-clear\"></i></label>"
--      buf = buf.."   <div class=\"col-sm-3 text-left\">"..MASK_CRON_LIGHT_OFF.."</div>"
--      buf = buf.."  </div>"

      buf = buf.." </div>"
      buf = buf.."</div>"

      buf = buf.."</div></body></html>"
      client:send(buf)
    end)
    conn:on("sent", function (c) c:close() end)
end)
