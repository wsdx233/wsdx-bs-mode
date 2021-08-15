# coding=utf-8
import bs
import datetime
import bsInternal
from bsUI import *
import bsUI
import os,sys
import shutil

import threading
import weakref
import json
import urllib2
import urllib

originalWatchWindow = bsUI.WatchWindow

SystemEncode = sys.getfilesystemencoding()
if not isinstance(SystemEncode,(unicode,str)):
        SystemEncode = "utf-8"
#print(bs.getEnvironment().get("buildNumber",0))
#print("Brp_helper running,system encoding '%s'"%SystemEncode)

def _createTabButtons(parentWidget,tabs,pos,size,onSelectCall=None,returnExtraInfo=False):

        tabPosV = pos[1]
        tabButtons = {}
        tabButtonsIndexed = []
        tabButtonWidth = float(size[0])/len(tabs)

        # add a bit more visual spacing as our buttons get narrower
        tabSpacing = (250.0-tabButtonWidth)*0.6

        positions = []
        sizes = []

        h = pos[0]
        for i,tab in enumerate(tabs):
                def _tickAndCall(call):
                        bs.playSound(bs.getSound('click01'))
                        onSelectCall(call)

                pos = (h+tabSpacing*0.5,tabPosV)
                size = (tabButtonWidth-tabSpacing,50.0)
                positions.append(pos)
                sizes.append(size)
                b = bs.buttonWidget(parent=parentWidget,position=pos,autoSelect=True,
                                          buttonType='tab',size=size,label=tab[1],enableSound=False,
                                          onActivateCall=bs.Call(_tickAndCall,tab[0]))                h += tabButtonWidth
                tabButtons[tab[0]] = b
                tabButtonsIndexed.append(b)        if returnExtraInfo: return {'buttons':tabButtons,'buttonsIndexed':tabButtonsIndexed,'positions':positions,'sizes':sizes}
        else: return tabButtons

def _updateTabButtonColors(tabs,selectedTab):
        for tId,tButton in tabs.items():
                if tId == selectedTab: bs.buttonWidget(edit=tButton,color=(0.5,0.4,0.93),textColor=(0.85,0.75,0.95)) # lit
                else: bs.buttonWidget(edit=tButton,color=(0.52,0.48,0.63),textColor=(0.65,0.6,0.7)) # unlit

