require "import"
import "java.io.File"
import "android.widget.*"

activity.setTitle("修改插件")

items = {}

list = ListView()
activity.setContentView(list)
--列表与适配器

files = luajava.astable(File(activity.getLuaDir().."/fix").list())

mods = {}

for k,v in pairs(files) do
  local fio = io.open(activity.getLuaDir().."/fix/"..v,"r")
  local content = fio:read("*a")
  fio:close()
  
  local metas = {}
  string.gsub(content,"%#%%.-%(.-%);",function(text)
    --注解格式
    --#%注解名(注解内容);
    
    local start = string.find(text,"%(")-1
    local close = string.find(text,"%)")-1
    
    local valuess = string.sub(text,start+2,close)
    local values = luajava.astable(String(valuess).split(","))
    
    metas[string.sub(text,3,start)] = {
      name = string.sub(text,3,start);
      values = values
    }
    
  end)
  metas.File = v
  metas.content = content
  table.insert(mods,metas)
end
--读取文件夹

--print(dump(mods))

for k,v in ipairs(mods) do
  table.insert(items,{
    title = v.Info.values[1];
    desc = v.Info.values[2] .."/".. v.Info.values[3];
  })
end

adapter = SimpleAdapter(
  activity,
  items,
  android.R.layout.simple_list_item_2,
  {"title","desc"},{android.R.id.text1,android.R.id.text2}
)
list.adapter = adapter
adapter.notifyDataSetChanged()
--设置适配器，显示内容

list.onItemClick = function(l,v,c,i)
  activity.newActivity("more/fix_emod",{mods[i+1]})
end