# ba_meta require api 6

#FIX the last stand
#By wsdx233

#NOTICE:If Install this Plugn , player will can't end the laststand.
#So,It can't provide a cheatting to game

#%Info(最终杀敌修改,修改最终杀敌的各项参数,1.5+);

#%Values(RESPAWN,QUICK,NOSLOW);
#%Type(bool,num,bool);
#%Name(无限重生,刷怪倍数,史诗级);
#生成变量相关参数

#%WsdxValues;
#在此处生成Wsdx233_Var赋值语句


from bastd.game.thelaststand import *
import ba
#导入最终杀敌

def end_game_pro(self):
  #修改死亡代码为重生
  for player in self.players :
    self.spawn_player(player)

TheLastStandGame.unprobot = TheLastStandGame._update_bots
def probot(self):
  for i in range(self.QUICK) :
    self.unprobot()

def pro_do_end(self, outcome: str) -> None:
  if outcome == 'defeat':
      self.fade_to_red()
  ba.screenmessage("得分:"+str(self._score)+",但由于修改，您将在之后被记为0分")
  self.end(delay=2.0,
      results={
          'outcome': outcome,
          'score': 0,
          'playerinfos': self.initialplayerinfos
  })
if RESPAWN:
  TheLastStandGame.do_end = pro_do_end

# ba_meta export plugin
class TheLastStandGameFixer(ba.Plugin):
  def on_app_launch(self):
    TheLastStandGame.slow_motion = NOSLOW
    if RESPAWN:
        TheLastStandGame.end_game = end_game_pro
    TheLastStandGame.QUICK = QUICK
    TheLastStandGame._update_bots = probot
    