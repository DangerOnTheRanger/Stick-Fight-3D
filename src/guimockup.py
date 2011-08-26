from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode


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
        # TODO
        pass

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


def test():

    import direct.directbase.DirectStart
    player1Hud = PlayerHud(PLAYER_1_SIDE, 'Player 1')
    player1Hud.setHealth(80)
    player2Hud = PlayerHud(PLAYER_2_SIDE, 'Player 2')
    run()


if __name__ == '__main__':
    test()
