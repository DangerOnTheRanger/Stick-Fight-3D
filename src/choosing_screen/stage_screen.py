from panda3d.core import *
from direct.gui.OnscreenText import OnscreenText 
from direct.gui.OnscreenImage import OnscreenImage
from os import listdir, sep
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpScaleInterval
from direct.interval.IntervalGlobal import Parallel, Sequence, Func

class PreviewStrip(object):
    
    def __init__(self, catalog, notify, height = -0.5):
        self.height = height
        self.catalog = catalog
        
        self.notify = notify

        self.preview_size = [-0.1,  0.1, -0.1, 0.1]
        
        self.generator = CardMaker("PreviewMaker") 
        self.generator.setFrame(*self.preview_size) 
        
        self.textures = []
        self.loadPreviewImages()
        
        #number of items visible on the screen
        self.visible = min(len(self.textures),5)
        
        #duration of an animation
        self.duration = 0.3
        
        self.positions = []
        self.preparePositions()
        
        self.head = 0
        self.tail = self.visible - 1
        
    def loadPreviewImages(self):
        files = listdir(self.catalog)
        files.sort()
        for filename in files:
            self.textures.append(loader.loadTexture(sep.join([self.catalog,filename,"icon.jpg"])))

    
    # distribution functions they specify the shape in which
    # initially visible images are arranged
    def x_dist(self, i):
        return 0.5*(i - self.visible/2)
    
    def y_dist(self, i):
        return abs (i - self.visible /2 )
    
    # initials scaling of the visible images
    def scale(self, i):
        try:
            return 2.5 -  2*abs (float(i)/(self.visible-1) -  0.5)
        except:
            return 1.0
    
    def preparePositions(self):
        for i in range(0,self.visible):
            model = aspect2d.attachNewNode(self.generator.generate())
            model.setPos(self.x_dist(i), self.y_dist(i), self.height)
            model.setScale(self.scale(i))
            # so that images are correctly displayed on top 
            # of each other
            model.setDepthTest(True)
            model.setDepthWrite(True)
            self.positions.append(model)
        
        # setting images    
        for i in range(len(self.positions)):
            self.positions[i].setTexture(self.textures[i])
        

    def _scaleItem(self, i, dir):
        # if dir is negative item is scaled right
        # if dir is positive item is scaled left
        next = (i+dir)%len(self.positions)
        return LerpScaleInterval (
                    self.positions[i], 
                    duration = self.duration,
                    startScale = self.positions[i].getScale(),
                    scale = self.positions[next].getScale()
        )
       
    def _positionItem(self, i, dir):
        # if dir is negative item is moved right
        # if dir is positive item is moved left 
        next = (i+dir) % len(self.positions)
        return LerpPosInterval (
                    self.positions[i], 
                    duration = self.duration,
                    startPos = self.positions[i].getPos(),
                    pos = self.positions[next].getPos()
        )
        
    def _adjustLeft(self):
        last = self.positions.pop()
        self.head = (self.head - 1) % len(self.textures)
        self.tail = (self.tail - 1) % len(self.textures)
        last.setTexture(self.textures[self.head])
        self.positions.insert(0,last)
        
        self.notifyAll()

    
    def _adjustRight(self):
        first = self.positions.pop(0)
        self.head = (self.head + 1) % len(self.textures)
        self.tail = (self.tail + 1) % len(self.textures)
        first.setTexture(self.textures[self.tail])
        self.positions.append(first)

        self.notifyAll()
        
    
    def rotateLeft(self):
        parallel = Parallel()
        
        for i in range(len(self.positions)-1):
            parallel.append( self._positionItem(i, 1))
            parallel.append( self._scaleItem(i, 1))

        # last item is moved symetrically so it has its scale preserved
        parallel.append(self._positionItem(-1,1))
        
        self.seq = Sequence(parallel, Func(self._adjustLeft))
        self.seq.start()

        
    def rotateRight(self):
        parallel = Parallel()
        
        for i in range(len(self.positions)):
            parallel.append( self._positionItem(i, -1))
            parallel.append( self._scaleItem(i,  -1))
 
  
        parallel.append(self._positionItem(0,-1))

        self.seq = Sequence(parallel, Func(self._adjustRight))
        self.seq.start()

    def current(self):
        # list is being kept the way that the middle argument in the list is always current
        return self.positions[self.visible/2]
    
    def notifyAll(self):
        for item in self.notify:
            item.notify()

    
 
 
class StageScreen(object):
    def __init__(self):
        self.ps = PreviewStrip("../../assets/stages", notify = [self])
        
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
    
