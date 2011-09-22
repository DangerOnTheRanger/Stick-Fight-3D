from direct.gui.DirectGui import *
from panda3d.core import TextNode, CardMaker , NodePath 
from direct.task import Task
from direct.interval.LerpInterval import LerpFunc
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import TransparencyAttrib
from os import sep, listdir

PLAYER_1_SIDE, PLAYER_2_SIDE = range(2)


class PlayerHud(object):

    def __init__(self, playerSide, name):

        self.side = playerSide
        self.name = name

        self._createHealthBar()
        self._createNameTag()
        self._createRoundIndicator()

    def setHealth(self, percentage):
        self.healthBar['value'] = percentage

    def setRoundIndicator(self, status):
        self.roundIndicator['text'] = status

    def _createHealthBar(self):

        HEALTHBAR_SCALE = 0.4
        healthBarPos = [-0.55, 0, 0.90]

        if self.side == PLAYER_2_SIDE:
            healthBarPos[0] *= -1

        self.healthBar = DirectWaitBar(scale = HEALTHBAR_SCALE,
                                       pos = healthBarPos,
                                       range = 100,
                                       value = 100)
        self.healthBar.reparentTo(render2d)
        self.healthBar['frameColor'] = (0.8,0.8,0.8,0.5)


    def _createRoundIndicator(self):

        INDICATOR_SCALE = 0.08
        indicatorPos = [-0.18, 0.80]
        indicatorAlign = TextNode.ARight

        if self.side == PLAYER_2_SIDE:

            indicatorPos[0] *= -1
            indicatorAlign = TextNode.ALeft


        self.roundIndicator = OnscreenText(scale = INDICATOR_SCALE,
                                           pos = indicatorPos
                                           )
        self.roundIndicator.reparentTo(render2d)

    def _createNameTag(self):

        NAME_SCALE = 0.07
        namePos = [-0.75, 0.80]

        if self.side == PLAYER_2_SIDE:
            namePos[0] *= -1

        self.nameTag = OnscreenText(text = self.name,
                                    align = TextNode.ACenter,
                                    scale = NAME_SCALE,
                                    pos = namePos
                                    )
        self.nameTag.reparentTo(render2d)


class Timer(object):
    
    def __init__(self, callback = None):
        TIMER_SCALE = 0.14
        timerPos = [0.00, 0.85]
        self.callback = callback
        self.time = 0
        self.timeTag = OnscreenText(text = str(self.time),
                                    align = TextNode.ACenter,
                                    scale = TIMER_SCALE,
                                    pos = timerPos
                                    )
        
    def start(self):
        taskMgr.doMethodLater(1, self.timerTask, 'timerTask')  
    
    def stop(self):  
        taskMgr.remove('timerTask')
        
    def setTime(self, seconds):
        self.time = seconds
        self.timeTag["text"] = str(self.time)
        
    def getTime(self, seconds):
        return self.time

    def timerTask(self,task): 
        if self.time > 0:
            self.time -= 1
            self.timeTag["text"] = str(self.time)
        else:
            if self.callback:
                self.callback()
            return
        return task.again 


#class for displaying variety of temporary messages indicating ko's
#end of rounds, combos etc. analogue using OnscreenImage 
#can be easily created
class AnimatedText(object):
    
    def __init__(self, text = "", pos = (0,0.3), time = 1.0):
        self.text = OnscreenText(text, scale = 1.0, pos = pos)
        self.text.hide()
        # hardcoded sequence of emerging, 
        # staying for a while on the screen
        # and slowly disappearing
        self.seq = Sequence(
            LerpFunc(self._easeIn, fromData=0, toData=1,
             duration=0.5, blendType='noBlend'), 
            Wait(time),
            LerpFunc(self._easeOut, fromData=0, toData=1,
             duration=0.5, blendType='noBlend'),
             Func(self.text.hide)
             )

        
    def play(self):
        self.text.show()
        self.seq.start()
    
    def _easeIn(self, t):
        self.text["fg"]= (0.0, 0.0, 0.0, t)
        self.text["scale"] = 1.0 - 0.8*t

    def _easeOut(self, t):
        t = 1-t
        self.text["fg"]= (0.0, 0.0, 0.0, t)
        self.text["scale"] = 1.0 - 0.8*t
        
    def setText(self, text):
        self.text["text"] = text
        
    def splay(self, text):
        self.text["text"] = text
        self.play()
    
