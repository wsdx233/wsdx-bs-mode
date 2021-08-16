require "import"
cjson = require "cjson"
import "android.widget.*"
import "android.view.*"
import "android.app.AlertDialog"
import "java.io.File"

wmlay = import "more/wmlay"

activity.setContentView(wmlay)
activity.getActionBar().subtitle = "Wsdx233的mod源"

mods = {}

link = "https://gitee.com/wsdx233/wsdx-bs-mode/raw/master/"

function gncode(name)
  local cod = ""
  for k,v in ipairs(luajava.astable(String(name).split(""))) do
    cod = cod .. (string.byte(v) or "")
  end
  return cod
end

Http.get(link.."mods.json",function(code,con)
  mods = cjson.decode(con).mods
  data = StringBuilder()
  data.append([[<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Wsdx233 Mods</title>
</head>
<body>]])
  data.append("<h1>Wsdx233的在线mod库</h1><h4>投稿mod请联系wsdx233</h4>")
  for k,v in ipairs(mods) do
    for kf,vf in ipairs(v.files) do
      if File("/sdcard/BombSquad/"..vf).exists() then
        v.has = true
        if not v.path then
          v.path = {}
        end
        table.insert(v.path,"/sdcard/BombSquad/"..vf)
        break
      end
      v.has = false
    end
    v.info = string.gsub(v.info,"%[.-%]",function(str)
      return "<font color=\"#ae"..tostring((string.byte(string.sub(str,#str-1))*433)).."\">"..str.."</font>"
    end)
    data.append("<br>")
    local tag = "<p>"
    tag = tag .. "<b font-size=\"200%\">"..v.name.."</b>" .. "<br>"
    tag = tag .. v.info .. "  作者" ..v.author .. "<br>"
    if not v.has then
      tag = tag .. "<a href=\"down://"..gncode(v.name).."\">【下载⬇️】</a>"
     else
      tag = tag .. "<a href=\"sett://"..gncode(v.name).."\">【管理⚙️】</a>"
    end
    if v.more
      tag = tag .. "<a href=\"info://"..gncode(v.name).."\">【信息ℹ️】</a>"
    end
    tag = tag .. "</p>"
    data.append(tag)
  end
  data.append([[
</body>
</html>
  ]])
  web.loadData(data.toString(),"text/html","utf-8")
  loading.visibility = 8
end)

web.setWebViewClient{
  shouldOverrideUrlLoading=function(view,url)
    --Url即将跳转
    local name = string.sub(url,8)

    local tag = string.sub(url,0,7)

    local mod = nil

    for k,v in ipairs(mods) do
      if gncode(v.name) == name then
        mod = v
        break
      end
    end

    if tag == "down://" then
      local results = {}
      for k,v in ipairs(mod.files) do
        Http.download(link..v,"/sdcard/BombSquad/"..v,function(code,path,head)
          table.insert(results,{path,code,(((code == 200) and "成功") or "失败")})
          local tips = "结果："
          for k,v in ipairs(results) do
            tips = tips .. "\n"..v[1].."  :"..v[3]
          end
          AlertDialog.Builder(activity)
          .setTitle("下载完成")
          .setMessage(tips)
          .setPositiveButton("确定",function()
            activity.recreate()
          end)
          .setCancelable(false)
          .show()
        end)
      end

     elseif tag == "info://" then
     
      AlertDialog.Builder(activity)
      .setTitle("信息")
      .setMessage("详细介绍:\n"..mod.more.minfo.."\n\n适配版本:"..(((mod.more.adjust == 1.4) and "1.4及以下") or ((mod.adjust == 1.5) and "1.5及以上") or "(其他版本)")
      .. "\n\nmod版本:"..mod.more.verson.name
      .."("..mod.more.verson.code..")"
      .."\n更新时间:"
      ..mod.more.verson.time)
      .setPositiveButton("关闭",nil)
      .show()
     elseif tag == "sett://" then
      local items={"删除模组","更新/重下","编辑模组"}
      AlertDialog.Builder(activity)
      .setTitle("管理本地mod")
      .setItems(items,{onClick=function(dialog,index)
          local selectItem=items[index+1]
          local actions = {
            ["删除模组"] = function()
              for key,path in ipairs(mod.path) do
                File(path).delete()
                activity.recreate()
              end
            end;
            ["编辑模组"] = function()
              
            end;
            ["更新/重下"] = function()
              local results = {}
              for k,v in ipairs(mod.files) do
                Http.download(link..v,"/sdcard/BombSquad/"..v,function(code,path,head)
                  table.insert(results,{path,code,(((code == 200) and "成功") or "失败")})
                  local tips = "结果："
                  for k,v in ipairs(results) do
                    tips = tips .. "\n"..v[1].."  :"..v[3]
                  end
                  AlertDialog.Builder(activity)
                  .setTitle("下载完成")
                  .setMessage(tips)
                  .setPositiveButton("确定",function()
                    activity.recreate()
                  end)
                  .setCancelable(false)
                  .show()
                end)
              end
            end

          }
          actions[selectItem]()
      end})
      .setPositiveButton("取消",nil)
      .show()
    end



    return true
  end,
  onPageStarted=function(view,url,favicon)
    --网页加载
  end,
  onPageFinished=function(view,url)
    --网页加载完成
    
    view.goBack()
  end
}