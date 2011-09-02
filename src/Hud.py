from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode
from direct.task import Task


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
    
    # example of how Timer which is itself only a GUI element can be used from outside
    taskMgr.doMethodLater(1, timerTask, 'timerTask', extraArgs = [timer], appendTask = True)  
    
    run()


if __name__ == '__main__':
    test()
