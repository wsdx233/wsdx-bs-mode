# ba_meta require api 6

#by wsdx233:安装文言文语言

import ba
import os
import _ba
import shutil

# ba_meta export plugin
class configSeter(ba.Plugin):
  def on_app_launch(self):
    if os.path.exists("/sdcard/BombSquad/chinese_wyw.json") and (not os.path.exists("/data/data/net.froemling.bombsquad/files/ballistica_files/ba_data/data/languages/chinese_wy