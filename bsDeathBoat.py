# -*- coding: utf-8 -*-

#by wsdx233
#菜猪比赛专用~


import bs
import random

def bsGetAPIVersion():
    # see bombsquadgame.com/apichanges
    return 4


def bsGetGames():
    return [DeathMatchGame]

class PirateBotPro(bs.PirateBot):
    curseTime = 9000
    defaultShields = False
    defaultBoxingGloves = True

class DeathMatchGame(bs.TeamGameActivity):

    @classmethod
    def getName(cls):
        return '选拔船员'

    @classmethod
    def getDescription(cls, sessionType):
        return '嘘！别被选上！'

    @classmethod
    def supportsSessionType(cls, sessionType):
        return True if(
            issubclass(sessionType, bs.TeamsSession)
            or issubclass(sessionType, bs.FreeForAllSession)) else False

    @classmethod
    def getSupportedMaps(cls, sessionType):
        return bs.getMapsSupportingPlayType("melee")

    @classmethod
    def getSettings(cls, sessionType):
        settings = [
            ("Time Limit",
             {
                 'choices':
                 [
                  ('1 Minute', 60),
                     ('2 Minutes', 120),
                     ('5 Minutes', 300),
                     ('10 Minutes', 600),
                     ('20 Minutes', 1200)],
                 'default': 60}),
            ("Respawn Times",
             {
                 'choices':
                 [('Shorter', 0.25),
                  ('Short', 0.5),
                     ('Normal', 1.0),
                     ('Long', 2.0),
                     ('Longer', 4.0)],
                 'default': 1.0}),
            ("Epic Mode", {'default': True})]

        # In teams mode, a suicide gives a point to the other team, but in
        # free-for-all it subtracts from your own score. By default we clamp
        # this at zero to benefit new players, but pro players might like to
        # be able to go negative. (to avoid a strategy of just
        # suiciding until you get a good drop)

        return settings

    def __init__(self, settings):
        bs.TeamGameActivity.__init__(self, settings)
        if self.settings['Epic Mode']:
            self._isSlowMotion = True

        # print messages when players die since it matters here..
        self.announcePlayerDeaths = True

        self._scoreBoard = bs.ScoreBoard()
    
    def _test(*a):
        bs.screenMessage(str(a))

    def getInstanceDescription(self):
        return ('嘘！别被选上！')

    def getInstanceScoreBoardDescription(self):
        return ('别被选上！逃！')

    def onTransitionIn(self):
        bs.TeamGameActivity.onTransitionIn(
            self, music='Epic' if self.settings['Epic Mode'] else 'ToTheDeath')

    def onTeamJoin(self, team):
        if self.hasBegun():
            return
        team.gameData['score'] = 0
        if self.hasBegun():
            self._updateScoreBoard()
    

    def onPlayerJoin(self, player):
        # don't allow joining after we start
        # (would enable leave/rejoin tomfoolery)
        if self.hasBegun():
            bs.screenMessage(
                bs.Lstr(
                    resource='playerDelayedJoinText',
                    subs=[('${PLAYER}', player.getName(full=True))]),
                color=(0, 1, 0))
            # for score purposes, mark them as having died right as the
            # game started
            return
        self.spawnPlayer(player)

    def onBegin(self):
        bs.TeamGameActivity.onBegin(self)
        self.setupStandardTimeLimit(self.settings['Time Limit'])
        self.setupStandardPowerupDrops()
        
        self._updateScoreBoard()
        self._dingSound = bs.getSound('dingSmall')
        
        
        # spawn some baddies
        self._bots = bs.BotSet()
        
        
        self._bots.spawnBot(PirateBotPro,pos=(-2,5,0), spawnTime=2000)
        
    def _curs(self, game, bot):
        bot.curseTime = 9999

    def handleMessage(self, m):
    
        
        # a spaz-bot has died
        if isinstance(m, bs.SpazBotDeathMessage):
            self._bots.spawnBot(PirateBotPro,pos=(random.randint(-5,5),5,random.randint(-5,5)), spawnTime=4000, onSpawnCall=self._curs)
            if (random.randint(1,100) >= 95 and (len(self._bots.getLivingBots()) < 3))  :
                self._bots.spawnBot(PirateBotPro,pos=(random.randint(-5,5),5,random.randint(-5,5)), spawnTime=4000, onSpawnCall=self._curs)

        if isinstance(m, bs.PlayerSpazDeathMessage):
            bs.TeamGameActivity.handleMessage(
                self, m)  # augment standard behavior

            player = m.spaz.getPlayer()
            
            
            
            
            self.respawnPlayer(player)

            killer = m.killerPlayer
            if killer is None:
                return

            # handle team-kills
            if True:

                # in free-for-all, killing yourself loses you a point
                if isinstance(self.getSession(), bs.FreeForAllSession):
                    newScore = player.getTeam().gameData['score'] - 1
                    if False:
                        newScore = max(0, newScore)
                    player.getTeam().gameData['score'] = newScore

                # in teams-mode it gives a point to the other team
                else:
                    bs.playSound(self._dingSound)
                    for team in self.teams:
                        if team is killer.getTeam():
                            team.gameData['score'] -= 1

            # killing someone on another team nets a kill
            

            self._updateScoreBoard()

            # if someone has won, set a timer to end shortly
            # (allows the dust to clear and draws to occur if deaths are
            # close enough)

        else:
            bs.TeamGameActivity.handleMessage(self, m)

    def _updateScoreBoard(self):
        for team in self.teams:
            self._scoreBoard.setTeamValue(
                team, team.gameData['score'],
                1)
    
    def spawnPlayer(self, player):

        spaz = self.spawnPlayerSpaz(player)

        # lets reconnect this player's controls to this
        # spaz but *without* the ability to attack or pick stuff up
        spaz.connectControlsToPlayer(enablePunch=False,enableBomb=False,enablePickUp=True)

    def endGame(self):
        results = bs.TeamGameResults()
        for t in self.teams:
            results.setTeamScore(t, t.gameData['score'])
        self.end(results=results)
