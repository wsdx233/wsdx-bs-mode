require "import"
import "android.widget.*"
import "android.view.*"
import "android.app.AlertDialog"
import "java.io.File"
emod_item = loadstring("return import \"more/fix_emod_item\"")()
emod_lay = loadstring("return import \"more/fix_emod_lay\"")()
activity.setContentView(emod_lay)

config = {}
adapter = LuaAdapter(activity,config,emod_item)
list.adapter = adapter


ttypes = {
  bool = {
    able = {"True","False"};
    defaultv = "True";
    str = false;
  };
  num = {
    able = function(v)
      return (tointeger(v))
    end;
    defaultv = "1";
    str = false;
  };
}

function updataUI()
  if File("/sdcard/BombSquad/"..mod.File).exists() then
    --mod文件已存在
    btn_spawn.text = "修改🆕"
    btn_delete.visibility = 0
    btn_delete.text = "删除🗑️"
   else
    --mod文件不存在
    btn_spawn.text = "创建✅"
    btn_delete.visibility = 8
  end
end

function main(...)
  mod = ...

  for k,v in ipairs(luajava.astable(luajava.astable(mod.Values).values)) do
    local key = v
    local name = luajava.astable(mod.Name).values[k]
    local type = luajava.astable(mod.Type).values[k]
    local value = ttypes[type].defaultv
    table.insert(config,{name = name,key = key,type = type,value = value})
  end
  --构建配置表
  activity.setTitle(luajava.astable(mod.Info).values[1])

  --新建列表项目
  updataUI()
end

function btn_delete.onClick(v)
  --删除按钮
  File("/sdcard/BombSquad/"..mod.File).delete()
  updataUI()
end

function btn_spawn.onClick(v)
  --修改/创建按钮

  local builder = StringBuilder()
  for k,v in ipairs(config) do
    if k > 1 then builder.append("\n") end
    local truth_value = ""
    if ttypes[v.type].str then
      truth_value = "\"" .. v.value .. "\""
     else
      truth_value = v.value
    end
    builder.append(v.key .. " = " .. truth_value)
  end
  --构建变量操作

  local var_string = builder.toString()

  local result_content = string.gsub(mod.content,"%#%%WsdxValues%;", var_string)

  local mod_file = io.open("/sdcard/BombSquad/"..mod.File,"w")
  mod_file:write(result_content)
  mod_file:flush()
  mod_file:close()

  print("生成mod成功！重启游戏生效！😛")

  updataUI()
end

function list.onItemClick(l,v,i,c)
  local con = config[c]
  local edit = EditText()
  edit.text = con.value

  if type(ttypes[con.type].able) == "table" then
    --可选择的类型
    local items= ttypes[con.type].able
    AlertDialog.Builder(activity)
    .setTitle(con.name)
    .setItems(items,{onClick=function(dialog,index)
        local selectItem=items[index+1]
        config[c].value = selectItem
        adapter.notifyDataSetChanged()
    end})
    .setPositiveButton("确定",nil)
    .show()

  else

    AlertDialog.Builder(activity)
    .setIcon(android.R.drawable.ic_menu_edit)
    .setTitle(con.name)
    .setView(edit)
    .setNegativeButton("取消",nil)
    .setPositiveButton("确定",{onClick=function(dialog)
        if type(ttypes[con.type].able) == "table" then
          if not (table.find(ttypes[con.type].able,edit.text) ) then
            print("数值拼写错误！请填写以下类型："..dump(ttypes[con.type].able))
            return
          end
         elseif type(ttypes[con.type].able) == "function" then
          if not ttypes[con.type].able(edit.text) then
            print("数值不符合类型！")
            return
          end
        end
        config[c].value = edit.text
    end})
    .show()


  end
end