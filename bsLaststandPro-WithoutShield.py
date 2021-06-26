import bs;
from bsTheLastStand import *;
import random;

def onbe(self):
        self._isSlowMotion = False
        bs.CoopGameActivity.onBegin(self)
        # spit out a few powerups and start dropping more shortly
        self._dropPowerups(standardPoints=True)
        bs.gameTimer(2000,bs.WeakCall(self._startPowerupDrops))
        bs.gameTimer(1,bs.WeakCall(self._startBotUpdates))
        self.setupLowLifeWarningSound()
        self._updateScores()
        self._bots = bs.BotSet()
        self._dingSound = bs.getSound('dingSmall')
        self._dingSoundHigh = bs.getSound('dingSmallHigh')
        # our TNT spawner (if applicable)
        self._tntSpawner = bs.TNTSpawner(position=self._tntSpawnPosition,respawnTime=10000)

def _bot(self):
        self._botUpdateInterval = 3300 - 300*(len(self.players))
        self._updateBots()
        self._updateBots()
        self._updateBots()
        self._updateBots()
        self._updateBots()
        self._updateBots()
        if len(self.players) > 2:
            self._updateBots()
        if len(self.players) > 3:
            self._updateBots()
        self._botUpdateTimer = bs.Timer(
            int(self._botUpdateInterval),
            bs.WeakCall(self._updateBots))

def _botup(self):
        self._botSpawnTypes = {
        bs.BomberBot:               [0.1,  0.7,  0.2],
        bs.BomberBotPro:            [0.1,  0.05, 0.001],
        #bs.BomberBotProShielded:    [0.2,  0.02, 0.002],
        bs.ToughGuyBot:             [0.2,  0.0,  0.0],
        bs.ToughGuyBotPro:          [0.2,  0.05, 0.1],
        #bs.ToughGuyBotProShielded:  [0.3,  0.02, 0.4],
        bs.ChickBot:                [0.3,  0.0,  0.0],
        bs.ChickBotPro:             [0.2,  0.05, 0.001],
        #bs.ChickBotProShielded:     [0.8,  0.02, 0.002],
        bs.NinjaBot:                [0.1,  0.05, 0.0],
        bs.MelBot:                  [0.1,  0.6, 0.3],
        bs.PirateBot:               [0.3, 0.2, 0.1],
        #bs.NinjaBotProShielded:      [0.3, 0.01, 0.2]
        }
        self._excludePowerups = ['tripleBombs','iceBombs','impactBombs','landMines','stickyBombs','curse'];
        self._botUpdateInterval = max(random.randint(1000,2000), 1000)
        self._botUpdateTimer = bs.Timer(
            int(self._botUpdateInterval),
            bs.WeakCall(self._updateBots))

        botSpawnPoints = [[-5, 5.5, -4.14], [0, 5.5, -4.14], [5, 5.5, -4.14]]
        dists = [0, 0, 0]
        playerPts = []
        for player in self.players:
            try:
                if player.isAlive():
                    playerPts.append(player.actor.node.position)
            except Exception as e:
                print 'EXC in _updateBots', e
        for i in range(3):
            for p in playerPts:
                dists[i] += abs(p[0]-botSpawnPoints[i][0])
            # little random variation
            dists[i] += random.random() * 5.0
        if dists[0] > dists[1] and dists[0] > dists[2]:
            pt = botSpawnPoints[0]
        elif dists[1] > dists[2]:
            pt = botSpawnPoints[1]
        else:
            pt = botSpawnPoints[2]

        pt = (pt[0]+3.0*(random.random()-0.5),
              pt[1], 2.0*(random.random()-0.5)+pt[2])

        # normalize our bot type total and find a random number within that
        total = 0.0
        for t in self._botSpawnTypes.items():
            total += t[1][0]
        r = random.random()*total

        # now go back through and see where this value falls
        total = 0
        for t in self._botSpawnTypes.items():
            total += t[1][0]
            if r <= total:
                spazType = t[0]
                break

        spawnTime = 1000
        count = 1
        while(count < random.randint(2,5)):
            spazType = t[0]
            spawnTime += 500
            pt = (pt[0]+1.2*(random.random()-0.3),pt[1], 1.5*(random.random()-0.3)+pt[2])
            self._bots.spawnBot(spazType, pos=pt, spawnTime=spawnTime)
            count += 1
            for t in self._botSpawnTypes.items():
                total += t[1][0]
                r = random.random()*total
                # now go back through and see where this value falls
            total = 0
            for t in self._botSpawnTypes.items():
                total += t[1][0]
                if r <= total:
                    spazType = t[0]
                    break


        # after every spawn we adjust our ratios slightly to get more
        # difficult..
        for t in self._botSpawnTypes.items():
            t[1][0] += t[1][1]  # increase spawn rate
            t[1][1] += t[1][2]  # increase spawn rate increase rate

def spawnPlayers(self, player):
        pos = (
            self._spawnCenter[0] + random.uniform(-1.5, 1.5),
            self._spawnCenter[1],
            self._spawnCenter[2] + random.uniform(-1.5, 1.5))
        spaz = self.spawnPlayerSpaz(player, position=pos)
        spaz.connectControlsToPlayer(enableBomb=False)

def end(self, outcome):
	    
        if outcome == 'defeat':
            self.fadeToRed()
        self.end(
            delay=2000,
            results={'outcome': outcome, 'score': self._score.get()/5,
                     'playerInfo': self.initialPlayerInfo})
#TheLastStandGame.onBegin = onbe;
bs.PirateBot.startCursed = False
bs.BomberBotProShielded.defaultBombType = 'ice'
bs.BomberBotPro.defaultBombType = 'tnt'
bs.BomberBot.defaultBombType = 'tnt'
TheLastStandGame._updateBots = _botup;
TheLastStandGame.spawnPlayer = spawnPlayers;
TheLastStandGame.doEnd = end;