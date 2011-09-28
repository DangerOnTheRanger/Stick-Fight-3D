from panda3d.core import BitMask32 ,  CollisionTraverser ,CollisionNode, CollisionRay , CollisionHandlerQueue , Vec3
from hud import PlayerHud
from fighterFsm import FighterFsm

class Fighter():
    def __init__(self,characterPath , callOnDeath , side , name = None):
        #side indicates if the player is on the left or right side.
        #TODO: add collision tests against floor and ring-out geometry in the arena, 
        
        self.side = side
        self.wins = 0 #counting won rounds, a double-ko/draw counts as win for both.
        self.faceOpp = True  #looking at opponent
        self.callOnDeath = callOnDeath
        
        self.statusBitMask = BitMask32()
        self.defenseBitMask = BitMask32()    #active defense parts get a 1
        #the attack bitmask is generated by the fsm and passed to the attack method directly
    
        if not name:
            name = "player"+str(1+bool(side))
            
        self.fighterNP = render.attachNewNode(name)
        self.collTrav = CollisionTraverser(name)
        fromObject = self.fighterNP.attachNewNode(CollisionNode('colNode'+name))
        fromObject.node().addSolid(CollisionRay(0, 0, 2,0,0, -1))
        fromObject.node().setFromCollideMask(BitMask32.bit(1))
        fromObject.node().setIntoCollideMask(BitMask32.allOff())
        self.queue = CollisionHandlerQueue()
        self.collTrav.addCollider(fromObject, self.queue)
        
        #fromObject.show() #more debug collision visuals
        #self.collTrav.showCollisions(render) #debug visuals for collision
        
        #input handler remains in the Fighter, could aswell go in fighterfsm but i moved it away from there. at will.
        self.fsm = FighterFsm(name) 
        self.fsm.setup(self,characterPath,self.side) 
        self.healthBar = PlayerHud(side, name )
        self.prepareFighter()
             
        
    def prepareFighter(self):
        taskMgr.remove("player"+str(self.side))
        self.speed = (0,0)
        self.fsm.forceTransition("Idle")
        self.health= 100
        self.healthBar.setHealth(self.health)
        self.healthBar.setRoundIndicator('V'*self.wins)
        
        if self.side:
            self.fighterNP.setX(5)
        else:
            self.fighterNP.setX(-5)
        self.fighterNP.setY(0)
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
   
    def attack(self,attackBitMask,attackrange,damageHit,damageDodge=0,angle=30): #those variables will be supplied by the fsm states later on. 
                                                             #function is pretty redundant... for structure only, and for early days
        attackstatus = self.opponent.getAttacked(attackBitMask,attackrange,damageHit,damageDodge,angle)
        return attackstatus
    
    def testHit(self,node1,node2,threshold=30, dist = 1):  #node1 which looks for a target , node2 is the target , threshold is the max-attack-angle, dist the dist
          dirVec = node1.getRelativePoint(node2,Vec3(0,0,0))
          dirVec = Vec3(dirVec[0],dirVec[1],dirVec[2])
          
          dirVec.normalize()
          angle = dirVec.angleDeg(Vec3(0,1,0))
          if angle < threshold and dist > node1.getDistance(node2):
            #print "hit at "+str(angle)+" degree!"
            return True
          else:
            #print angle,node1.getDistance(node2)
            return False
        
    def getAttacked(self,attackBitMask,attackrange,damageHit,damageDodge=0,angle = 30):
        """
        returns 0 if not hit, 1 if hit was blocked, 2 if hit, 3 for hit+KO 
        """
        if self.health <=0:
            return 4 #player is ko already
            

        if  not self.testHit(self.opponent.getNP(),self.fighterNP  ,angle,attackrange )  : #instead of 0, a sligtly positive values makes thinks look better.
            #attack misses due to out of range.
            return 0 

        if (self.statusBitMask & attackBitMask).getWord() == 0: # attak misses cause the player avoided it. went low or so.
            return 0
  
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
                taskMgr.doMethodLater(0.5,self.callOnDeath,"RoundEnd") 
                return 3
            #TODO: requesting the same state as you are in doesnt work well.sorta need to re-enter the hit state
            if "Crouch" in self.fsm.state:
                self.fsm.forceTransition("CrouchHit")
            elif self.fsm.state:
                self.fsm.forceTransition("Hit")
            return 2 #regular hit
    
    def setSpeed(self,x,y):
        self.speed = (x,y)
    
    def faceOpponent(self,facing):
        self.faceOpp = facing #true if yuo look at the other player (usualy true unless attacking), so you can dodge an attack by evading.
    
    def __playertask__(self,task):
        
        oldpos = self.fighterNP.getPos()
        
        dist = self.fighterNP.getY(self.opponent.getNP()) 

        if dist > 3 or self.speed[0]<0: #prevert players from walking throug each other , too troublesome atm
            self.fighterNP.setX(self.fighterNP,self.speed[1]*globalClock.getDt())
            self.fighterNP.setY(self.fighterNP,self.speed[0]*globalClock.getDt())
        else :
            self.speed = ( min(2,self.speed[0] ), self.speed[1])
            #also push back other player
            self.opponent.getNP().setY(self.opponent.getNP(),-self.speed[0]*globalClock.getDt() )
            
        self.collTrav.traverse(render)
        self.queue.sortEntries()
        for i in range(self.queue.getNumEntries()):
            entry = self.queue.getEntry(i)
            if "ground" in entry.getIntoNodePath().getName() :
                break
            if "out" in entry.getIntoNodePath().getName() :
                pass #ring out
                self.fighterNP.setPos(oldpos) #for now reset him as we have no ring-out anim yet #TODO: add ring out anim!
                break
            
        if self.queue.getNumEntries() == 0:
            #if there is no ground and no ring out, propably a wall or no thin like that. just reset the pos     
            self.fighterNP.setPos(oldpos)
            print "resetting fighter"
            
        if self.faceOpp:
            self.fighterNP.lookAt(self.opponent.getNP())      
                
        return task.cont

