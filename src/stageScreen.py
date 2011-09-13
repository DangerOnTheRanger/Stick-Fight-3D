import hud
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import CardMaker
from os import sep
from configFile import readKeys

class StageScreen(object):
    def __init__(self, parent = None):
        self.ps = hud.PreviewStrip("../assets/stages", notify = [self])
        
        self.parent = parent
        
        self.text = OnscreenText("")
        self.text.setPos(0,self.ps.height - 0.4)
        
        self.preview_size = [-0.5,  0.5, -0.5, 0.5]
        
        self.generator = CardMaker("PreviewMaker") 
        self.generator.setFrame(*self.preview_size)
        
        self.preview = aspect2d.attachNewNode(self.generator.generate())
        self.preview.setPos(0,0, 0.4)
        
        self.keys = readKeys()
        self.left = [self.keys[0][1], self.keys[1][2]]
        self.right = [self.keys[0][3], self.keys[1][3]]
        self.select = [self.keys[0][4], self.keys[1][4]]
        
        self.ready = OnscreenText("ready")
        self.ready.setPos(0,self.ps.height)
        self.ready.hide()
        
        self.notify()
     
    def updateText(self):
        t = str(self.ps.current().getTexture().getFilename())
        self.text["text"] = t.split(sep)[-2] 
        
    def updateImg(self):
        self.preview.setTexture(self.ps.current().getTexture())
        
    def rotateLeft(self):
        for key in self.right + self.left:
            base.ignore(key)
        
        self.ps.rotateLeft()
        
    def rotateRight(self):
        for key in self.right + self.left:
            base.ignore(key)

        self.ps.rotateRight()
        
    def sel(self):
        self.ready.show()
        base.ignoreAll()
        if self.parent:
            self.hide()
            self.parent.notify()
            self.ready.hide()

        
    def notify(self, arg = None):
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
        base.ignoreAll()
    
    def show(self):
        self.text.show()
        self.preview.show()
        self.ps.show()
        self.notify()
        
    def getStage(self):
        t = str(self.ps.current().getTexture().getFilename()).rstrip("icon.jpg")
        return t + "stage"
        
if __name__ == "__main__":
    import direct.directbase.DirectStart 

    ps = StageScreen()
    run()
    
