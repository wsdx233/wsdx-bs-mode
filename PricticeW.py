# ba_meta require api 6

from __future__ import annotations



import ba
from bastd.actor.spazbot import *
import random

class NBSpaz(SpazBot):
  static = True
  default_bomb_count = 0
  color = (1,1,1)
  highlight = (1,1,1)
  
  def handlemessage(self,msg):
    if isinstance(msg, ba.DieMessage):
      if msg.how == "out_of_bounds":
        super().handlemessage(msg)
        #如果掉出场地则死亡否则回血
      
      self.hitpoints = self.hitpoints_max
      return None
    else:
      self._punch_cooldown = 100000
      super().handlemessage(msg)

# ba_meta export game
class Exercise(ba.TeamGameActivity):

	name = '沙袋'
	description = '打沙袋.'
	# Print messages when players die since it matters here.
	announce_player_deaths = True

	@classmethod
	def get_available_settings(
			cls, sessiontype: Type[ba.Session]) -> List[ba.Setting]:
		settings = [
			ba.BoolSetting('Epic Mode', default=False),
			ba.BoolSetting('boxing_gloves', default=False),
			ba.IntSetting(
               'spaz_count',
                min_value=1,
                default=1,
                increment=1
			)
		]
		return settings

	@classmethod
	def supports_session_type(cls, sessiontype: Type[ba.Session]) -> bool:
		return (issubclass(sessiontype, ba.DualTeamSession)
				or issubclass(sessiontype, ba.FreeForAllSession))

	@classmethod
	def get_supported_maps(cls, sessiontype: Type[ba.Session]) -> List[str]:
		maps = ba.getmaps('melee')
		return maps

	def __init__(self, settings: dict):
		super().__init__(settings)
		self._epic_mode = bool(settings['Epic Mode'])
		self._bot = SpazBotSet()
		self.slow_motion = self._epic_mode
		self.msettings = settings
		
	def on_begin(self):
		super().on_begin()
		for k in range(self.msettings["spaz_count"]):
			self._bot.spawn_bot(NBSpaz,(random.randint(-2,2),8,random.randint(-2,2)),0)

		if self.msettings["boxing_gloves"] :
			for player in self.players :
				player.actor.equip_boxing_gloves()

	def get_instance_description(self) -> Union[str, Sequence]:
		return '打“沙袋” by wsdx233。'

	def get_instance_description_short(self) -> Union[str, Sequence]:
		return '打“沙袋”。'
	
	