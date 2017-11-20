-- Credentials
SSID = "THE SSID"
PASSWORD = "THE PASSWORD"
-- General configurations
NODEID = "X1"
VERBOSE = true
SERVER_NTP="pool.ntp.br"
FMT_TIME="%04d-%02d-%02d %02d:%02d"

DATAREPO = "THE URL"

-- https://crontab.guru/ (nodemcu time is GMT. Sao Paulo time is GMT-2)
MASK_CRON_LIGHT_ON="0 8 * * *"  -- 6AM SP time (LocalTime+2H)
MASK_CRON_LIGHT_OFF="0 20 * * *" -- 6PM SP time (LocalTime+2H)
MASK_CRON_SYNC_CLOCK="0 8 * * 0" -- 6AM SP time on Sundays (LocalTime+2H)
MASK_CRON_DHT="* * * * *"

-- default values
TEMPERATURE_NSAMPLES = 10 -- https://goo.gl/3bLYao
TEMPERATURE_SMA = 25 -- Simple Moving Average Temperature
TEMPERATURE_THRESHOLD = 25 -- above this temperature, fan should be off

PIN_DHT   = 5
PIN_FAN   = 6
PIN_LIGHT = 7
