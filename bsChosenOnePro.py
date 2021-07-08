# -*- coding: utf-8 -*-

#by wsdx233
#菜猪比赛专用~


import bs
import random


def bsGetAPIVersion():
    # see bombsquadgame.com/apichanges
    return 4


def bsGetGames():
    return [ChosenOneGame]


class ChosenOneGame(bs.TeamGameActivity):

    @classmethod
    def getName(cls):
        return '传递诅咒'

    @classmethod
    def getScoreInfo(cls):
        return {'scoreName': 'Time Held'}

    @classmethod
    def getDescription(cls, sessionType):
        return ('被选中将会倒计时走向死亡！.\n'
                '攻击别人传递诅咒给他')

    @classmethod
    def supportsSessionType(cls, sessionType):
        return True if(
            issubclass(sessionType, bs.TeamsSession)
            or issubclass(sessionType, bs.FreeForAllSession)) else False

    @classmethod
    def getSupportedMaps(cls, sessionType):
        return bs.getMapsSupportingPlayType("keepAway")

    @classmethod
    def getSettings(cls, sessionType):
        return [("Chosen One Time", {'minValue': 10, 'default': 30,
                                     'increment': 10}),
                ("Time Limit", {
                    'choices': [('None', 0), ('1 Minute', 60),
                                ('2 Minutes', 120), ('5 Minutes', 300),
                                ('10 Minutes', 600), ('20 Minutes', 1200)],
                    'default':0
                }),
                ("Respawn Times", {
                    'choices': [('Shorter', 0.25), ('Short', 0.5),
                                ('Normal', 1.0), ('Long', 2.0),
                                ('Longer', 4.0)],
                    'default':1.0
                }),
                ("Epic Mode", {'default': False})]

    def __init__(self, settings):
        bs.TeamGameActivity.__init__(self, settings)
        if self.settings['Epic Mode']:
            self._isSlowMotion = True
        self._scoreBoard = bs.ScoreBoard()
        self._chosenOnePlayer = None
        self._swipSound = bs.getSound("swip")
        self._countDownSounds = {10: bs.getSound('announceTen'),
                                 9: bs.getSound('announceNine'),
                                 8: bs.getSound('announceEight'),
                                 7: bs.getSound('announceSeven'),
                                 6: bs.getSound('announceSix'),
                                 5: bs.getSound('announceFive'),
                                 4: bs.getSound('announceFour'),
                                 3: bs.getSound('announceThree'),
                                 2: bs.getSound('announceTwo'),
                                 1: bs.getSound('announceOne')}

    def getInstanceDescription(self):
        return '倒计时结束意味着永远的死亡！'

    def onTransitionIn(self):
        bs.TeamGameActivity.onTransitionIn(
            self, music='Epic' if self.settings['Epic Mode'] else 'Chosen One')

    def onTeamJoin(self, team):
        team.gameData['timeRemaining'] = self.settings["Chosen One Time"]
        self._updateScoreBoard()
        
    def onPlayerJoin(self,player):
        player.gameData['die'] = False
        bs.TeamGameActivity.onPlayerJoin(self, player)

    def onPlayerLeave(self, player):
        bs.TeamGameActivity.onPlayerLeave(self, player)
        
        if self._getChosenOnePlayer() is player:
            self._setChosenOnePlayer(None)

    def onBegin(self):

        # test...
        if not all(player.exists() for player in self.players):
            bs.printError(
                "Nonexistant player in onBegin: " +
                str([str(p) for p in self.players]) + ': we are ' + str(player))

        bs.TeamGameActivity.onBegin(self)
        self.setupStandardTimeLimit(self.settings['Time Limit'])
        self.setupStandardPowerupDrops()
        
        bs.gameTimer(1000, call=self._tick, repeat=True)
        
        self._setChosenOnePlayer(None)

        

    def _getChosenOnePlayer(self):
        if self._chosenOnePlayer is not None and self._chosenOnePlayer.exists():
            return self._chosenOnePlayer
        else:
            return None
    
    def _handleResetCollide(self):
        # if we have a chosen one ignore these
        if self._getChosenOnePlayer() is not None:
            return
        try:
            player = bs.getCollisionInfo(
                "opposingNode").getDelegate().getPlayer()
        except Exception:
            return
        if player is not None and player.isAlive():
            self._setChosenOnePlayer(player)

    def _tick(self):


        # give the chosen one points
        player = self._getChosenOnePlayer()
        
        #bs.screenMessage('!')
        
        if player is not None:

            # this shouldnt happen, but just in case..
            if not player.isAlive():
                pass
            #if False:
                #bs.printError('got dead player as chosen one in _tick')
                #self._setChosenOnePlayer(None)
            else:
            
                scoringTeam = player.getTeam()
                self.scoreSet.playerScored(
                    player, 3, screenMessage=False, display=False)

                scoringTeam.gameData['timeRemaining'] = max(
                    0, scoringTeam.gameData['timeRemaining']-1)

                # show the count over their head
                try:
                    if scoringTeam.gameData['timeRemaining'] > 0:
                        player.actor.setScoreText(
                            str(scoringTeam.gameData['timeRemaining']))
                except Exception:
                    pass

                self._updateScoreBoard()

                # announce numbers we have sounds for
                try:
                    bs.playSound(
                        self._countDownSounds
                        [scoringTeam.gameData['timeRemaining']])
                except Exception:
                    pass

                # winner
                if scoringTeam.gameData['timeRemaining'] <= 0:
                    #self.endGame()

                    player.gameData['die'] = True
                    self.onPlayerLeave(player)

        # player is None
        else:
            # this shouldnt happen, but just in case..
            # (chosen-one player ceasing to exist should trigger onPlayerLeave
            # which resets chosen-one)
            if self._chosenOnePlayer is not None:
                bs.printError('got nonexistant player as chosen one in _tick')
                self._setChosenOnePlayer(None)

    def endGame(self):
        results = bs.TeamGameResults()
        for team in self.teams:
            results.setTeamScore(
                team, team.gameData['timeRemaining'])
        self.end(results=results, announceDelay=0)

    def _setChosenOnePlayer(self, player):
        try:
            for p in self.players:
                p.gameData['chosenLight'] = None
            bs.playSound(self._swipSound)
            
            
            if player == "die":
            	return
            
            
            if player is None or not player.exists():
                #self._flag = bs.Flag(color=(1, 0.9, 0.2),
                #                     position=self._flagSpawnPos,
                #                     touchable=False)
                
                totalp = []
                
                for team in self.teams :
                    for player in team.players :
                        if not player.gameData['die'] :
                             totalp.append(player)
                
                #bs.screenMessage(str(totalp))
                
                if len(totalp) <= 0 :
                    self.endGame()
                    return
                
                self._setChosenOnePlayer(totalp[random.randint(0,len(totalp)-1)])
                
                
                bs.screenMessage(totalp[random.randint(0,len(totalp)-1)])

                
            else:
                if player.actor is not None:
                    self._chosenOnePlayer = player
                    
        except Exception, e:
            import traceback
            print 'EXC in _setChosenOnePlayer'
            traceback.print_exc(e)
            traceback, print_stack()
            bs.screenMessage(str('!'))

    def handleMessage(self, m):
        if isinstance(m, bs.PlayerSpazDeathMessage):
            bs.TeamGameActivity.handleMessage(
                self, m)  # augment standard behavior
            player = m.spaz.getPlayer()
            killerPlayer = m.killerPlayer
            if killerPlayer is self._getChosenOnePlayer():
                self._setChosenOnePlayer(
                    "die" if (player is None or
                             killerPlayer is player)
                    else player)
            if killerPlayer is player :
                scoringTeam = player.getTeam()
                

                
                scoringTeam.gameData['timeRemaining'] = max(
                    0, scoringTeam.gameData['timeRemaining']-5)
                    
                self._updateScoreBoard()
                    
            self.respawnPlayer(player)
        else:
            bs.TeamGameActivity.handleMessage(self, m)

    def _updateScoreBoard(self):
        for team in self.teams:
            self._scoreBoard.setTeamValue(
                team, team.gameData['timeRemaining'],
                (self.settings['Chosen One Time']),
                countdown=True)
