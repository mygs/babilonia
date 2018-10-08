print("[NODEID] "..node.chipid())
-------- UTILS -------
function publish(value)
  local parms = {}
  table.insert(parms, "id:"..node.chipid())
  table.insert(parms, ";value:"..value)

  if(module.MQTT_STATUS == 0)then
    print("[MQTT] Publishing:")
    MQTTCLIENT:publish("/moi",table.concat(parms,""), 0, 0)	-- publish
  else
    print("[MQTT] Not connected")
  end
end

function moisture()
  local analogic = adc.read(0)
  -- ~ analogic > 500 --- digital = 1
  publish(analogic)
end


----- INIT SETUP -----.
gpio.mode(0, gpio.INPUT)
adc.force_init_mode(adc.INIT_ADC)
cron.schedule(module.MASK_CRON_MOI,  function(e) moisture() end)
print("[SETUP] Completed")
module.BABILONIA_STATUS = 0
