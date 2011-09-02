from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import Func,Wait
from Hud import Timer
from Fighter import Fighter
class Match():
    def __init__(self, Character1, Character2, keymapPlayer1,keymapPlayer2,roundTime=90,name1="Player1",name2="Player2"):
        ###character 1 and 2 are strings pointing to the assets with the character. will be delivered by the character-selection screen.
        ### till we have the selection screen, hardcode or default them.
        
        #arena = #... load the arena here, be sure to set propper bitmasks on the floor and ring-out geometry
        self.arena = loader.loadModel('../assets/models/floortile/floortile')
        self.arena.reparentTo(render)
        self.arena.setScale(4)
        
        self.player1 = Fighter(Character1, self.roundEnd, 0, keymapPlayer1 ,name=name1 )
        self.player2 = Fighter(Character2, self.roundEnd, 1, keymapPlayer2 ,name=name2 )
        
        self.player1.setOpponent(self.player2)
        self.player2.setOpponent(self.player1)
        
        self.roundTime=roundTime
        self.timer = Timer(self.roundEnd)
        self.roundStart()
    
    def roundStart(self,task=None):
        self.player1.prepareFighter()
        self.player2.prepareFighter()
        self.timer.setTime(self.roundTime)
        self.timer.start()
        self.roundEnded = False
                
    def roundEnd(self,task=None):
        if self.roundEnded:
            return
        else:
            self.roundEnded = True
        self.timer.stop()
        #double ko would require a variable like roundOver.
        #short delay to allow double ko. 
        if self.player1.getHealth()<0 and self.player2.getHealth() < 0:
            #double knockout.
            self.player1.fighterWin()
            self.player2.fighterWin()
            
        elif self.player2.getHealth() > self.player1.getHealth():
            self.player2.fighterWin()
            #player2 wins
        elif self.player2.getHealth() < self.player1.getHealth():
            self.player1.fighterWin()
        else:
            #both players with the same health??? W T F ??
            pass
            
        
        
        print self.player1.getWins(),self.player2.getWins()
        if self.player1.getWins() >=3 and self.player2.getWins() >=3:
            #match ended in a draw
            self.endMatch()
            return
        elif self.player1.getWins() >=3:
            #player1 wins
            self.endMatch()
            return
        elif self.player2.getWins() >=3 :
            #player2 wins
            self.endMatch()
            return
        else:
            #in case of double time-up we need to disable inputs of the player till the next round starts.
            pass
        
        taskMgr.doMethodLater(3,self.roundStart,"startRound")
            
        #update the round-wins gui. display guistuff, play win animation on chars, do whatever you like..
        #reset the char healt,reset the positions and fsm states, then let the fun go on.
        #eventually clear the round-end variable.
        #if one player has 3 wins. end match
 
    def endMatch(self):
        print "match ended!"
        #preferably show splashscreen till the menu has loaded
        #remove players and the arena.

