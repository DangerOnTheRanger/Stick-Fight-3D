import hud
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import CardMaker
from os import sep

class StageScreen(object):
    def __init__(self):
        self.ps = hud.PreviewStrip("../assets/stages", notify = [self])
        
        self.text = OnscreenText("")
        self.text.setPos(0,self.ps.height - 0.4)
        
        self.preview_size = [-0.5,  0.5, -0.5, 0.5]
        
        self.generator = CardMaker("PreviewMaker") 
        self.generator.setFrame(*self.preview_size)
        
        self.preview = aspect2d.attachNewNode(self.generator.generate())
        self.preview.setPos(0,0, 0.4)
        
        self.notify()
     
    def updateText(self):
        t = str(self.ps.current().getTexture().getFilename())
        self.text["text"] = t.split(sep)[-2] 
        
    def updateImg(self):
        self.preview.setTexture(self.ps.current().getTexture())
        
    def rotateLeft(self):
        base.ignore('arrow_right')
        self.ps.rotateLeft()
        
    def rotateRight(self):
        base.ignore('arrow_left')
        self.ps.rotateRight()
        
    def notify(self):
        self.updateText()
        self.updateImg()
        base.acceptOnce('arrow_right', self.rotateRight)
        base.acceptOnce('arrow_left', self.rotateLeft)
        
if __name__ == "__main__":
    import direct.directbase.DirectStart 

    ps = StageScreen()
    run()
    