class PreviewStrip(object):
    
    def __init__(self, catalog, def_height = -0.5):
        self.stripRoot = NodePath('stripRoot')
        self.height = def_height
        self.catalog = catalog
        
        self.seq = Sequence()
        
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
    
    def getStripNP(self):
        return self.stripRoot
        
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
        return abs (i - self.visible/2)
        
    def z_dist(self, i):
        return self.height
    
    # initials scaling of the visible images
    # this scaling function makes the middle one the biggest
    def scale(self, i):
        try:
            return 2.5 -  2*abs (float(i)/(self.visible-1) -  0.5)
        except:
            return 1.0
    
    def preparePositions(self):
        for i in range(0,self.visible):
            model = self.stripRoot.attachNewNode(self.generator.generate())
            model.setPos(self.x_dist(i), self.y_dist(i), self.z_dist(i))
            model.setScale(self.scale(i))
            # so that images are correctly displayed on top 
            # of each other
            model.setDepthTest(True)
            model.setDepthWrite(True)
            self.positions.append(model)
        
        # setting images    
        for i in range(len(self.positions)):
            self.positions[i].setTexture(self.textures[i])
        

    def _scaleItemInterval(self, i, dir):
        # if dir is negative item is scaled right
        # if dir is positive item is scaled left
        next = (i+dir)%len(self.positions)
        return LerpScaleInterval (
                    self.positions[i], 
                    duration = self.duration,
                    startScale = self.positions[i].getScale(),
                    scale = self.positions[next].getScale()
        )
       
    def _positionItemInterval(self, i, dir):
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

    
    def _adjustRight(self):
        first = self.positions.pop(0)
        self.head = (self.head + 1) % len(self.textures)
        self.tail = (self.tail + 1) % len(self.textures)
        first.setTexture(self.textures[self.tail])
        self.positions.append(first)
        
    
    def rotateLeft(self):
        if self.seq.isPlaying():
            return
        parallel = Parallel()
        
        for i in range(len(self.positions)):
            parallel.append( self._positionItemInterval(i, 1))
            parallel.append( self._scaleItemInterval(i, 1))
        self._adjustLeft()
        self.seq = Sequence(parallel)
        self.seq.start()

        
    def rotateRight(self):
        if self.seq.isPlaying():
            return
        parallel = Parallel()
        
        for i in range(len(self.positions)):
            parallel.append( self._positionItemInterval(i, -1))
            parallel.append( self._scaleItemInterval(i,  -1))
        self._adjustRight()
        self.seq = Sequence(parallel)
        self.seq.start()

    def current(self):
        # list is being kept the way that the middle argument in the list is always current
        return self.positions[self.visible/2]
            
    def hide(self):
        for item in self.positions:
            item.hide()
            
    def show(self):
        for item in self.positions:
            item.show()


def test():

    import direct.directbase.DirectStart
    player1Hud = PlayerHud(PLAYER_1_SIDE, 'Player 1')
    player1Hud.setHealth(80)
    player1Hud.setRoundIndicator('L V')
    player2Hud = PlayerHud(PLAYER_2_SIDE, 'Player 2')
    player2Hud.setRoundIndicator('V')
    timer = Timer()
    timer.setTime(90)
    
    at1 = AnimatedText("K.O.")

    at1.play()

    
    
    # example of how Timer which is itself only a GUI element can be used from outside
    #taskMgr.doMethodLater(1, timerTask, 'timerTask', extraArgs = [timer], appendTask = True)  
    
    run()


if __name__ == '__main__':
    test()
