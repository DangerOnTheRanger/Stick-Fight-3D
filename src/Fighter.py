from panda3d.core import BitMask32
from Hud import PlayerHud
from FighterFsm import FighterFsm
from InputHandler import InputHandler
class Fighter():
    def __init__(self,characterPath , callOnDeath , side , keymap, name = None):
        #side indicates if the player is on the left or right side.
        
        
        self.side = side
        
        self.wins = 0 #counting won rounds, a doubleko/draw counts as win for both.
        
        self.callOnDeath = callOnDeath
        self.statusBitMask = BitMask32()
        self.defenseBitMask = BitMask32()    #active defense parts get a 1
        #the attack bitmask is generated by the fsm and passed to attack right away
        
        if not name:
            name = "player"+str(1+bool(side))
        self.fighterNP = render.attachNewNode(name)
        
        self.inputHandler = InputHandler(keymap,self.side)
        self.fsm = FighterFsm(name)
        self.fsm.setup(self,self.inputHandler,self.side)
        self.healthBar = PlayerHud(side, name )
        self.prepareFighter()
    
    def prepareFighter(self):
        taskMgr.remove("player"+str(self.side))
        self.speed = (0,0)
        self.fsm.forceTransition("Idle")
        print "preparing for new round"
        self.health= 100
        self.healthBar.setHealth(self.health)
        self.healthBar.setRoundIndicator('V'*self.wins)
        
        if self.side:
            self.fighterNP.setX(5)
        else:
            self.fighterNP.setX(-5)
            
        taskMgr.add(self.__playertask__, "player"+str(self.side))
    
    def setStatusBitMask(self,bitmask):
        self.statusBitMask = bitmask
        
    def setDefenseBitMask(self,bitmask):
        self.defenseBitMask = bitmask 
   
    #getters and setters are a bit stupid here. properties from python 3 would be nice
    def fighterWin(self):
        #request a win-anim from the fsm if there are any
        self.wins += 1
        self.healthBar.setRoundIndicator('V'*self.wins)
    
    def getWins(self):
        return self.wins   
    
    def getHealth(self):
        return self.health
        
    def getNP(self):
        return self.fighterNP

    def setOpponent(self,opponent):
        self.opponent = opponent
        self.fighterNP.lookAt(self.opponent.getNP())
   
    def attack(self,attackBitMask,attackrange,damageHit,damageDodge=0): #those variables will be supplied by the fsm states later on. 
                                                             #function is pretty redundant... for structure only, and for early days
        attackstatus = self.opponent.getAttacked(attackBitMask,attackrange,damageHit,damageDodge)
        return attackstatus
        
    def getAttacked(self,attackBitMask,attackrange,damageHit,damageDodge=0):
        """
        returns 0 if not hit, 1 if hit was blocked, 2 if hit, 3 for hit+KO 
        """
        if self.health <=0:
            return 4 #player is ko already
        dist = self.fighterNP.getY(self.opponent.getNP()) 
        if  dist > attackrange or dist < 0   :
            #attack misses due to out of range.
            return 0 

        if self.statusBitMask & attackBitMask == 0: # attak misses cause the player avoided it. went low or so.
            return 0
            
        print (self.defenseBitMask & attackBitMask).getWord()    
        if (self.defenseBitMask & attackBitMask).getWord():
            self.health -= damageDodge
            self.healthBar.setHealth(self.health)
            return 1 #hit,... but blocked so no combos 
            
        else:
            self.health -= damageHit
            self.healthBar.setHealth(self.health)
            if self.health <= 0 : #if KO
                taskMgr.remove("player"+str(self.side))
                self.fsm.forceTransition("Ko")
                #actually make the match.py allow the other player to KO (in case of doubleKO,befor calling round end.
                taskMgr.doMethodLater(0.2,self.callOnDeath,"RoundEnd") 
                return 3
            self.fsm.forceTransition("Hit")
            return 2 #regular hit
    
    def setSpeed(self,x,y):
        self.speed = (x,y)
 
    def __playertask__(self,task):
        self.fighterNP.setX(self.fighterNP,self.speed[1]*globalClock.getDt())
        self.fighterNP.setY(self.fighterNP,self.speed[0]*globalClock.getDt()) 
        return task.cont

