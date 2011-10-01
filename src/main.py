from direct.showbase.ShowBase import ShowBase
from menu import Menu
base = ShowBase()

class Game(object):
    def __init__(self):
        self.menu = Menu()

g = Game()


#Match("../assets/fighters/Stickman/","../assets/fighters/Stickman/",'../assets/stages/Test Stage - Green/stage')

#base.disableMouse()
#base.camera.setY(-250)
#base.camera.setZ(30)
base.run() 