class ExWatchWindow(WatchWindow):
        def __init__(self,transition='inRight',originWidget=None):

                bsInternal._setAnalyticsScreen('Watch Window')

                if originWidget is not None:
                        self._transitionOut = 'outScale'
                        scaleOrigin = originWidget.getScreenSpaceCenter()
                        transition = 'inScale'
                else:
                        self._transitionOut = 'outRight'
                        scaleOrigin = None

                global gMainWindow
                gMainWindow = "Watch"

                self._r = 'watchWindow'

                self._width = 1240 if gSmallUI else 1040
                xInset = 100 if gSmallUI else 0
                self._height = 578 if gSmallUI else 670 if gMedUI else 800
                self._current_tab = None
                extraTop = 20 if gSmallUI else 0

                self._rootWidget = bs.containerWidget(size=(self._width,self._height+extraTop),transition=transition,
 toolbarVisibility='MENU_MINIMAL',
 scaleOriginStackOffset=scaleOrigin,
 scale=1.3 if gSmallUI else 0.97 if gMedUI else 0.8,
 stackOffset=(0,-10) if gSmallUI else (0,15) if gMedUI else (0,0))

                if gSmallUI and gToolbars:
                        bs.containerWidget(edit=self._rootWidget,onCancelCall=self._back)
                        self._backButton = None
                else:
                        self._backButton = backButton = b = bs.buttonWidget(parent=self._rootWidget,autoSelect=True,position=(70+xInset,self._height-74),
                                          size=(140,60),scale=1.1,label=bs.Lstr(resource='backText'),
                                          buttonType='back', onActivateCall=self._back)
                        bs.containerWidget(edit=self._rootWidget,cancelButton=b)
                        if gDoAndroidNav:
                                bs.buttonWidget(edit=b,buttonType='backSmall',size=(60,60),label=bs.getSpecialChar('back'))
                                # bs.textWidget(edit=t,hAlign='left',position=(155,self._height - 40))

                t = bs.textWidget(parent=self._rootWidget,position=(self._width*0.5,self._height-38),size=(0,0),
 color=gTitleColor,scale=1.5,hAlign="center",vAlign="center",
 text=bs.Lstr(resource=self._r+'.titleText'),
 maxWidth=400)


                tabsDef = [['myReplays',bs.Lstr(resource=self._r+'.myReplaysText')],['outReplays','Out Replays']]

                scrollBufferH = 130 + 2*xInset
                tabBufferH = 750 + 2*xInset
                self._tab_buttons = _createTabButtons(self._rootWidget,tabsDef,pos=(tabBufferH*0.5,self._height - 130),
size=(self._width-tabBufferH,50),onSelectCall=self._setTab)

                if gToolbars:
                        bs.widget(edit=self._tab_buttons[tabsDef[-1][0]],rightWidget=bsInternal._getSpecialWidget('partyButton'))                        if gSmallUI:
                                bb = bsInternal._getSpecialWidget('backButton')
                                bs.widget(edit=self._tab_buttons[tabsDef[0][0]],upWidget=bb,leftWidget=bb)

                self._scrollWidth = self._width-scrollBufferH
                self._scrollHeight = self._height-180

                # not actually using a scroll widget anymore; just an image
                scrollLeft = (self._width-self._scrollWidth)*0.5
                scrollBottom = self._height-self._scrollHeight-79-48
                bufferH = 10
                bufferV = 4
                bs.imageWidget(parent=self._rootWidget,position=(scrollLeft-bufferH,scrollBottom-bufferV),size=(self._scrollWidth+2*bufferH,self._scrollHeight+2*bufferV),
texture=bs.getTexture('scrollWidget'),modelTransparent=bs.getModel('softEdgeOutside'))                self._tabContainer = None

                self._restore_state()
        def _setTab(self, tab):

                if self._current_tab == tab: return
                self._current_tab = tab

                # we wanna preserve our current tab between runs
                bs.getConfig()['Watch Tab'] = tab
                bs.writeConfig()

                # update tab colors based on which is selected
                bsUI._updateTabButtonColors(self._tab_buttons, tab)

                if self._tabContainer is not None and self._tabContainer.exists():
                        self._tabContainer.delete()
                scrollLeft = (self._width - self._scrollWidth) * 0.5
                scrollBottom = self._height - self._scrollHeight - 79 - 48

                # a place where tabs can store data to get cleared when switching to a different tab
                self._tabData = {}

                def _simpleMessage(message, stringHeight):
                        msgScale = 1.1
                        cWidth = self._scrollWidth
                        cHeight = min(self._scrollHeight, stringHeight * msgScale + 100)
                        self._tabContainer = c = bs.containerWidget(parent=self._rootWidget,
                                          position=(scrollLeft,
 scrollBottom + (self._scrollHeight - cHeight) * 0.5),
                                          size=(cWidth, cHeight), background=False, selectable=False)
                        bs.widget(edit=c, upWidget=self._tab_buttons[tab])

                        t = bs.textWidget(parent=c, position=(cWidth * 0.5, cHeight * 0.5), color=(0.6, 1.0, 0.6), scale=msgScale,
 size=(0, 0), maxWidth=cWidth * 0.9, maxHeight=cHeight * 0.9,
 hAlign='center', vAlign='center',
 text=message)

                if tab == 'myReplays':
                        cWidth = self._scrollWidth
                        cHeight = self._scrollHeight - 20
                        subScrollHeight = cHeight - 63
                        self._myReplaysScrollWidth = subScrollWidth = (680 if gSmallUI else 640)

                        self._tabContainer = c = bs.containerWidget(parent=self._rootWidget,
                                          position=(scrollLeft,
 scrollBottom + (self._scrollHeight - cHeight) * 0.5),
                                          size=(cWidth, cHeight), background=False,
                                          selectionLoopToParent=True)

                        v = cHeight - 30
                        t = bs.textWidget(parent=c, position=(cWidth * 0.5, v), color=(0.6, 1.0, 0.6), scale=0.7,
 size=(0, 0),
 maxWidth=cWidth * 0.9,
 hAlign='center', vAlign='center',
 text=bs.Lstr(resource='replayRenameWarningText',
  subs=[('${REPLAY}', bs.Lstr(resource='replayNameDefaultText'))]))

                        bWidth = 140 if gSmallUI else 178
                        bHeight = 80 if gSmallUI else 106 if gMedUI else 139
                        bSpaceExtra = 0 if gSmallUI else -2 if gMedUI else -5

                        bColor = (0.6, 0.53, 0.63)
                        bTextColor = (0.75, 0.7, 0.8)
                        bv = cHeight - (48 if gSmallUI else 45 if gMedUI else 40) - bHeight
                        bh = 40 if gSmallUI else 40
                        sh = 190 if gSmallUI else 225
                        ts = 1.0 if gSmallUI else 1.2
                        self._myReplaysWatchReplayButton = b1 = bs.buttonWidget(parent=c, size=(bWidth, bHeight), position=(bh, bv),
                                          buttonType='square', color=bColor,
                                          textColor=bTextColor,
                                          onActivateCall=self._onMyReplayPlayPress,
                                          textScale=ts,
                                          label=bs.Lstr(
                                          resource=self._r + '.watchReplayButtonText'),
                                          autoSelect=True)
                        bs.widget(edit=b1, upWidget=self._tab_buttons[tab])
                        if gSmallUI and gToolbars:
                                bs.widget(edit=b1, leftWidget=bsInternal._getSpecialWidget('backButton'))
                        bv -= bHeight + bSpaceExtra
                        b2 = bs.buttonWidget(parent=c, size=(bWidth, bHeight), position=(bh, bv),
buttonType='square', color=bColor, textColor=bTextColor,
onActivateCall=self._onMyReplayRenamePress, textScale=ts,
label=bs.Lstr(resource=self._r + '.renameReplayButtonText'),
autoSelect=True)
                        bv -= bHeight + bSpaceExtra
                        b3 = bs.buttonWidget(parent=c, size=(bWidth, bHeight), position=(bh, bv),
buttonType='square', color=bColor, textColor=bTextColor,
onActivateCall=self._onMyReplayDeletePress, textScale=ts,
label=bs.Lstr(resource=self._r + '.deleteReplayButtonText'),
autoSelect=True)
                        bv -= bHeight + bSpaceExtra
                        b4 = bs.buttonWidget(parent=c, size=(bWidth, bHeight), position=(bh, bv),
buttonType='square', color=bColor, textColor=bTextColor,
onActivateCall=self._onMyReplayExportPress, textScale=ts,
label=u'导出\n回放',
autoSelect=True)

                        v -= subScrollHeight + 23
                        self._scrollWidget = sw = bs.scrollWidget(parent=c, position=(sh, v),
 size=(subScrollWidth, subScrollHeight))
                        bs.containerWidget(edit=c, selectedChild=sw)
                        self._columnWidget = bs.columnWidget(parent=sw, leftBorder=10)
                        bs.widget(edit=sw, autoSelect=True, leftWidget=b1, upWidget=self._tab_buttons[tab])
                        bs.widget(edit=self._tab_buttons[tab], downWidget=sw)

                        self._myReplaySelected = None
                        self._refreshMyReplays()


                elif tab == 'outReplays':
                        cWidth = self._scrollWidth
                        cHeight = self._scrollHeight - 20
                        subScrollHeight = cHeight - 63
                        self._myReplaysScrollWidth = subScrollWidth = (680 if gSmallUI else 640)

                        self._tabContainer = c = bs.containerWidget(parent=self._rootWidget,
                                          position=(scrollLeft,
 scrollBottom + (self._scrollHeight - cHeight) * 0.5),
                                          size=(cWidth, cHeight), background=False,
                                          selectionLoopToParent=True)

                        v = cHeight - 30
                        t = bs.textWidget(parent=c, position=(cWidth * 0.5, v), color=(0.6, 1.0, 0.6), scale=0.7,
 size=(0, 0),
 maxWidth=cWidth * 0.9,
 hAlign='center', vAlign='center',
 text=u'Location:%ModsFolder%' + os.sep + u'replays' + os.sep +u'  This part made by Plasma Boson.Thx Deva for help.')

                        bWidth = 140 if gSmallUI else 178
                        bHeight = 80 if gSmallUI else 106 if gMedUI else 139
                        bSpaceExtra = 0 if gSmallUI else -2 if gMedUI else -5

                        bColor = (0.6, 0.53, 0.63)
                        bTextColor = (0.75, 0.7, 0.8)
                        bv = cHeight - (48 if gSmallUI else 45 if gMedUI else 40) - bHeight
                        bh = 40 if gSmallUI else 40
                        sh = 190 if gSmallUI else 225
                        ts = 1.0 if gSmallUI else 1.2
                        self._myReplaysWatchReplayButton = b1 = bs.buttonWidget(parent=c, size=(bWidth, bHeight), position=(bh, bv),
                                          buttonType='square', color=bColor,
                                          textColor=bTextColor,
                                          onActivateCall=self._onMyReplayPlayPress,
                                          textScale=ts,
                                          label=bs.Lstr(
                                          resource=self._r + '.watchReplayButtonText'),
                                          autoSelect=True)
                        bs.widget(edit=b1, upWidget=self._tab_buttons[tab])
                        if gSmallUI and gToolbars:
                                bs.widget(edit=b1, leftWidget=bsInternal._getSpecialWidget('backButton'))
                        bv -= bHeight + bSpaceExtra
                        b2 = bs.buttonWidget(parent=c, size=(bWidth, bHeight), position=(bh, bv),
buttonType='square', color=bColor, textColor=bTextColor,
onActivateCall=self._onMyReplayRenamePress, textScale=ts,
label=bs.Lstr(resource=self._r + '.renameReplayButtonText'),
autoSelect=True)
                        bv -= bHeight + bSpaceExtra
                        b3 = bs.buttonWidget(parent=c, size=(bWidth, bHeight), position=(bh, bv),
buttonType='square', color=bColor, textColor=bTextColor,
onActivateCall=self._onMyReplayDeletePress, textScale=ts,
label=bs.Lstr(resource=self._r + '.deleteReplayButtonText'),
autoSelect=True)
                        bv -= bHeight + bSpaceExtra
                        b4 = bs.buttonWidget(parent=c, size=(bWidth, bHeight), position=(bh, bv),
buttonType='square', color=bColor, textColor=bTextColor,
onActivateCall=self._onMyReplayTransportPress, textScale=ts,
label=u'拉取QQ\n下载的录像',
autoSelect=True)

                        v -= subScrollHeight+23
                        self._scrollWidget = sw = bs.scrollWidget(parent=c,position=(sh,v),size=(subScrollWidth,subScrollHeight))                        bs.containerWidget(edit=c,selectedChild=sw)
                        self._columnWidget = bs.columnWidget(parent=sw,leftBorder=10)

                        bs.widget(edit=sw,autoSelect=True,leftWidget=b1,upWidget=self._tab_buttons[tab])
                        bs.widget(edit=self._tab_buttons[tab],downWidget=sw)

                        #for our replays.
                        if not os.path.exists(os.path.join(bs.getEnvironment()['userScriptsDirectory'],'replays' + os.sep)):
                                os.makedirs(os.path.join(bs.getEnvironment()['userScriptsDirectory'],'replays' + os.sep))
                        self._myReplaySelected = None
                        self._refreshMyReplays()


                else:
                        # preserve that official share tab coming in future
                        originalWatchWindow._setTab(self, tab)

        def _onMyReplayExportPress(self):
                if self._myReplaySelected is None:
                        self._noReplaySelectedError()
                        return
                self._exportMyReplay(self._myReplaySelected)

        def _exportMyReplay(self, replay):
                try:
                        if replay != '__lastReplay.brp':
                                exportDir = os.path.join(bs.getEnvironment()['userScriptsDirectory'],'replays' + os.sep).encode(SystemEncode)
                                if not os.path.exists(exportDir):
                                        os.mkdir(exportDir)
                                oldNameFull = (bsInternal._getReplaysDir() + os.sep + replay).encode(SystemEncode)
                                newNameFull = os.path.join(exportDir.decode(SystemEncode) + os.sep,replay).encode(SystemEncode)
                                if os.path.exists(newNameFull):
                                        bs.playSound(bs.getSound('error'))
                                        bs.screenMessage(bs.Lstr(resource=self._r + '.replayRenameErrorAlreadyExistsText'), color=(1, 0, 0))
                                else:
                                        shutil.copyfile(oldNameFull, newNameFull)
                                        self._refreshMyReplays()
                                        bs.playSound(bs.getSound('gunCocking'))
                                        bs.screenMessage(u'导出成功，录像文件在' + exportDir + u'目录下.')
                                        #bs.screenMessage(u'MOD下载器也将推出分享录像 功能，敬请期待，下载地址http://deva.fun/')
                        else:
                                bs.playSound(bs.getSound('error'))
                                bs.screenMessage(u'请更换名称后再导出自动保存的录像', color=(1, 0, 0))
                except Exception, e:
                        print e
                        # bs.printException("error copying replay '" + oldNameFull + "' to '" + newNameFull + "'")
                        bs.playSound(bs.getSound('error'))
                        bs.screenMessage(bs.Lstr(resource=self._r + '.replayRenameErrorText'), color=(1, 0, 0))
        def _onMyReplayPlayPress(self):
                if self._myReplaySelected is None:
                        self._noReplaySelectedError()
                        return

                bsInternal._incrementAnalyticsCount('Replay watch')
                def doIt():
                        try:
                                bsInternal._fadeScreen(True)
                                if self._current_tab == 'myReplays':fileDir = (bsInternal._getReplaysDir()+os.sep+self._myReplaySelected).encode(SystemEncode)
                                elif self._current_tab == 'outReplays':fileDir = (os.path.join(bs.getEnvironment()['userScriptsDirectory'],'replays' + os.sep,self._myReplaySelected)).encode(SystemEncode)
                                #print fileDir
                                bsInternal._newReplaySession(fileDir)
                        except Exception:
                                import bsMainMenu
                                bs.printException("exception running replay session")
                                bs.printException()
                                # drop back into a fresh main menu session in case we half-launched or something..
                                bsInternal._newHostSession(bsMainMenu.MainMenuSession)                bsInternal._fadeScreen(False,time=250,endCall=bs.Call(bs.pushCall,doIt))
                bs.containerWidget(edit=self._rootWidget,transition='outLeft')

        def _onMyReplayRenamePress(self):
                if self._myReplaySelected is None:
                        self._noReplaySelectedError()
                        return
                cWidth = 600
                cHeight = 250
                self._myReplaysRenameWindow = c = bs.containerWidget(scale=1.8 if gSmallUI else 1.55 if gMedUI else 1.0,
size=(cWidth,cHeight),transition='inScale')                dName = self._getReplayDisplayName(self._myReplaySelected)
                bs.textWidget(parent=c,size=(0,0),hAlign='center',vAlign='center',
                                          text=bs.Lstr(resource=self._r+'.renameReplayText',subs=[('${REPLAY}',dName)]),
                                          maxWidth=cWidth*0.8,
                                          position=(cWidth*0.5,cHeight-60))
                self._myReplayRenameText = t = bs.textWidget(parent=c,size=(cWidth*0.8,40),hAlign='left',vAlign='center',text=dName,
editable=True,
description=bs.Lstr(resource=self._r+'.replayNameText'),
position=(cWidth*0.1,cHeight-140),autoSelect=True,maxWidth=cWidth*0.7,maxChars=200)
                cb = bs.buttonWidget(parent=c,
label=bs.Lstr(resource='cancelText'),
onActivateCall=bs.Call(bs.containerWidget,edit=c,transition='outScale'),size=(180,60),position=(30,30),autoSelect=True)
                okb = bs.buttonWidget(parent=c,
 label=bs.Lstr(resource=self._r+'.renameText'),
 size=(180,60),position=(cWidth-230,30),
 onActivateCall=bs.Call(self._renameMyReplay,self._myReplaySelected),autoSelect=True)
                bs.widget(edit=cb,rightWidget=okb)
                bs.widget(edit=okb,leftWidget=cb)
                bs.textWidget(edit=t,onReturnPressCall=okb.activate)
                bs.containerWidget(edit=c,cancelButton=cb,startButton=okb)

        def _renameMyReplay(self,replay):
                try:
                        if not self._myReplayRenameText.exists():
                                return
                        newNameRaw = bs.textWidget(query=self._myReplayRenameText)
                        newName = newNameRaw+'.brp'
                        # ignore attempts to change it to what it already is (or what it looks like to the user)
                        if replay != newName and self._getReplayDisplayName(replay) != newNameRaw:
                                #print SystemEncode
                                if self._current_tab == 'myReplays':fileDir = bsInternal._getReplaysDir()
                                elif self._current_tab == 'outReplays':fileDir = bs.getEnvironment()['userScriptsDirectory'] + os.sep + u"replays"
                                oldNameFull = (fileDir+os.sep+replay).encode(SystemEncode)
                                newNameFull = (fileDir+os.sep+newName).encode(SystemEncode)
                                if os.path.exists(newNameFull):
                                        bs.playSound(bs.getSound('error'))
                                        bs.screenMessage(bs.Lstr(resource=self._r+'.replayRenameErrorAlreadyExistsText'),color=(1,0,0))
                                elif any(char in newNameRaw for char in ['/','\\',':']):
                                        bs.playSound(bs.getSound('error'))
                                        bs.screenMessage(bs.Lstr(resource=self._r+'.replayRenameErrorInvalidName'),color=(1,0,0))                                else:
                                        bsInternal._incrementAnalyticsCount('Replay rename')
                                        os.rename(oldNameFull,newNameFull)
                                        self._refreshMyReplays()
                                        bs.playSound(bs.getSound('gunCocking'))
                except Exception,e:
                        bs.printException()                        bs.printException("error renaming replay '"+replay+"' to '"+newName+"'")
                        bs.playSound(bs.getSound('error'))
                        bs.screenMessage(bs.Lstr(resource=self._r+'.replayRenameErrorText'),color=(1,0,0))
                        bs.screenMessage(repr(e),color=(1,0,0))

                bs.containerWidget(edit=self._myReplaysRenameWindow,transition='outScale')


        def _onMyReplayDeletePress(self):
                if self._myReplaySelected is None:
                        self._noReplaySelectedError()
                        return
                ConfirmWindow(bs.Lstr(resource=self._r+'.deleteConfirmText',subs=[('${REPLAY}',self._getReplayDisplayName(self._myReplaySelected))]),
                                          bs.Call(self._deleteReplay,self._myReplaySelected),450,150)

        def _getReplayDisplayName(self,replay):
                if replay.endswith('.brp'):                        replay = replay[:-4]
                if replay == '__lastReplay': return bs.Lstr(resource='replayNameDefaultText').evaluate()
                return replay

        def _deleteReplay(self,replay):
                try:
                        bsInternal._incrementAnalyticsCount('Replay delete')

                        if self._current_tab == 'myReplays':file = os.path.join(bsInternal._getReplaysDir()+os.sep,replay).encode(SystemEncode)
                        elif self._current_tab == 'outReplays':file = os.path.join(bs.getEnvironment()['userScriptsDirectory'] + os.sep,"replays" + os.sep,replay).encode(SystemEncode)
                        os.remove(file)
                        self._refreshMyReplays()
                        bs.playSound(bs.getSound('shieldDown'))
                        if replay == self._myReplaySelected: self._myReplaySelected = None
                except Exception:
                        bs.printException("exception deleting replay '"+replay+"'")
                        bs.playSound(bs.getSound('error'))
                        bs.screenMessage(bs.Lstr(resource=self._r+'.replayDeleteErrorText'),color=(1,0,0))

        def _onMyReplayTransportPress(self):
                        if bs.getEnvironment()['platform'] == 'android':
                                outReplayPath = (bs.getEnvironment()['userScriptsDirectory'] + os.sep + "replays" + os.sep).encode(SystemEncode)
                                QQFilePath = (bs.getEnvironment()['userScriptsDirectory'][:-10] + os.sep + "tencent" + os.sep + "QQfile_recv"+ os.sep).encode(SystemEncode)
                                if os.path.exists(QQFilePath):
                                        def searchFiles(path):
                                          root, dirs, files = os.walk(path).next()
                                          list = []
                                          for fn in files:
                                          if fn.endswith('.brp'):
                                          list.append(fn)
                                          return list
                                        outReplaylist = searchFiles(outReplayPath)
                                        QQFilePathlist = searchFiles(QQFilePath)
                                        if len(QQFilePathlist) > 0:
                                          for itemName in QQFilePathlist:
                                          if itemName not in outReplaylist:
                                          try:
                                          shutil.move(QQFilePath+itemName,outReplayPath+itemName)

                                          except Exception, e:bs.screenMessage(repr(e),color=(1,0,0))
                                          else:bs.screenMessage(u'发现重名文件.(%s)已 跳过.'%itemName.decode('utf-8'),color=(1,0,0));bs.playSound(bs.getSound('error'))
                                        else:bs.screenMessage(u'QQ的下载目录没有录像文件.',color=(1,0,0));bs.playSound(bs.getSound('error'))
                                else:bs.screenMessage(u'找不到QQ的下载目录.(%s)'%QQFilePath.decode('utf-8'),color=(1,0,0));bs.playSound(bs.getSound('error'))
                                self._refreshMyReplays()
                        else:bs.screenMessage(u'Does not support current platform.(%s)'%bs.getEnvironment()['platform'],color=(1,0,0));bs.playSound(bs.getSound('error'))
        def _refreshMyReplays(self):
                for c in self._columnWidget.getChildren(): c.delete()
                tScale = 1.6
                try:
                        if self._current_tab == 'myReplays':names = os.listdir(bsInternal._getReplaysDir())
                        elif self._current_tab == 'outReplays':names = os.listdir(os.path.join(bs.getEnvironment()['userScriptsDirectory'],"replays" + os.sep))
                        names = [bs.uni(n) for n in names if n.endswith('.brp')] # ignore random other files in there..
                        names.sort(key=lambda x:x.lower())
                except Exception:
                        bs.printException("error listing replays dir")
                        names = []

                for i,name in enumerate(names):
                        t = bs.textWidget(parent=self._columnWidget,size=(self._myReplaysScrollWidth/tScale,30),selectable=True,
 color=(1.0,1,0.4) if name == '__lastReplay.brp' else (1,1,1),alwaysHighlight=True,
 onSelectCall=bs.Call(self._onMyReplaySelect,name),
 onActivateCall=self._myReplaysWatchReplayButton.activate,
 text=self._getReplayDisplayName(name),hAlign='left',vAlign='center',cornerScale=tScale,
 maxWidth=(self._myReplaysScrollWidth/tScale)*0.93)
                        if i == 0:
                                bs.widget(edit=t,upWidget=self._tab_buttons['myReplays'])



if bs.getEnvironment().get("buildNumber",0) >= 14343:
        bsUI.WatchWindow = ExWatchWindow
else:print("Brp_helper only runs with bs version higer than 1.4.140.")

