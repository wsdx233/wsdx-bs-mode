# *-* coding:utf8 *-*

import requests
import json
import time

bpath = input('输入炸队模组文件夹路径:')
baselink = 'https://gitee.com/wsdx233/wsdx-bs-mode/raw/master/'

mods = json.loads(
  requests.get(baselink+'mods.json').text
  )['mods']

while True:
  for ind in range(len(mods)) :
    print("\n")
    mod = mods[ind]
    print("["+str(ind)+"]"+mod['name']+" "*2+"by "+mod['author'])
    print(mod['info'])
  
  num = input('安装序号(exit退出):')
  
  if num == 'exit':
    break
  
  dmod = mods[int(num)]
  
  for fname in dmod['files'] :
    if not bpath.endswith('/') :
      bpath = bpath + '/'
    with open(bpath+fname,'w') as f:
      f.write(requests.get(baselink+fname).text)
      print(bpath+fname+"已安装")
  
  print('\n模组 '+dmod['name']+' 安装完成!五秒后返回模组列表！')
  time.sleep(5)
  