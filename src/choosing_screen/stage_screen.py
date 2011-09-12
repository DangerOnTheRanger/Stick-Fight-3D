from panda3d.core import *
from direct.gui.OnscreenText import OnscreenText 
from os import listdir, sep
from math import pi, sin, cos, pow, copysign, degrees
from direct.interval.LerpInterval import LerpFunc, LerpHprInterval, LerpScaleInterval
from direct.interval.IntervalGlobal import *

class PreviewStrip(object):
    
    def __init__(self, catalog, height = -0.5):
        self.height = height
        self.catalog = catalog
        
        ratio = 1.3
        self.preview_size = [-0.1*ratio,  0.1*ratio, -0.1, 0.1]
        
        self.generator = CardMaker("PreviewMaker") 
        self.generator.setFrame(*self.preview_size) 
        
        self.textures = []
        self.loadPreviewImages()
        
        #number of items visible on the screen
        self.visible = 15
        #angle separation between the cards
        self.angle = -pi / (self.visible - 1)
        #duration of an animation
        self.duration = 0.3
        self.positions = []
        self.preparePositions()
        self.first = 0
        self.last = self.visible
        self.text = OnscreenText("")
        self.text["text"] = str(self.current().getTexture().getFilename())
        self.text.setPos(0,-0.9)

    def loadPreviewImages(self):
        files = listdir(self.catalog)
        files.sort()
        for filename in files:
            self.textures.append(loader.loadTexture(self.catalog + sep + filename))

    
    # depth function - for setting the Y good
    def depth(self, i):
        return abs (i - self.visible /2 )
    
    def preparePositions(self):
        angle = self.angle
        for i in range(0,self.visible):
            model = aspect2d.attachNewNode(self.generator.generate())
            # here we specify the distribution of images 
            # and hence the shape they will create
            model.setPos(1.4*cos(i*angle), self.depth(i), self.height)
            # how they are scaled
            model.setScale(abs(sin(i*angle)) + 2)
            model.setDepthTest(True)
            model.setDepthWrite(True)
            self.positions.append(model)
            
        for i in range(len(self.positions)):
            self.positions[i].setTexture(self.textures[i])
        

    def _scaleItem(self, i, dir):
        next = (i+dir)%len(self.positions)
        return LerpScaleInterval (
                    self.positions[i], 
                    duration = self.duration,
                    startScale = self.positions[i].getScale(),
                    scale = self.positions[next].getScale()
        )
    def _positionItem(self, i, dir):
        next = (i+dir)%len(self.positions)
        return LerpPosInterval (
                    self.positions[i], 
                    duration = self.duration,
                    startPos = self.positions[i].getPos(),
                    pos = self.positions[next].getPos()
        )
        
    def _adjustLeft(self):
        last = self.positions.pop()
        self.first = (self.first - 1) % len(self.textures)
        #last.setTexture(self.textures[self.first])
        self.positions.insert(0,last)
        self.text["text"] = str(self.current().getTexture().getFilename())
    
    def _adjustRight(self):
        first = self.positions.pop(0)
        self.last = (self.last + 1) % len(self.textures)
        #first.setTexture(self.textures[self.last])
        self.positions.append(first)
        self.text["text"] = str(self.current().getTexture().getFilename())
    
    def rotateLeft(self):
        parallel = Parallel()
        
        for i in range(len(self.positions)-1):
            parallel.append( self._positionItem(i, 1))
            parallel.append( self._scaleItem(i, 1))
  
        pos = self.positions[-4].getPos()
        pos.setX(pos.getX()*(-1))
        pos.setY(pos.getY()*(-1))

        parallel.append(self._positionItem(-1,1))
        seq = Sequence(parallel, Func(self._adjustLeft))
        seq.start()

        
    def rotateRight(self):
        parallel = Parallel()
        
        for i in range(len(self.positions)):
            parallel.append( self._positionItem(i, -1))
            parallel.append( self._scaleItem(i,  -1))
 
        
        pos = self.positions[3].getPos()
        pos.setX(pos.getX()*(-1))
        pos.setY(pos.getY()*(-1))
        parallel.append(self._positionItem(0,-1))
        seq = Sequence(parallel, Func(self._adjustRight))
        seq.start()

    def current(self):
        return self.positions[self.visible/2]
        
        
if __name__ == "__main__":
    import direct.directbase.DirectStart 
    
    ps = PreviewStrip("characters")

    base.accept('arrow_left', ps.rotateLeft)
    base.accept('arrow_right', ps.rotateRight)



    run()
    
