from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode
from direct.task import Task
from direct.interval.LerpInterval import LerpFunc
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import TransparencyAttrib
from os import sep

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
    
# similar to above but offering to animate images instead
class AnimatedImage(object):
    
    def __init__(self, directory, pad = 4, position = (0,0.1,0.3), time = 1.0):
        self.anim = OnscreenImage(image = directory + sep + directory + "0"*pad + ".png", 
                                    pos = position)
        
        self.textures = self._loadTextureMovie(24, directory + sep + directory,'png', padding = pad)
        self.fps = 25

        self.anim.hide()

        self.seq = Sequence(
            Parallel(LerpFunc(self._easeOut, fromData=0, toData=1,
             duration=1.5, blendType='noBlend'), 
            LerpFunc(self._animate, fromData=0, toData=1,
             duration=1.5, blendType='noBlend')),
             Func(self.anim.hide)
             )

        
    def play(self):
        self.anim.show()
        self.seq.start()
    
    def _easeIn(self, t):
        self.anim["image"]
        self.anim["scale"] = 1.0 - 0.8*t

    def _animate(self, t):
        currentFrame = int(t * self.fps)
        self.anim["image"] = self.textures[currentFrame % len(self.textures)]
        self.anim.setTransparency(TransparencyAttrib.MAlpha)

    def _easeOut(self, t):
        t = 1-t
        self.anim["scale"] = 0.5 - 0.1*t
        
          
    
    def _loadTextureMovie(self, frames, name, suffix, padding = 1):
        return [loader.loadTexture((name+"%0"+str(padding)+"d."+suffix) % i) 
            for i in range(frames)]



# only a test function



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
    at = AnimatedImage("explosion")
    at1.play()
    at.play()
    
    
    # example of how Timer which is itself only a GUI element can be used from outside
    #taskMgr.doMethodLater(1, timerTask, 'timerTask', extraArgs = [timer], appendTask = True)  
    
    run()


if __name__ == '__main__':
    test()
