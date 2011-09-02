from panda3d.core import BitMask32
from Hud import PlayerHud
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
        
        self.fsm = FighterFSM(name)
        self.fsm.setup(self,keymap,self.side)
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
        #request a win-anim from the fsm if there are any , be sure to filter out that one if the player is KO
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
        print 'attacking'
        self.opponent.getAttacked(attackBitMask,attackrange,damageHit,damageDodge)
        
    def getAttacked(self,attackBitMask,attackrange,damageHit,damageDodge=0): #the equivalent
        print "getting attacked!!"
        if self.health<0:
            return 0 #catch the event that the player is dead already. the forceTransition Hit made trouble
        dist = self.fighterNP.getY(self.opponent.getNP()) 
        if  dist > attackrange or dist < 0   :
            #attack misses due to out of range.
            print "missed due to long distance"
            return 0 

        if self.statusBitMask & attackBitMask == 0: # attak misses cause the player avoided it. went low or so.
            print "attack missed, no bitmask match"
            return 0
            
        print (self.defenseBitMask & attackBitMask).getWord()    
        if (self.defenseBitMask & attackBitMask).getWord():
            
            print "attack got dodged"
            self.health -= damageDodge
            self.healthBar.setHealth(self.health)
            #set health down by damageDodge if any.
            #set fsm so it goes into the right anim and so on
            return 1 #hit,... but blocked so no combos 
            
        else:
            print "hit it!"
            self.health -= damageHit
            self.healthBar.setHealth(self.health)
            self.fsm.forceTransition("Hit")
            #draw health
            #set fsm state.
            print self.health
            return 2 #in ya face .... smash.
    
    def setSpeed(self,x,y):
        self.speed = (x,y)
         #player motion should go here i guess, if the fsm provide any smarter way to do that disregard this definition.
        #checking for players health. couldbe done in getAttacked but that would propably break the last animation on the attacker side.
        #setx, sety 
        
    def __playertask__(self,task):
        if self.health <= 0:
            taskMgr.remove("ko-task")
            taskMgr.doMethodLater(0.2,self.callOnDeath,name="ko-task") #allow 0.2 seconds for double ko
            self.fsm.forceTransition("Ko")
            return
        self.fighterNP.setX(self.fighterNP,self.speed[1]*globalClock.getDt())
        self.fighterNP.setY(self.fighterNP,self.speed[0]*globalClock.getDt()) 
        return task.cont

