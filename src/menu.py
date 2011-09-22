from direct.fsm.FSM import FSM
from direct.actor.Actor import Actor

from direct.interval.MetaInterval import Sequence,Parallel
from direct.interval.FunctionInterval import Func,Wait
from direct.interval.SoundInterval import SoundInterval

from panda3d.core import Point3

from menuBackground import MenuBackground
from characterScreen import CharacterScreen
from stageScreen import StageScreen
from match import Match

class Menu(FSM):


    def __init__(self):
        FSM.__init__(self,"mainMenu")
        self.background = MenuBackground().getNP()
        self.background.reparentTo(render)
        
        self.charScreen = CharacterScreen(callback = lambda: self.request("StageSelect") ) 
        self.charScreen.getNp().reparentTo(self.background)
        self.charScreen.getNp().setPos(-1,1.4,0)
        self.charScreen.getNp().setScale(.3)
        
        self.stageScreen = StageScreen(callback = lambda: self.request("Match") ) 
        self.stageScreen.getNp().reparentTo(self.background)
        self.stageScreen.getNp().setPos(0,1.4,0)
        self.stageScreen.getNp().setScale(.3)
        
        
        self.request("CharSelect")
        
        
    def enterCharSelect(self):
        base.disableMouse()
        self.charScreen.enableInput()
        self.camlerp = base.camera.posInterval(1.5, Point3(-1, 0, 0),blendType='easeInOut')
        self.camlerp.start()
        print "enter charsel"
        pass
        
    def filterCharSelect(self,request,options):
        if request != "CharSelect":
            return request

    def exitCharSelect(self):
        self.charScreen.disableInput()
        print "exit charsel"

    
    
    #---------------------

    def enterStageSelect(self):
        self.stageScreen.enableInput()
        self.camlerp = base.camera.posInterval(1.5, Point3(0, 0, 0),blendType='easeInOut')
        self.camlerp.start()
        print "enter Stage sel"
        pass
        #self.fighterinstance.setSpeed(self.cfgData["run-in"]["speedx"],self.cfgData["run-in"]["speedy"])
        
    def filterStageSelect(self,request,options):
        pass
        if request != "StageSelect":
            return request

    def exitStageSelect(self):
        self.stageScreen.disableInput()
        print "exit stage sel"
    
    #-------------------------
    
    def enterMatch(self):
        self.background.hide()
        stage = self.stageScreen.getStage()
        players = self.charScreen.getPlayers()
        Match(players[0], players[1], stage)
    
    def filterMatch(self):
        pass
        
    def exitMatch(self):
        pass
