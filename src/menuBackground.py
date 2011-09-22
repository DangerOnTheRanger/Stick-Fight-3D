from panda3d.core import CardMaker , NodePath , ExecutionEnvironment
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3
from random import random , uniform ,seed

MAIN_DIR = ExecutionEnvironment.expandString("$MAIN_DIR")

class MenuBackground():
    
    def getNP(self):
        return self.menuNP

    def _addCard(self,texture):
        tex = loader.loadTexture(MAIN_DIR+"/../assets/models/bamboo/"+texture)
        cm = CardMaker('card')
        ratio = float(tex.getXSize())/tex.getYSize()
        cm.setFrame(-0.5*ratio,0.5*ratio,-0.5,0.5)
        card = self.menuNP.attachNewNode(cm.generate())
        card.setTexture(tex)
        return card

   
    def __init__(self):
        seed(1236)
        self.menuNP = NodePath("menunp")
        background = self._addCard('bamboo-menu-layer-4.jpg')
        background.setY( 10)
        background.setScale(6)

        for i in range(20):
            bamboo3 = self._addCard('bamboo-menu-layer-3.png')
            bamboo3.setTransparency(True)
            bamboo3.setY(7+random()*3)
            bamboo3.setX(uniform(-4,4))
            bamboo3.setZ(uniform(-.3,.3))
            bamboo3.setR(uniform(-1,1)*3)
            bamboo3.setScale(6)
        
        for i in range(12):
            bamboo2 = self._addCard('bamboo-menu-layer-2.png')
            bamboo2.setTransparency(True)
            bamboo2.setY(4.5+uniform(0,2.5))
            bamboo2.setX(uniform(-4,4))
            bamboo2.setZ(uniform(-.1,.1))
            #bamboo2.setR(uniform(-1,1)*2)
            bamboo2.setScale(4)    
            
            dummy = self.menuNP.attachNewNode("rotate-dummy")
            dummy.setZ(-5)
            bamboo2.wrtReparentTo(dummy)
            h1 = uniform(-3,3)
            h2 = h1 + uniform(-1,1)
            time = uniform(5,9)
            hpr1 = dummy.hprInterval(time, Point3(0, 0, h1), Point3(0, 0, h2),blendType='easeInOut')
            hpr2 = dummy.hprInterval(time, Point3(0, 0, h2), Point3(0, 0, h1),blendType='easeInOut')
            ani = Sequence(hpr1,hpr2)
            ani.loop()

        for i in range(7):
            bamboo1 = self._addCard('bamboo-menu-layer-1.png')
            bamboo1.setTransparency(True)
            bamboo1.setY(2.0+uniform(0,2))
            bamboo1.setX(uniform(-2,2))
            bamboo1.setZ(uniform(-.06,.06))
            #bamboo1.setR(uniform(-1,1)*1)
            bamboo1.setScale(2.2) 
            
            dummy = self.menuNP.attachNewNode("rotate-dummy")
            dummy.setZ(-5)
            bamboo1.wrtReparentTo(dummy)
            h1 = uniform(-3,3)
            h2 = h1 + uniform(-1,1)
            time = uniform(5,9)
            hpr1 = dummy.hprInterval(time, Point3(0, 0, h1), Point3(0, 0, h2),blendType='easeInOut')
            hpr2 = dummy.hprInterval(time, Point3(0, 0, h2), Point3(0, 0, h1),blendType='easeInOut')
            ani = Sequence(hpr1,hpr2)
            ani.loop()

        bamboo0 = self._addCard('bamboo-menu-layer-0.png')
        bamboo0.setY(1.9)
        bamboo0.setX(-1.5)
        bamboo0.setR(4)
        bamboo0.setScale(1.5)
        bamboo0.setTransparency(True)

        dummy = self.menuNP.attachNewNode("rotate-dummy")
        dummy.setZ(-5)
        bamboo0.wrtReparentTo(dummy)
        h1 = 0
        h2 = h1 + 0.2
        time = uniform(5,9)
        hpr1 = dummy.hprInterval(time, Point3(0, 0, h1), Point3(0, 0, h2),blendType='easeInOut')
        hpr2 = dummy.hprInterval(time, Point3(0, 0, h2), Point3(0, 0, h1),blendType='easeInOut')
        ani = Sequence(hpr1,hpr2)
        ani.loop()


if __name__ == '__main__':
    from direct.showbase.ShowBase import ShowBase    
    base = ShowBase()
    menubg = MenuBackground().getNP()
    menubg.reparentTo(render)
    PosInterval1 = base.camera.posInterval(6, Point3(-1, 0, 0),  startPos=Point3(1, 0, 0),blendType='easeInOut')
    PosInterval2 = base.camera.posInterval(6, Point3(1, 0, 0),  startPos=Point3(-1, 0, 0),blendType='easeInOut')
    base.disableMouse()
    camera.setPos(1,0,0)
    cameramove = Sequence(PosInterval1,PosInterval2)
    cameramove.start()
    base.run()
