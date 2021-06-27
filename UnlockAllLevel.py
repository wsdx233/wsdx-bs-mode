# ba_meta require api 6


#Unlock all coop-games ...yes the last stand too ....yipeee

# Level unlock by Mr..Smoothy
# join discord https://discord.gg/ucyaesh

# dont remove ...my credits ...I did very hard work typing these 3 lines.  pressed over 100 keys . burned 10 Cals.   wasted .4 % of my battery
# THIS MOD IS ONLY FOR NOOBS !

import ba
import _ba
from ba import Level
# ba_meta export plugin
class bySmoothy(ba.Plugin):
    def __init__(self):
        if _ba.env().get("build_number",0) >= 20246:
        	unlock()

            
def unlock():
	ba.Level.complete=completed

def completed(self):
	return True
    
