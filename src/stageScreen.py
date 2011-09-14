import hud
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import CardMaker
from os import sep
from configFile import readKeys

class StageScreen(object):
    def __init__(self, parent = None):
        # we are sending the preview strip reference to us so it can
        # inform us to update text and image preview
        self.ps = hud.PreviewStrip("../assets/stages", parent = [self])
        # parent of the screen, will be notified when
        # screen does its job
        self.parent = parent
        # name of the stage will be displyed here
        self.text = OnscreenText("")
        self.text.setPos(0,self.ps.height - 0.4)
        
        self.preview_size = [-0.5,  0.5, -0.5, 0.5]
        
        self.generator = CardMaker("PreviewMaker") 
        self.generator.setFrame(*self.preview_size)
        
        self.preview = aspect2d.attachNewNode(self.generator.generate())
        self.preview.setPos(0,0, 0.4)
        # keys are read so that the first in the pair is from player 1
        # and second from the player 2, so that they both can decide
        self.keys = readKeys()
        self.left = [self.keys[0][1], self.keys[1][2]]
        self.right = [self.keys[0][3], self.keys[1][3]]
        self.select = [self.keys[0][4], self.keys[1][4]]
        
        self.ready = OnscreenText("ready")
        self.ready.setPos(0,self.ps.height)
        # will be shown when players selected the stage
        self.ready.hide()
        # we notify ourselves to enable the key input and update text
        # and preview
        self.notify()
     
    def updateText(self):
        t = str(self.ps.current().getTexture().getFilename())
        self.text["text"] = t.split(sep)[-2] 
        
    def updateImg(self):
        self.preview.setTexture(self.ps.current().getTexture())
        
    def rotateLeft(self):
        # ignore all keys so that nothing get pressed while strip rotates
        # strip will notify us when it finishes and we will enable it again
        # in notify()
        for key in self.right + self.left:
            base.ignore(key)
        
        self.ps.rotateLeft()
        
    def rotateRight(self):
        # same as above
        for key in self.right + self.left:
            base.ignore(key)

        self.ps.rotateRight()
        
    def sel(self):
        # short for selection, used when player use punch key
        # we display ready over image
        self.ready.show()
        # discarding functions assigne to to players keys
        for key in self.left+self.right+self.select:
            base.ignore(key)
        # we hide ourselves
        if self.parent:
            self.hide()
            
            self.parent.notify()
            self.ready.hide()

        
    def notify(self, arg = None):
        # arg is just for compatibility issues here
        self.updateText()
        self.updateImg()
        
        for key in self.right:
            base.acceptOnce(key, self.rotateRight)
        for key in self.left:
            base.acceptOnce(key, self.rotateLeft)
        for key in self.select:
            base.acceptOnce(key, self.sel)    

    
    def hide(self):
        self.text.hide()
        self.preview.hide()
        self.ps.hide()
        for key in self.left+self.right+self.select:
            base.ignore(key)
    
    def show(self):
        self.text.show()
        self.preview.show()
        self.ps.show()
        self.notify()
        
    def getStage(self):
        # return path to stage acceptable by Match class
        t = str(self.ps.current().getTexture().getFilename()).rstrip("icon.jpg")
        return t + "stage"
        
if __name__ == "__main__":
    import direct.directbase.DirectStart 

    ps = StageScreen()
    run()
    
