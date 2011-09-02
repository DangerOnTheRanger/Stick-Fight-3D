from direct.fsm.FSM import FSM
from direct.actor.Actor import Actor

from direct.interval.MetaInterval import Sequence,Parallel
from direct.interval.FunctionInterval import Func,Wait
from direct.interval.SoundInterval import SoundInterval

from panda3d.core import BitMask32

from random import choice

#TODO: adding states for all animations, an before and after round state ,etc.. this pretty much is the core of the game.

class FighterFsm(FSM):  #inherits from direct.fsm.FSM
                    ##this class has to be written for each character in the game 
                    ####unfortunately that much coding per char is required until we can autogenerate based on artists input
                    ## i am not sure where to put the fighter actor. logically it belongs to the fighter class, but the fsm does a lot more with it.
                    ## guess it will end up in the fsm as this is the file created for each fighter individually.
                    ## or if we should inherit Fighter from FSM and simply stuff everything in there wich would be bad cause we copy all shared code around
   
        
    def setup(self,FighterClassInstance,inputHandlerInstance,side):
        self.inputHandler = inputHandlerInstance
        path = "../assets/models/stickdummy01/export/"
        self.fighter = Actor(path+'stickfigure', 
                                        {
                                          'rpunch'      :path+'stickfigure-r_punch',
                                          'lpunch'      :path+'stickfigure-l_punch',
                                          'hit'         :path+'stickfigure-hit'    ,
                                          'defense'     :path+'stickfigure-defense',
                                          'idle'        :path+'stickfigure-idle'   ,
                                          'kick'        :path+'stickfigure-kick'   ,
                                          'run'         :path+'stickfigure-run'    ,
                                          'step'        :path+'stickfigure-step'   ,
                                          'ko'          :path+'stickfigure-ko'     ,
                                          'round-kick'  :path+'stickfigure-round-kick'

                                        })
        #model was rotated the wrong way in blender.. darn fixing it
        self.fighter.setH(180)
        self.fighter.flattenMedium()                           
        self.fighter.reparentTo(render)
        self.fighter.setBlend(frameBlend=True)
        
        self.fighterinstance = FighterClassInstance
        self.fighter.reparentTo(self.fighterinstance.getNP())
        self.activeInterval = None #we will store our active sequence,parallel or interval here, so we can easily clean it up 
        self.transitionTimer = None #usually holds a sequence like sequence(Wait(time),self.request('nextstate'))
        
        #loading sounds... could go in an extra-file
        path = "../assets/sounds/"
        self.hitsounds = []
        self.misssounds = []
        self.blocksounds = []

        for x in range(1,6):        
            Sound = loader.loadSfx(path+"hit/hit"+str(x)+".wav")
            self.hitsounds.append( SoundInterval(
                                    Sound,
                                    loop = 0,
                                    volume =1.0,
                                    )
                                 )                                                       
        for x in range(1,4):        
            Sound = loader.loadSfx(path+"block/block"+str(x)+".wav")
            self.blocksounds.append( SoundInterval(
                                    Sound,
                                    loop = 0,
                                    volume =1.0,
                                    )
                                 )    
        
        for x in range(1,7):        
            Sound = loader.loadSfx(path+"miss/miss"+str(x)+".wav")
            self.misssounds.append( SoundInterval(
                                    Sound,
                                    loop = 0,
                                    volume =1.0,
                                    )
                                 )
        self.request("Idle")
    
    def mapEvent(self,eventNr,event,activeevents=[]):
        """
        convenience function
        """
        self.inputHandler.mapEvent(self,eventNr,event,activeevents)
        
    def clearMapping(self):
        """
        another convenience function
        """
        self.inputHandler.clearMapping()
   
    def setSBM(self,bitmask):
        """
        yet another convenience function, sets the status bit mask
        """
        self.fighterinstance.setStatusBitMask(bitmask)
        
    def setDBM(self,bitmask):
        """
        aaand yet another convenience function, sets the defense bit mask
        """
        self.fighterinstance.setDefenseBitMask(bitmask)    
            
    def attack(self,attackBitMask,attackrange,damageHit,damageDodge=0):
        """
        more convenience function, this one attacks the opponent
        """
        hit = self.fighterinstance.attack(attackBitMask,attackrange,damageHit,damageDodge)
        if hit == 0:
            choice(self.misssounds).start()
        elif hit == 1:
            choice(self.blocksounds).start()
        elif hit == 2:
            choice(self.hitsounds).start()
        elif hit == 3:
            #the other player went ko , go to win-state
            choice(self.hitsounds).start()
        elif hit == 4:
            pass
            #the other player is ko already..    

    def cancelActive(self,task=0):
        if self.activeInterval:
            self.activeInterval.remove()
            self.activeInterval = None
            
    #----------
    def enterKo(self):
        taskMgr.doMethodLater(0.2,self.cancelActive,"cancelActive") #timer to allow double-KO
        self.clearMapping()
        self.fighter.play("ko")
    def filterKo(self,request,args):
        #this blocks the fsm. but will be forced to idle by the fighter class
        return
    def exitKo(self):
        pass
          
    #-----------
    def enterHit(self):
        self.clearMapping()
        self.fighter.play("hit")
        self.transitionTimer= Sequence(Wait(self.fighter.getDuration()), Func(self.request,"Idle" ) )
        self.transitionTimer.start()
   
    def exitHit(self):
        self.clearMapping()
        self.transitionTimer = None
        self.activeInterval = None
    #------------
    def enterIdle(self):
        #self.fighterinstance.setSpeed(0,0)
        newBitMask = BitMask32()
        newBitMask.setRange(0,3)
        self.setSBM(newBitMask)
        self.fighter.loop("idle")
        self.mapEvent( 3, "Step")
        self.mapEvent( 4, "Run")
        self.mapEvent( 5, "RPunch" )
        self.mapEvent( 5, "LPunch", [2])
        self.mapEvent( 6, "Kick" )  
        self.mapEvent( 7, "Defense" )
        Func(self.inputHandler.pollEvents).start() #slightly hacky but we cant call that WITHIN the transition of entering idle. so it will be called next frame.
        #doesnt look logic but saves craploads of uncool code, trust me
        
    def exitIdle(self):
        #self.fighterinstance.setSpeed(0,0) #cant hurt
        self.transitionTimer = None
        self.activeInterval = None
        self.clearMapping()
    
    
     #-------------------------
    def enterStep(self):
        self.fighter.loop("step")
        self.fighter.setPlayRate(-1,"step")
        self.fighterinstance.setSpeed(-4.69 ,0)
        self.mapEvent(-3, "Idle")
        self.mapEvent( 5, "RPunch",[3]) #we would not hit unless we add the key. might need a fix^^
        self.mapEvent( 6, "Kick"  ,[3] )  
    
    def exitStep(self):
        self.fighter.stop()
        self.fighterinstance.setSpeed(0 ,0)
        self.clearMapping()
    
    #-------------------------
    def enterRun(self):
        self.fighter.loop("run")
        self.fighterinstance.setSpeed(20.23 ,0)
        self.mapEvent(-4, "Idle")
        self.mapEvent( 5, "RPunch",[4]) #we would not hit unless we add the key. might need a fix^^
        self.mapEvent( 6, "Kick"  ,[4] )  
    
    def exitRun(self):
        self.fighter.stop()
        self.fighterinstance.setSpeed(0 ,0)
        self.clearMapping()
    
    #-------------------------
    #example of a punch, wich default returns to idle, if no buttons are pressed. also blocks button presses/requests until short befor the end. 
    #at the end it is possible to transition to any legal state we defined earlier 
    def enterRPunch(self):
        #self.fighterinstance.setSpeed(0,0) #just for illustration
        self.fighter.stop()
        self.fighter.play('rpunch')
        self.transitionTimer= Sequence(Wait(self.fighter.getDuration()), Func(self.request,"Idle" ) )
        self.transitionTimer.start() 
        attackMask = BitMask32()
        attackMask.setBit(2)
        self.activeTimer = Sequence( Wait(0.12),
                                     Func(self.attack,attackMask,6,5 ) #attack, bitmasks, range, damage
                                   )
        self.activeTimer.start()
        
        self.mapEvent(5,"LPunch") #allows us to combo a punch followed by a kick.

    def filterRPunch(self,request,args):
        if self.transitionTimer.getT() > self.transitionTimer.getDuration()-0.2 :  #allow player to hit the next strike 0.2 to 0 seconds befor the animation finished
            return request

    def exitRPunch(self):
        self.transitionTimer = None
        self.activeInterval = None
        self.clearMapping()
        pass
        

    #---------------------------
   
    def enterLPunch(self):
        #self.fighterinstance.setSpeed(0,0) #just for illustration
        self.fighter.stop()
        self.fighter.play('lpunch')
        self.transitionTimer= Sequence(Wait(self.fighter.getDuration()), Func(self.request,"Idle" ) )
        self.transitionTimer.start()
        attackMask = BitMask32()
        attackMask.setBit(2)
        self.activeTimer = Sequence( Wait(0.12),
                                     Func(self.attack,attackMask,6,5 ) #attack, bitmasks, range, damage
                                   )
        self.activeTimer.start()
        self.mapEvent(5,"RPunch")

    def filterLPunch(self,request,args):
        if self.transitionTimer.getT() > self.transitionTimer.getDuration()-0.2 :  #allow player to hit the next strike 0.2 to 0 seconds befor the animation finished
            return request

    def exitLPunch(self):
        self.transitionTimer = None
        self.activeInterval = None
        self.clearMapping()
        
    #--------------------------------    
        
    def enterKick(self):
        self.fighter.stop()
        self.fighter.play('kick')
        self.transitionTimer= Sequence(Wait(self.fighter.getDuration()), Func(self.request,"Idle" ) )
        self.transitionTimer.start()
        attackMask = BitMask32()
        attackMask.setBit(2)
        self.activeTimer = Sequence( Wait(0.16),
                                     Func(self.attack,attackMask,6,10,2 ) #attack, bitmasks, range, damage, dodgedamage
                                   )
        self.activeTimer.start()

    def filterKick(self,request,args):
        if self.transitionTimer.getT() > self.transitionTimer.getDuration()-0.2 : 
            return request

    def exitLPunch(self):
        self.transitionTimer = None
        self.activeInterval = None
        self.clearMapping()
  
    #-----------------  

    def enterDefense(self):
        newBitMask = BitMask32()
        newBitMask.setBit(1)
        newBitMask.setBit(2)
        self.setDBM(newBitMask)
        
        self.fighter.stop()
        self.fighter.loop('defense')
        self.mapEvent(-7,"Idle")


    def exitDefense(self):
        newBitMask = BitMask32()
        self.setDBM(newBitMask)
        self.transitionTimer = None
        self.activeInterval = None
        self.clearMapping()
        
    #-----------------    
