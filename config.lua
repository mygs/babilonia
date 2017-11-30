-- Credentials
SSID = "THE SSID"
PASSWORD = "THE PASSWORD"
-- General configurations
NODEID = "X001"

DATAREPO = "https://script.google.com/macros/s/AKfycbwhkc1vSeszz9JE6DjSwgqpK_mKSXuVm3BK_1VuPqQgeoP5FTg/exec"

-- https://crontab.guru/ (nodemcu time is GMT. Sao Paulo time is GMT-2)
MASK_CRON_LIGHT_ON="0 11 * * *"  -- 9AM SP time (LocalTime+2H)
MASK_CRON_LIGHT_OFF="0 20 * * *" -- 6PM SP time (LocalTime+2H)
MASK_CRON_CTRL="* * * * *" -- At every minute

-- default values
TEMPERATURE_NSAMPLES = 10 -- https://goo.gl/3bLYao
TEMPERATURE_SMA = 25 -- Simple Moving Average Temperature
TEMPERATURE_THRESHOLD = 25 -- above this temperature, fan should be off

PIN_DHT   = 5
PIN_FAN   = 6
PIN_LIGHT = 7

RATIO_CTRL_UPDATE_UPLOAD = 4 -- X/Y: For each X update, execute Y upload
