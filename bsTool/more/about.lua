require "import"
import "android.widget.*"
import "android.content.Context"

about_lay = loadstring("return import \"more/about_lay\"")()

activity.setContentView(loadlayout(about_lay))

activity.setTitle("关于")
activity.actionBar.subtitle = "长按可复制内容"

local abouts = {
  ["作者"] = "Wsdx233",
  ["QQ"] = "1284321744",
  
  ["炸队官网下载"] = "https://files.ballistica.net/bombsquad/builds/",
  ["wsdx的mod源"] = "http://gitee.com/wsdx233/wsdx-bs-mode",
  ["菜猪阴间服地址"] = "47.115.23.140"
}

adapter = ArrayAdapter(activity,android.R.layout.simple_list_item_1)

for k,v in pairs(abouts) do
  adapter.add(k .. ": " ..v)
end

list.adapter = adapter

list.onItemLongClick = function(list,v,c,i)
  activity.getSystemService(Context.CLIPBOARD_SERVICE).setText(v.text)
  print("已复制!")
end