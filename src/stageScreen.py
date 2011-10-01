from hud import PreviewStrip
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import CardMaker,NodePath
from os import sep
from configFile import readKeys
from direct.showbase import DirectObject

class StageScreen(DirectObject.DirectObject):
    def __init__(self, callback = None):
        self.stageRoot = NodePath("stageSelectRoot")
        
        self.ps = PreviewStrip("../assets/stages" ,-0.7)
        self.ps.getStripNP().reparentTo(self.stageRoot)
        
        self.callback = callback
        # name of the stage will be displayed here
        self.text = OnscreenText("")
        self.text.reparentTo(self.stageRoot)
        self.text.setPos(0,self.ps.height - 0.4)
        
        self.preview_size = [-0.5,  0.5, -0.5, 0.5]
        
        self.generator = CardMaker("PreviewMaker") 
        self.generator.setFrame(*self.preview_size)
        
        self.preview = self.stageRoot.attachNewNode(self.generator.generate())
        self.preview.setPos(0,0, 0.4)
        # keys are read so that the first in the pair is from player 1
        # and second from the player 2, so that they both can decide
        self.keys = readKeys()
        self.left = [self.keys[0][1], self.keys[1][2]]
        self.right = [self.keys[0][3], self.keys[1][3]]
        self.select = [self.keys[0][4], self.keys[1][4]]
        
        self.ready = OnscreenText("ready")
        self.ready.reparentTo(self.stageRoot)
        self.ready.setPos(0,self.ps.height)
        # will be shown when players selected the stage
        self.ready.hide()
        # we notify ourselves to enable the key input and update text
        # and preview
        
        self.updateText()
        self.updateImg() 
        
        self.disableInput()
    
    def enableInput(self):
        self.accept( self.left[0], self.rotateLeft ) 
        self.accept( self.left[1], self.rotateLeft ) 
        self.accept( self.right[0], self.rotateRight ) 
        self.accept( self.right[1], self.rotateRight ) 
        self.accept( self.select[0], self.callback)
        self.accept( self.select[1], self.callback)
    
    def disableInput(self):
        for key in self.left + self.right + self.select:
            self.ignore(key) 
    
    def getNp(self):
        return self.stageRoot 
     
    def updateText(self):
        t = str(self.ps.current().getTexture().getFilename())
        self.text["text"] = t.split(sep)[-2] 
     
    def updateImg(self):
        self.preview.setTexture(self.ps.current().getTexture())

    def rotateRight(self):
        self.ps.rotateRight()
        self.updateText()
        self.updateImg()    
        
    def rotateLeft(self):
        self.ps.rotateLeft()
        self.updateText()
        self.updateImg()
    
    def hide(self):
        self.stageRoot.hide()
    
    def show(self):
        self.stageRoot.show()
        
    def getStage(self):
        # return path to stage acceptable by Match class
        t = str(self.ps.current().getTexture().getFilename()).rstrip("icon.jpg")
        return t + "stage"
        
if __name__ == "__main__":
    import direct.directbase.DirectStart 

    ps = StageScreen()
    run()
    
