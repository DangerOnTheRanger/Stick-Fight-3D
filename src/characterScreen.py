from hud import PreviewStrip
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import CardMaker , NodePath
from os import sep
from configFile import readKeys
from direct.showbase import DirectObject

class CharacterScreen(DirectObject.DirectObject):
    def __init__(self, callback = None):
        self.charRoot = NodePath("characterSelectRoot")
        
        self.players = [{},{}]
        # heights on which preview strips appear
        heights = [0.8,-0.8]
        # determines separation between previews
        previews = [0.5, -0.5]

        self.callback = callback
        self.preview_size = [-0.3,  0.3, -0.3, 0.3]
        self.generator = CardMaker("PreviewMaker") 
        self.generator.setFrame(*self.preview_size)
        self.players_ready = 0
        
        self.vs = OnscreenText("vs")
        self.vs.reparentTo(self.charRoot)
        
        players = self.players
        for i in range(2):
            players[i]["strip"] = PreviewStrip("../assets/fighters", def_height = heights[i])
            players[i]["strip"].getStripNP().reparentTo(self.charRoot)
            
            players[i]["text"] = OnscreenText("")
            players[i]["text"].reparentTo(self.charRoot)
            players[i]["text"].setPos(0, players[i]["strip"].height - (2*i-1)* 0.25)
            
            players[i]["preview"] = self.charRoot.attachNewNode(self.generator.generate())
            players[i]["preview"].setPos(previews[i],.2, 0.0)
            players[i]["select"] = OnscreenText("ready")
            players[i]["select"].reparentTo(self.charRoot)
            players[i]["select"].setPos(0, players[i]["strip"].height)
            players[i]["select"].hide()

        self.keys = readKeys()
        self.left = [self.keys[0][1], self.keys[1][2]]
        self.right = [self.keys[0][3], self.keys[1][3]]
        self.confirm = [self.keys[0][4], self.keys[1][4]]

        self.updateText()
        self.updateImg()
    
    def enableInput(self):
        #map keys of player 0
        self.accept(self.right[0], self.rotateRight, [0])
        self.accept(self.left[0], self.rotateLeft, [0])
        self.accept(self.confirm[0], self.select, [0])
        #same for player 1
        self.accept(self.right[1], self.rotateRight, [1])
        self.accept(self.left[1], self.rotateLeft, [1])
        self.accept(self.confirm[1], self.select, [1])
    
    def disableInput(self):
        for key in self.left + self.right + self.confirm:
            self.ignore(key)
        
    def getNp(self):
        return self.charRoot
     
    def updateText(self):
        for i in range(2):
            t = str(self.players[i]["strip"].current().getTexture().getFilename())
            self.players[i]["text"]["text"] = t.split(sep)[-2] 
        
    def updateImg(self):
        for i in range(2):
            t = self.players[i]["strip"].current().getTexture()
            self.players[i]["preview"].setTexture(t)
        
    def rotateLeft(self, num):
        self.players[num]["strip"].rotateLeft()
        self.updateText()
        self.updateImg()
        
    def rotateRight(self, num):
        self.players[num]["strip"].rotateRight()
        self.updateText()
        self.updateImg()
        
    def select(self, num):
        self.players[num]["select"].show()
        for key in [self.right[num], self.left[num], self.confirm[num]]:
            self.ignore(key)
        self.players_ready += 1    
        if self.callback and self.players_ready == 2:
            #self.hide()
            self.callback()
            self.players[0]["select"].hide()
            self.players[1]["select"].hide()

    
    def hide(self):
        self.charRoot.hide()
        self.disableInput()
    
    def show(self):
        for i in range(2):
            self.players[i]["text"].show()
            self.players[i]["preview"].show()
            self.players[i]["strip"].show()
        self.vs.show()
        
    def getPlayers(self):
        players = []
        for i in range(2):
            t = str(self.players[i]["strip"].current().getTexture().getFilename()).rstrip("icon.jpg")
            players.append(t)
        return players
        
if __name__ == "__main__":
    import direct.directbase.DirectStart 

    ps = CharacterScreen()
    run()
    
