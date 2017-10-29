----------------------
----- VARIABLES ------
----------------------
SERVER_NTP="pool.ntp.br"
PIN_DHT, PIN_FAN, PIN_LIGHT = 5, 6, 7
MASK_CRON_LIGHT_ON="0 8 * * *"  -- 6AM SP time (LocalTime+2H)
MASK_CRON_LIGHT_OFF="0 0 * * *" -- 10PM SP time (LocalTime+2H)
MASK_CRON_DHT="*/5 * * * *" -- every 5 minutes
FMT_TIME="%04d-%02d-%02d %02d:%02d"

----------------------
-------- UTILS -------
----------------------

-- CONSOLE AUDIT
-- @param func Function name
-- @param info Additional information
-- @return Console log audit
function audit(func, info)
  local log=""
  local tm = rtctime.epoch2cal(rtctime.get())
  log=string.format(FMT_TIME, tm["year"], tm["mon"], tm["day"], tm["hour"], tm["min"])
  print(log.." ["..func.."] "..info)
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
function tempHum()
  local buf = ""
  status, temp, humi, temp_dec, humi_dec = dht.read(PIN_DHT)
  if status == dht.ERROR_CHECKSUM then
    buf = "Checksum error."
    audit("DHT", buf)
    return buf,buf
  elseif status == dht.ERROR_TIMEOUT then
    buf = "Timed out."
    audit("DHT", buf)
    return buf,buf
--  elseif status == dht.OK then
  end
  buf = "Temperature:"..temp.."C ".."Humidity:"..humi.."%"
  audit("DHT", buf)
  return temp, humi
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
function fan(switch) --
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
gpio.mode(PIN_FAN, gpio.OUTPUT)
gpio.mode(PIN_LIGHT, gpio.OUTPUT)
sync_clock()
light(0)
fan(0)
-- nodemcu time is GMT. Sao Paulo time is GMT-2
--cron.schedule(MASK_CRON_LIGHT_ON, light(1))
--cron.schedule(MASK_CRON_LIGHT_OFF, light(0))
--cron.schedule(MASK_CRON_DHT, tempHum())
--cron.schedule(MASK_CRON_LIGHT_OFF, sync_clock()) -- sporadically sync clock

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

      if(_GET.light == "1")then
            light(1)
      elseif(_GET.light == "0")then
            light(0)
      end

      if(_GET.fan == "1")then
            fan(1)
      elseif(_GET.fan == "0")then
            fan(0)
      end
      local buf = "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n<!DOCTYPE html>"
      buf = buf.."<html><head><title>babilonia v0.0.1</title>"
      buf = buf.."<link rel=\"shortcut icon\" type=\"image/png\" href=\"https://goo.gl/b1zr7A\"/></head>"
      buf = buf.."<body>"
      local tempx, humix = tempHum()
      buf = buf.."<b>DHT</b>: Temperature:"..tempx.."C  ".."Humidity:"..humix.."%"
      buf = buf.."<br /><form>"
      buf = buf.."<label><b>LIGHT</b>:<label>"
      buf = buf.."  <input type=\"radio\" name=\"light\" value=\"1\" "..(light() == 1 and " checked" or "").." onchange=\"form.submit()\"> On"
      buf = buf.."  <input type=\"radio\" name=\"light\" value=\"0\" "..(light() == 0 and " checked" or "").." onchange=\"form.submit()\"> Off"
      buf = buf.."<br />"
      buf = buf.."<label><b>FAN</b>:<label>"
      buf = buf.."  <input type=\"radio\" name=\"fan\" value=\"1\" "..(fan() == 1 and " checked" or "").." onchange=\"form.submit()\"> On"
      buf = buf.."  <input type=\"radio\" name=\"fan\" value=\"0\" "..(fan() == 0 and " checked" or "").." onchange=\"form.submit()\"> Off"
      buf = buf.."</form></body></html>"
      client:send(buf)
    end)
    conn:on("sent", function (c) c:close() end)
end)
--  dofile("apps.lua")
