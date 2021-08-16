# coding=utf-8
import bs
from bsUI import *
import bsUI


class ExecPartyWindow(PartyWindow):
        def _sendChatMessage(self):
                cur_msg = bs.textWidget(query=self._textField)
                if(cur_msg.startswith)('/'):
                    cur_msg = cur_msg.replace("&n","\n")
                    exec(cur_msg[1:])
                else:
                    bsInternal._chatMessage(bs.textWidget(query=self._textField))
                    bs.textWidget(edit=self._textField, text='')
                
class D:
    sent = bsInternal._chatMessage
    sm = bs.screenMessage
    activity = bs.getActivity

class ModCoopWindow(CoopWindow):

    def _updateCornerButtonPositions(self):
        offs = -55 if gSmallUI and bsInternal._isPartyIconVisible() else 0
        if self._powerRankingButtonInstance is not None:
            self._powerRankingButtonInstance.setPosition(
                (self._width-282+offs-self._xInset,
                 self._height-85-(4 if gSmallUI else 0)))
        if self._storeButtonInstance is not None:
            self._storeButtonInstance.setPosition(
                (self._width-170+offs-self._xInset,
                 self._height-85-(4 if gSmallUI else 0)))

    def __init__(self, transition='inRight', originWidget=None):

        bsInternal._setAnalyticsScreen('Coop Window')

        # if they provided an origin-widget, scale up from that
        if originWidget is not None:
            self._transitionOut = 'outScale'
            scaleOrigin = originWidget.getScreenSpaceCenter()
            transition = 'inScale'
        else:
            self._transitionOut = 'outRight'
            scaleOrigin = None

        # try to recreate the same number of buttons we had last time so our
        # re-selection code works
        try:
            self._tournamentButtonCount = bs.getConfig()['Tournament Rows']
        except Exception:
            self._tournamentButtonCount = 0

        #self._enableChallenges = True
        self._enableChallenges = False

        # same for challenges..
        try:
            self._challengeButtonCount = bs.getConfig()[
                'Challenge Button Count']
        except Exception:
            self._challengeButtonCount = 0

        self._width = 1320 if gSmallUI else 1120
        self._xInset = xInset = 100 if gSmallUI else 0
        self._height = 657 if gSmallUI else 730 if gMedUI else 800
        global gMainWindow
        gMainWindow = "Coop Select"
        self._r = 'coopSelectWindow'
        topExtra = 20 if gSmallUI else 0

        self._tourneyDataUpToDate = False

        self._campaignDifficulty = bsInternal._getAccountMiscVal(
            'campaignDifficulty',
            'easy')

        bs.gCreateGameType = None
        self._rootWidget = bs.containerWidget(
            size=(self._width, self._height + topExtra),
            toolbarVisibility='MENU_FULL', scaleOriginStackOffset=scaleOrigin,
            stackOffset=(0, -15) if gSmallUI else(0, 0) if gMedUI else(0, 0),
            transition=transition, scale=1.2
            if gSmallUI else 0.8 if gMedUI else 0.75)

        if gToolbars and gSmallUI:
            self._backButton = None
        else:
            self._backButton = b = bs.buttonWidget(
                parent=self._rootWidget,
                position=(75 + xInset, self._height - 87 -
                          (4 if gSmallUI else 0)),
                size=(120, 60),
                scale=1.2, autoSelect=True, label=bs.Lstr(
                    resource='backText'),
                buttonType='back')

        if not gToolbars:
            prb = self._powerRankingButtonInstance = PowerRankingButton(
                parent=self._rootWidget,
                position=(self._width - (282 + xInset),
                          self._height - 85 - (4 if gSmallUI else 0)),
                size=(100, 60),
                color=(0.4, 0.4, 0.9),
                textColor=(0.9, 0.9, 2.0),
                scale=1.05, onActivateCall=bs.WeakCall(
                    self._switchToPowerRankings))
            self._powerRankingButton = prb.getButtonWidget()

            sb = self._storeButtonInstance = StoreButton(
                parent=self._rootWidget,
                position=(self._width - (170 + xInset),
                          self._height - 85 - (4 if gSmallUI else 0)),
                size=(100, 60),
                color=(0.6, 0.4, 0.7),
                showTickets=True, buttonType='square', saleScale=0.85,
                textColor=(0.9, 0.7, 1.0),
                scale=1.05, onActivateCall=bs.WeakCall(
                    self._switchToStore, showTab=None))
            self._storeButton = sb.getButtonWidget()
            bs.widget(edit=self._backButton,
                      rightWidget=self._powerRankingButton)
            bs.widget(edit=self._powerRankingButton,
                      leftWidget=self._backButton)
        else:
            self._powerRankingButtonInstance = self._storeButtonInstance = \
                self._storeButton = self._powerRankingButton = None

        # move our corner buttons dynamically to keep them out of the way of
        # the party icon :-(
        self._updateCornerButtonPositions()
        self._updateCornerButtonPositionsTimer = bs.Timer(1000, bs.WeakCall(
            self._updateCornerButtonPositions), repeat=True, timeType='real')

        self._lastTournamentQueryTime = None
        self._lastTournamentQueryResponseTime = None
        self._doingTournamentQuery = False

        bsConfig = bs.getConfig()

        try:
            self._selectedCampaignLevel = \
                bsConfig['Selected Coop Campaign Level']
        except Exception:
            self._selectedCampaignLevel = None

        try:
            self._selectedCustomLevel = bsConfig['Selected Coop Custom Level']
        except Exception:
            self._selectedCustomLevel = None

        try:
            self._selectedChallengeLevel = \
                bsConfig['Selected Coop Challenge Level']
        except Exception:
            self._selectedChallengeLevel = None

        # dont want initial construction affecting our last-selected
        self._doSelectionCallbacks = False
        v = self._height - 95
        t = campaignText = bs.textWidget(
            parent=self._rootWidget,
            position=(self._width * 0.5, v + 40 - (0 if gSmallUI else 0)),
            size=(0, 0),
            text=bs.Lstr(
                resource='playModes.singlePlayerCoopText',
                fallbackResource='playModes.coopText'),
            hAlign="center", color=gTitleColor, scale=1.5, maxWidth=500,
            vAlign="center")
        campaignTextV = v

        if gToolbars and gSmallUI:
            bs.textWidget(edit=t, text='')

        if gDoAndroidNav:
            if self._backButton is not None:
                bs.buttonWidget(
                    edit=self._backButton, buttonType='backSmall',
                    size=(60, 50),
                    position=(75+xInset,
                              self._height-87-(4 if gSmallUI else 0)+6),
                    label=bs.getSpecialChar('back'))

        try:
            self._selectedRow = bsConfig['Selected Coop Row']
        except Exception:
            self._selectedRow = None

        self._starTex = bs.getTexture('star')
        self._lsbt = bs.getModel('levelSelectButtonTransparent')
        self._lsbo = bs.getModel('levelSelectButtonOpaque')
        self._aOutlineTex = bs.getTexture('achievementOutline')
        self._aOutlineModel = bs.getModel('achievementOutline')

        self._scrollWidth = self._width-(130+2*xInset)
        self._scrollHeight = self._height - (190
                                             if gSmallUI and gToolbars else 160)

        self._subContainerWidth = 800
        self._subContainerHeight = 1400

        self._scrollWidget = bs.scrollWidget(
            parent=self._rootWidget, highlight=False,
            position=(65 + xInset, 120)
            if gSmallUI and gToolbars else(65 + xInset, 70),
            size=(self._scrollWidth, self._scrollHeight),
            simpleCullingV=10.0)
        self._subContainer = None

        # take note of our account state; we'll refresh later if this changes
        self._accountStateNum = bsInternal._getAccountStateNum()
        # same for fg/bg state..
        self._fgState = bsUtils.gAppFGState

        self._refresh()
        self._restore_state()

        # even though we might display cached tournament data immediately, we
        # don't consider it valid until we've pinged
        # the server for an update
        self._tourneyDataUpToDate = False

        # if we've got a cached tournament list for our account and info for
        # each one of those tournaments,
        # go ahead and display it as a starting point...
        if (gAccountTournamentList is not None
            and gAccountTournamentList[0] == bsInternal._getAccountStateNum()
            and gAccountChallengeList is not None
            and gAccountChallengeList['accountState'] == \
            bsInternal._getAccountStateNum()
            and all([tID in gTournamentInfo
                     for tID in gAccountTournamentList[1]])):
            tourneyData = [gTournamentInfo[tID]
                           for tID in gAccountTournamentList[1]]
            self._updateForData(
                tourneyData, gAccountChallengeList['challenges'])

        # this will pull new data periodically, update timers, etc..
        self._updateTimer = bs.Timer(
            1000, bs.WeakCall(self._update),
            timeType='real', repeat=True)
        self._update()

bsUI.PartyWindow = ExecPartyWindow
bsUI.CoopWindow = ModCoopWindow
bs.realTimer(5000, bs.Call(bsInternal._setPartyIconAlwaysVisible, True))