from hud import PreviewStrip
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import CardMaker
from os import sep
from configFile import readKeys

class CharacterScreen(object):
    def __init__(self):
        self.players = [{},{}]
        heights = [0.7,-0.7]
        previews = [0.5, -0.5]
        
        self.preview_size = [-0.3,  0.3, -0.3, 0.3]
        self.generator = CardMaker("PreviewMaker") 
        self.generator.setFrame(*self.preview_size)
        
        players = self.players
        
        self.vs = OnscreenText("vs")
        
        for i in range(2):
            players[i]["strip"] = PreviewStrip("../assets/stages", height = heights[i], notify = [self])
            
            players[i]["text"] = OnscreenText("")
            players[i]["text"].setPos(0, players[i]["strip"].height - 0.25)
            
            players[i]["preview"] = aspect2d.attachNewNode(self.generator.generate())
            players[i]["preview"].setPos(previews[i],0, 0.0)

        self.keys = readKeys()
        self.left = [self.keys[0][1], self.keys[1][2]]
        self.right = [self.keys[0][3], self.keys[1][3]]
        self.select = [self.keys[0][4], self.keys[1][4]]
        
        self.notify()
     
    def updateText(self):
        for i in range(2):
            t = str(self.players[i]["strip"].current().getTexture().getFilename())
            self.players[i]["text"]["text"] = t.split(sep)[-2] 
        
    def updateImg(self):
        for i in range(2):
            t = self.players[i]["strip"].current().getTexture()
            self.players[i]["preview"].setTexture(t)
        
    def rotateLeft(self, num):
        for key in self.right + self.left:
            base.ignore(key)
        self.players[num]["strip"].rotateLeft()
        
    def rotateRight(self, num):
        for key in self.right + self.left:
            base.ignore(key)
        self.players[num]["strip"].rotateRight()
        
    def notify(self):
        self.updateText()
        self.updateImg()
        
        for key in self.right:
            base.acceptOnce(key, self.rotateRight, [self.right.index(key)])
        for key in self.left:
            base.acceptOnce(key, self.rotateLeft, [self.left.index(key)])
    
    def hide(self):
        for i in range(2):
            self.players[i]["text"].hide()
            self.players[i]["preview"].hide()
            self.players[i]["strip"].hide()
        self.vs.hide()
    
    def show(self):
        for i in range(2):
            self.players[i]["text"].show()
            self.players[i]["preview"].show()
            self.players[i]["strip"].show()
        self.vs.show()
        
if __name__ == "__main__":
    import direct.directbase.DirectStart 

    ps = CharacterScreen()
    run()
    
