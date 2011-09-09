from panda3d.core import *
from direct.gui.OnscreenText import OnscreenText 
from os import listdir, sep
from math import pi, cos
from direct.interval.LerpInterval import LerpFunc
from direct.interval.IntervalGlobal import *

class Portrait(object):
    def __init__(self, img, left = 0, right = 0.2, bottom = 0.0, top = 0.2):
        self.left, self.right, self.bottom, self.top = left, right, bottom, top
        # setting up a portrait
        self.generator = CardMaker("Portrait") 
        self.generator.setFrame(left, right, bottom, top) 
        texture = loader.loadTexture(img) 
        self.geom = aspect2d.attachNewNode(self.generator.generate()) 
        self.geom.setTexture(texture)
        self.lightDown()
        # retrieving information from filename
        self.name = img.split(".")[0].split("_")[1]
        self.num = img.split("_")[0].split(sep)[1]
        # used for selection
        self.t = 0.0

    def setPos(self, x, y):
        self.geom.setPos(x, 0 , y)
    
    def lightUp(self):
        self.geom.setColorScale(Vec4(1,1,1,1))
        
    def lightDown(self):
        self.geom.setColorScale(Vec4(0.5,0.5,0.5,1))   

    def selectionTask(self, task):
        self.t += task.delayTime
        t = 0.5*cos(pi*self.t) + 1
        self.geom.setColorScale(Vec4(t,t,t,1))
        return task.again
    
    def unselect(self):
        taskMgr.remove('selectionTask'+ self.name)
        self.lightDown()
    
    def select(self):
        taskMgr.doMethodLater(0.03, self.selectionTask, 'selectionTask' + self.name)

class VersusArea(object):
    def __init__(self):
        left, right = -1.0, 1.0
        bottom, top = 0.0, 1.4 
        gap, subtitle = 0.2, 0.2
        width = ((right - left) - gap) / 2
        height = ((top - bottom) - subtitle) / 2
        size = 0.5*max(width, height)
        
        self.images = [Portrait("characters/01_panda.png", -size , size, -size , size), 
                        Portrait("characters/01_panda.png", -size , size, -size , size)]
        self.images[0].setPos(-(gap + 0.5*width), bottom + 0.5*height + subtitle)
        self.images[1].setPos(gap + 0.5*width, bottom  + 0.5*height + subtitle)
        
        self.vs = OnscreenText(text = "vs", pos = (0.0, (top - bottom)/2- height + subtitle))
        
        self.subs = [OnscreenText(text = "Player 1", pos = (-(gap + 0.5*width), bottom - 0.5*subtitle)), 
                        OnscreenText(text = "Player 2", pos = (gap + 0.5*width, bottom - 0.5*subtitle))]
        
    def setPlayerImage(self, num, image):
        self.images[num].geom.setTexture(image)
        self.images[num].lightUp()
    
    def setPlayerSub(self, num, text):
        self.subs[num]["text"] = text



class PortraitArray(object):
    def __init__(self, catalog, slots, rows):
        left, right = -1.0, 1.0
        bottom, top = -1.2, -0.5
        
        filenames = listdir(catalog)
        filenames.sort()
        while len(filenames) > slots:
            filenames.pop()
        
        self.portraits = [[] for i in range(rows)]
        for i in range(len(self.portraits)):
            self.portraits[i] = [None for j in range(slots/rows)]
        
        for i in range(slots % rows):
            self.portraits[i].append(None)
        
        height = (bottom - top)/ len(self.portraits)
        width = (right - left)/len(self.portraits[0])
        size = 0.95*min(width,abs(height))
        
        k = 0
        for i in range(len(self.portraits)):
            for j in range(len(self.portraits[i])):
                self.portraits[i][j] = Portrait(catalog + sep + filenames[k], 0 , size, 0, size)
                self.portraits[i][j].setPos(left + j*width, top + i*height)
                k += 1

        temp = []
        
        self.vs = VersusArea()
        # initial selection
        self.players = [[0,0],[0,0]]
        
        
        
    def clear(self):
        for i in range(len(self.portraits)):
            for j in range(len(self.portraits[i])):
                pass
                
    def select(self, player, x, y):
        self.players[player] = [x,y]
        self.portraits[x][y].select()
        self.clear()
        self.vs.setPlayerImage(player,self.portraits[x][y].geom.getTexture())
        self.vs.setPlayerSub(player,self.portraits[x][y].name)
    
    def unselect(self, player, x, y):
        if self.players[0] != self.players[1]:
            self.portraits[x][y].unselect()
        
        
    def left(self, player):
        x = self.players[player][0]
        y = self.players[player][1]
        if y > 0:
            self.unselect(player, x,y)
            self.select(player, x,y-1)
    
    def right(self, player):
        x = self.players[player][0]
        y = self.players[player][1]
        if y < len(self.portraits[x]) - 1:
            self.unselect(player, x,y)
            self.select(player, x,y+1)
            
    def up(self, player):
        x = self.players[player][0]
        y = self.players[player][1]
        if x > 0:
            self.unselect(player, x,y)
            self.select(player, x-1,y)
    
    def down(self, player):
        x = self.players[player][0]
        y = self.players[player][1]
        if (x < len(self.portraits) - 1):
            if y == len(self.portraits[x])-1 and len(self.portraits[x]) > len(self.portraits[x + 1]):
                pass
            else:
                self.unselect(player, x,y)
                self.select(player, x+1,y)


if __name__ == "__main__":
    import direct.directbase.DirectStart 
 
    pa = PortraitArray("characters", 16, 2)
    base.accept('arrow_up', pa.up,[0])
    base.accept('arrow_down', pa.down,[0])
    base.accept('arrow_left', pa.left,[0])
    base.accept('arrow_right', pa.right,[0])

    base.accept('w', pa.up,[1])
    base.accept('s', pa.down,[1])
    base.accept('a', pa.left,[1])
    base.accept('d', pa.right,[1])


    run()
    
