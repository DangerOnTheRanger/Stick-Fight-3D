from direct.showbase.ShowBase import ShowBase
from menu import Menu
base = ShowBase()

class Game(object):
    def __init__(self):
        self.menu = Menu()
    """
        self.screens = []
        self.i = 0
        self.screens.append(StageScreen(parent = self))
        self.screens.append(CharacterScreen(parent = self))
        
        for screen in self.screens:
            screen.hide()
        self.notify()
    
    def notify(self):
        if self.i == len(self.screens):
            stage = self.screens[0].getStage()
            players = self.screens[1].getPlayers()
            Match(players[0], players[1], stage)
        elif self.i == 0:
            self.screens[self.i].show()
            self.i += 1
        else:
            self.screens[self.i].show()
            self.i += 1
     """   

g = Game()


#Match("../assets/fighters/Stickman/","../assets/fighters/Stickman/",'../assets/stages/Test Stage - Green/stage')

#base.disableMouse()
#base.camera.setY(-250)
#base.camera.setZ(30)
base.run() 
