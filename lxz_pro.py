from bsMeteorShower import *;

def onBegin(self):
        self._isSlowMotion = True
        
        bs.TeamGameActivity.onBegin(self)
        
        bs.screenMessage("woooo-wsdx")

        # drop a wave every few seconds.. and every so often drop the time
        # between waves ..lets have things increase faster if we have fewer
        # players
        self._meteorTime = 2000
        t = 5000 if len(self.players) > 2 else 2500
        if self.settings['Epic Mode']:
            t /= 4
        bs.gameTimer(t, self._decrementMeteorTime, repeat=True)

        # kick off the first wave in a few seconds
        t = 3000
        if self.settings['Epic Mode']:
            t /= 4
        bs.gameTimer(t, self._setMeteorTimer)

        self._timer = bs.OnScreenTimer()
        self._timer.start()
        
        # check for immediate end (if we've only got 1 player, etc)
        bs.gameTimer(5000, self._checkEndGame)
def handleMessage(self, m):

        if isinstance(m, bs.PlayerSpazDeathMessage):

            bs.TeamGameActivity.handleMessage(
                self, m)  # (augment standard behavior)

            deathTime = bs.getGameTime()

            # record the player's moment of death
            self.spawnPlayer(m.spaz.getPlayer())
            m.spaz.getPlayer().gameData['deathTime'] = deathTime

            # in co-op mode, end the game the instant everyone dies
            # (more accurate looking)
            # in teams/ffa, allow a one-second fudge-factor so we can
            # get more draws
            if isinstance(self.getSession(), bs.CoopSession):
                # teams will still show up if we check now.. check in
                # the next cycle
                # also record this for a final setting of the clock..
                self._lastPlayerDeathTime = deathTime
            else:
                bs.gameTimer(1000, self._checkEndGame)

        else:
            # default handler:
            bs.TeamGameActivity.handleMessage(self, m)

def spawnPlayer(self, player):

        spaz = self.spawnPlayerSpaz(player)


        # also lets have them make some noise when they die..
        spaz.playBigDeathSound = True

def onPlayerJoin(self, player):
        # don't allow joining after we start
        # (would enable leave/rejoin tomfoolery)
        self.spawnPlayer(player)

MeteorShowerGame.onBegin = onBegin;
MeteorShowerGame.spawnPlayer = spawnPlayer;
MeteorShowerGame.handleMessage = handleMessage;
MeteorShowerGame.onPlayerJoin = onPlayerJoin;