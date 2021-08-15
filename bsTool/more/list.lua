require "import"
import "android.widget.*"
import "android.content.Context"

about_lay = loadstring("return import \"more/about_lay\"")()

activity.setContentView(loadlayout(about_lay))

activity.actionBar.subtitle = "长按可复制内容"

adapter = ArrayAdapter(activity,android.R.layout.simple_list_item_1)



function main(...)
  local title,items = ...
  activity.setTitle(title)
  for k,v in pairs(items) do
    adapter.add(k .. ": " ..v)
  end
end

list.adapter = adapter

list.onItemLongClick = function(list,v,c,i)
  activity.getSystemService(Context.CLIPBOARD_SERVICE).setText(v.text)
  print("已复制!")
end