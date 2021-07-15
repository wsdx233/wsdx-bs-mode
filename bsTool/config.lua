local cjson = require "cjson"

local config = {}

config.data = {}

config.save = function()
  --保存配置
  local file = io.open(activity.getLuaDir().."/data/config.json","w")
  file:write(cjson.encode(config.data))
  file:flush()
  file:close()
end

config.load = function()
  --加载配置
  local file = io.open(activity.getLuaDir().."/data/config.json","r")
  config.data = cjson.decode(file:read("*a"))
  file:close()
end

config.tget = function(str)
  local ndata = config.data
  for k,v in ipairs(luajava.astable(String(str).split("/"))) do
    if ndata[v] then
      ndata = ndata[v]
    else
      return nil
    end
  end
  return ndata
end

return config