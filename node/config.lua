require("profile")
module = {}

-- profile
module.MODE = profile.MODE
module.SSID = profile.SSID
module.PASSWORD = profile.PASSWORD
module.BABILONIA_SERVER = profile.BABILONIA_SERVER

-- I/O ports
--module.PIN_ANALOGIC_MOISTURE  = 0
module.PIN_SENSORS_SWITCH     = 1  -- fixed at shield
module.PIN_MOISTURE_A         = 2
module.PIN_MOISTURE_B         = 0
module.PIN_MOISTURE_C         = 5
module.PIN_DHT                = 4 -- fixed at shield
module.PIN_FAN                = 6
module.PIN_LIGHT              = 7
module.PIN_PUMP_SOLENOID      = 3

-- default values
module.MQTT_STATUS = 1 -- 0 Connected / 1 = Disconnected
module.SLEEP_TIME = 10 -- seconds
module.SLEEP_TIME_MOISTURE = 5000000 -- 5 seconds
module.SLEEP_TIME_SPRINKLE = 25000000 -- 25 seconds
module.TEMPERATURE_THRESHOLD = 25 -- above this temperature, fan should be off
module.TEMPERATURE_NSAMPLES = 10 -- https://goo.gl/3bLYao
module.TEMPERATURE_SMA = 25 -- Simple Moving Average Temperature
-- https://crontab.guru/ (nodemcu time is GMT. Sao Paulo time is GMT-2)
module.MASK_CRON_LIGHT_ON="0 11 * * *"  -- 9AM SP time (LocalTime+2H)
module.MASK_CRON_LIGHT_OFF="0 20 * * *" -- 6PM SP time (LocalTime+2H)
module.MASK_CRON_CTRL="*/9 * * * *" -- At every 9 minutes

-- overwrite variables
if file.exists("nconfig.lua") then
  dofile("nconfig.lua")
end

-- PRINT VARIABLES
print("WIFI: "..module.SSID)
print("SERVER: "..module.BABILONIA_SERVER)
if (module.MODE == 0) then -- indoor
  print("MODE: INDOOR")
  print("TEMPERATURE_THRESHOLD: "..module.TEMPERATURE_THRESHOLD)
  print("MASK_CRON_LIGHT_ON: "..module.MASK_CRON_LIGHT_ON)
  print("MASK_CRON_LIGHT_OFF: "..module.MASK_CRON_LIGHT_OFF)
else
  print("MODE: OUTDOOR")
  print("SLEEP_TIME_SPRINKLE: "..module.SLEEP_TIME_SPRINKLE)
end
print("SLEEP_TIME_MOISTURE: "..module.SLEEP_TIME_MOISTURE)
print("MASK_CRON_CTRL: "..module.MASK_CRON_CTRL)
