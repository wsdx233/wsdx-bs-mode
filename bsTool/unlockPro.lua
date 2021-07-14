require "import"
import "android.widget.*"
import "android.view.*"
import "unlockLayout"
import "java.io.File"

activity.setContentView(loadlayout(unlockLayout))


modOld = io.open(activity.getLuaDir().."/mods/UnlockPro.py","r"):read("*a")
modNew = io.open(activity.getLuaDir().."/mods/UnlockPro_FA.py","r"):read("*a")
--读取mod

fileOld = File("/sdcard/BombSquad/UnlockPro.py")
fileNew = File("/sdcard/BombSquad/UnlockPro_FA.py")
--文件

if fileOld.exists() or fileNew.exists() then
  swit.setChecked(true)
end

swit.setOnCheckedChangeListener(
  function(v,c)
  if c then
    --v.text = "开启/ON"
    setUp()
  else
    --v.text = "关闭/OFF"
    unSetUp()
  end
end)

function onCreateOptionsMenu(menu)
  tab = {"关于","反馈","设置"}
  for k,v in ipairs(tab) do
    menu.add(v)
  end
end

function onOptionsItemSelected(str)
  tab = {
    ["关于"] = function()
      
    end;
    ["反馈"] = function()
      
    end;
    ["设置"] = function()
      
    end
  }

  tab[tostring(str)]()
end




function setUp()
  --安装
  
  
  if not fileOld.exists() then
    fileOld.createNewFile()
    local fileOldLua = io.open(fileOld.getPath(),"w")
    fileOldLua:write(modOld)
    fileOldLua:flush()
    fileOldLua:close()
  end

  if not fileNew.exists() then
    fileNew.createNewFile()
    local fileNewLua = io.open(fileNew.getPath(),"w")
    fileNewLua:write(modNew)
    fileNewLua:flush()
    fileNewLua:close()
  end

  
  
  
  
end

function unSetUp()
  --安装
  
  
  if fileOld.exists() then
    fileOld.delete()
  end

  if fileNew.exists() then
    fileNew.delete()
  end

end