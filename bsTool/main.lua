require "import"
cjson = require "cjson"
import "android.app.*"
import "android.os.*"
import "android.widget.*"
import "android.view.*"
import "layout"
import "java.io.File"
import "android.graphics.drawable.BitmapDrawable"

--activity.setTitle('AndroLua+')
--activity.setTheme(android.R.style.Theme_Holo_Light)
activity.setContentView(loadlayout(layout))

function getGameInfo()
  --获取游戏信息
  local gameInfo = {}
  local manager = activity.getPackageManager()
  local info = manager.getPackageInfo("net.froemling.bombsquad", 0)
  local icon = info.applicationInfo.loadIcon(manager)
  local version = info.versionName
  local versionCode = info.versionCode
  local bsFile = File("/sdcard/BombSquad/")
  local modFileExists = bsFile.exists()
  local modFileList = luajava.astable(bsFile.list())

  gameInfo.version = version
  gameInfo.versionCode = versionCode
  gameInfo.icon = icon
  gameInfo.modFileExists = modFileExists
  gameInfo.modFileList = modFileList

  return gameInfo
end

function toast(str)
  Toast.makeText(activity,str,Toast.LENGTH_LONG).show()
end


local error,info = pcall(getGameInfo)

local sinfo = table.clone(info)
sinfo.icon = nil
infoFile = io.open(activity.getLuaDir().."/data/gameinfo.json","w")
infoFile:write(cjson.encode(sinfo))
infoFile:flush()
infoFile:close()
--保存读取的数据

fileOld = File("/sdcard/BombSquad/UnlockPro.py")
fileNew = File("/sdcard/BombSquad/UnlockPro_FA.py")
--文件

if not error then
  builder = AlertDialog.Builder(activity)
  builder.setTitle("没有找到炸队")
  builder.setMessage("软件试图获取炸队的版本信息，但是失败了，请检查您的设备上有没有安装炸队。\n错误信息:"..info)
  builder.setPositiveButton("我知道了",nil)
  builder.create().show()
 else
  --bsIcon.imageDrawable = icon
  local infoStr = ""
  infoStr = infoStr.."游戏版本："..info.version.." ("..info.versionCode..")"
  .."\n启用mod："..((info.modFileExists and "是") or "否")
  if info.modFileExists then
    infoStr = infoStr .."\nmod数："..(#info.modFileList)
    .."\n解锁状态："..((fileOld.exists() or fileNew.exists()) and "已解锁" or "未解锁")
  end
  bsInfo.text = infoStr
end

fileOld,fileNew = nil

if not info.modFileExists then
  --mod文件夹不存在
  builder = AlertDialog.Builder(activity)
  builder.setIcon(BitmapDrawable(activity.getLuaDir("icon.png")))
  builder.setTitle("mod未开启")
  builder.setMessage("请前往炸队 设置>高级>显示修改文件夹 开启mod，并给炸队和本软件储存权限")
  builder.setPositiveButton("我知道了",nil)
  builder.setNegativeButton("强行开启",function(p,w)
    File("/sdcard/BombSquad/").mkdir()
    activity.finish()
    activity.newActivity("main")
  end)
  builder.create().show()
end

function pretend(id,color)
  import "android.content.res.ColorStateList"
  local attrsArray = {android.R.attr.selectableItemBackgroundBorderless}
  local typedArray =activity.obtainStyledAttributes(attrsArray)
  ripple=typedArray.getResourceId(0,0)
  Pretend=activity.Resources.getDrawable(ripple)
  Pretend.setColor(ColorStateList(int[0].class{int{}},int{color}))
  id.setBackground(Pretend.setColor(ColorStateList(int[0].class{int{}},int{color})))
end

pretend(l1,0x39000000)
pretend(l2,0x39000000)
pretend(r1,0x39000000)
pretend(r2,0x39000000)
--设置波澜

l1.onClick = function(v)
  --专业版~
  activity.newActivity("unlockPro")
end

l2.onClick = function(v)
  --Wsdx的mod
  activity.newActivity("more/wmod")
end

function onCreateOptionsMenu(menu)
  for k,e in ipairs({"启动游戏","管理模组"})do
    menu.add(e)
  end
end

function onOptionsItemSelected(t)
  t = tostring(t)
  local actions = {
    ["启动游戏"] = function()

    end;
    ["模组管理"] = function()

    end
  }
  actions[t]()
end

bsIcon.onClick = function(v)
  AlertDialog.Builder(activity)
  .setTitle("游戏信息")
  .setMessage(dump(info))
  .setPositiveButton("Done",nil)
  .show()
end

bsIcon.onLongClick = function(v)
  local items={"卸载游戏","更改包名","更改模组路径","转到设置","清除所有mod"}
  AlertDialog.Builder(activity)
  .setTitle("游戏操作")
  .setItems(items,{onClick=function(dialog,index)
      local selectItem=items[index+1]
  end})
  .setPositiveButton("关闭",nil)
  .show()
end

function onResume()
  --返回界面时重读信息
  local error,info = pcall(getGameInfo)

  local sinfo = table.clone(info)
  sinfo.icon = nil
  infoFile = io.open(activity.getLuaDir().."/data/gameinfo.json","w")
  infoFile:write(cjson.encode(sinfo))
  infoFile:flush()
  infoFile:close()
  --保存读取的数据

  fileOld = File("/sdcard/BombSquad/UnlockPro.py")
  fileNew = File("/sdcard/BombSquad/UnlockPro_FA.py")
  --文件

  --bsIcon.imageDrawable = icon
  local infoStr = ""
  infoStr = infoStr.."游戏版本："..info.version.." ("..info.versionCode..")"
  .."\n启用mod："..((info.modFileExists and "是") or "否")
  if info.modFileExists then
    infoStr = infoStr .."\nmod数："..(#info.modFileList)
    .."\n解锁状态："..((fileOld.exists() or fileNew.exists()) and "已解锁" or "未解锁")
  end
  bsInfo.text = infoStr

  fileOld,fileNew = nil
end