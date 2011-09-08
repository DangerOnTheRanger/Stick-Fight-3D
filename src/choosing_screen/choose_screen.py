from panda3d.core import *
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText 
import random
from os import listdir, sep
from math import pi, cos
from direct.interval.LerpInterval import LerpFunc
from direct.interval.IntervalGlobal import *

class Portrait(object):
    def __init__(self, img, left, right, bottom, top):
        self.generator = CardMaker("Portrait") 
        self.generator.setFrame(left, right, bottom, top) 
        texture = loader.loadTexture(img) 
        self.geom = render2d.attachNewNode(self.generator.generate()) 
        self.geom.setTexture(texture)
        self.lightDown()
        self.name = img.split(".")[0].split("_")[1]
        self.num = img.split("_")[0].split(sep)[1]
        self.t = 0.0

    def setPos(self, x, y):
        self.geom.setPos(x, 0 , y)
    
    def lightUp(self):
        self.geom.setColorScale(Vec4(1,1,1,1))
        
    def lightDown(self):
        self.geom.setColorScale(Vec4(0.5,0.5,0.5,1))   

    
    def selectionTask(self, task):
        self.t += task.delayTime
        self.t %= 100
        t = 0.5*cos(pi*self.t) + 1
        self.geom.setColorScale(Vec4(t,t,t,1))
        return task.again
    
    def _select(self):
        taskMgr.doMethodLater(0.05, self.selectionTask, 'selectionTask' + self.name)
    
    def unselect(self):
        taskMgr.remove('selectionTask'+ self.name)
        self.lightDown()
    
    def select(self):
        self._select()


class PortraitArray(object):
    def __init__(self):
        self.area = [-0.9,0.9, -0.9,-0.6]
        self.rows = 2
        self.cols = 8
        
        self.extents = [(self.area[1]-self.area[0])/self.cols, (self.area[3]-self.area[2])/self.rows]
        self.portraits = {}
        files = listdir("characters")
        files.sort()
        
        f = 0
        
        
        
        for ypos in [1,0]:
            for xpos in range(self.cols):
                p = Portrait("characters" + sep + files[f],
                                        -0.5*self.extents[0]*0.9,
                                        0.5*self.extents[0]*0.9, 
                                        -0.5*self.extents[1]*0.9, 
                                        0.5*self.extents[1]*0.9)
                                        
                self.portraits[int(p.num)] = p
                self.portraits[int(p.num)].setPos(self.area[0] + (xpos+0.5) * self.extents[0], 
                self.area[2] + (ypos+0.5) * self.extents[1])
                f += 1
        
        self.players = [0, 0]
        self.current = 0
        self.text = [OnscreenText(text = "", pos = (-0.8,-0.5)), OnscreenText(text = "", pos = (0.8,-0.5))]  
        self.big_image = [Portrait("characters/01_panda.png", -0.3, 0.3, -0.6, 0.6), Portrait("characters/01_panda.png", -0.3, 0.3, -0.6, 0.6)]  
        self.big_image[0].setPos(-0.6,0.3)
        self.big_image[0].lightUp()
        self.big_image[1].setPos(0.6,0.3)
        self.big_image[1].lightUp()
            
        self.vs = OnscreenText(text = "VS", pos = (0,0))
        
        self.select(1)
        
                
    def clear(self):
        for key in self.portraits.keys():
            if key not in self.players:
                self.portraits[key].unselect()    
    
                
    def select(self, num):
        self.portraits[num].select()
        self.players[self.current] = num
        self.clear()
        self.text[self.current]["text"] = self.portraits[self.players[self.current]].name
        self.big_image[self.current].geom.setTexture(self.portraits[num].geom.getTexture())
        
        
    def left(self):
        if self.players[self.current] in range(2,17):
            self.select(self.players[self.current] - 1)
    
    def right(self):
        if self.players[self.current] in range(1,16):
            self.select(self.players[self.current] + 1)
            
    def up(self):
        if self.players[self.current] in range(9,17):
            self.select(self.players[self.current] - self.cols)
    
    def down(self):
        if self.players[self.current] in range(1,9):
            self.select(self.players[self.current] + self.cols)

    def selected(self):
        if self.current == 0:
            self.current = 1
            self.players[1] = self.players[0]
        else:
            print "already selected"
        

if __name__ == "__main__":
    import direct.directbase.DirectStart 
 
    pa = PortraitArray()
    base.accept('arrow_up', pa.up)
    base.accept('arrow_down', pa.down)
    base.accept('arrow_left', pa.left)
    base.accept('arrow_right', pa.right)
    base.accept('enter', pa.selected)

    run()
    
