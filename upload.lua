local measured_temp, measured_humid, status_fan, status_light = ...
local parms = {}
table.insert(parms, DATAREPO)
table.insert(parms, "?tag="..NODEID.."&ct="..TEMPERATURE_SMA)
table.insert(parms, "&mt="..measured_temp.."&mh="..measured_humid)
table.insert(parms, "&sf="..status_fan.."&sl="..status_light)
parms = table.concat(parms,"")
print("URLX >>> "..parms)
http.get(parms, nil, function(code, data)
    if (code < 0) then
      audit("UPLOAD","HTTPS request failed")
    else
      --print(code, data)
      audit("UPLOAD","HTTPS request success")
    end
  end)
