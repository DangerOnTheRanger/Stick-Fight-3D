from direct.fsm.FSM import FSM
from direct.actor.Actor import Actor

from direct.interval.MetaInterval import Sequence,Parallel
from direct.interval.FunctionInterval import Func,Wait
from direct.interval.SoundInterval import SoundInterval

from panda3d.core import BitMask32
from inputHandler import InputHandler
from playerSoundFX import PlayerSoundFX


#TODO: adding states for all animations, an before and after round state ,etc.. this pretty much is the core of the game.

class FighterFsm(FSM):  #inherits from direct.fsm.FSM
                    ##this class has to be written for each character in the game 
                    ####unfortunately that much coding per char is required until we can autogenerate based on artists input
                    ## i am not sure where to put the fighter actor. logically it belongs to the fighter class, but the fsm does a lot more with it.
                    ## guess it will end up in the fsm as this is the file created for each fighter individually.
                    ## or if we should inherit Fighter from FSM and simply stuff everything in there wich would be bad cause we copy all shared code around
                    #bitmasks are 0 for on the floor, 1 for legs, 2 for torso&head , 
                    #3 for vertical down (like hammer smackdown, bodyslam form the back of a horse, meteroids...)
        
    def setup(self,FighterClassInstance,side):
        self.inputHandler = InputHandler(self,side)
        path = "../assets/models/stickdummy01/export/"
        self.fighter = Actor(path+'stickfigure', 
                                        { 
                                          'idle'        :path+'stickfigure-idle'   ,
                                          'jump'        :path+'stickfigure-jump', 
                                          'crouch'      :path+'stickfigure-crouch-idle',                                      
                                          'runIn'       :path+'stickfigure-run'    ,
                                          'runOut'      :path+'stickfigure-step'   ,
                                          'punch'       :path+'stickfigure-r_punch',
                                          'hit'         :path+'stickfigure-hit'    ,
                                          'defense'     :path+'stickfigure-defense',
                                          'kick'        :path+'stickfigure-kick'   ,
                                          'ko'          :path+'stickfigure-ko'     ,
                                          'crouch-punch':path+'stickfigure-crouch-punch',       
                                          'crouch-kick' :path+'stickfigure-crouch-kick', 
                                          'crouch-defense':path+'stickfigure-crouch-defense', 
                                          'crouch-hit'  :path+'stickfigure-crouch-hit', 
                                          'jump-in'     :path+'stickfigure-jump-forward', 
                                          'jump-out'     :path+'stickfigure-jump-backward', 
                                          #'round-kick'  :path+'stickfigure-round-kick',
                                          #'side-step'   :path+'stickfigure-side-step'

                                        })
        #model was rotated the wrong way in blender.. darn fixing it
        self.fighter.setH(180)
        self.fighter.flattenMedium()                           
        self.fighter.reparentTo(render)
        self.fighter.setBlend(frameBlend=True)
        
        self.fighterinstance = FighterClassInstance
        self.fighter.reparentTo(self.fighterinstance.getNP())
        self.activeTimer = None #we will store our active sequence,parallel or interval here, so we can easily clean it up 
        self.transitionTimer = None #usually holds a sequence like sequence(Wait(time),self.request('nextstate'))
        
        #loading sounds... could go in an extra-file
        self.sounds = PlayerSoundFX()
                                 
        self.request("Idle")
    
   
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
            self.sounds.playMiss()
        elif hit == 1:
            self.sounds.playBlock()
        elif hit == 2:
            self.sounds.playHit()
        elif hit == 3:
            #the other player went ko , go to win-state
            self.sounds.playHit()
        elif hit == 4:
            pass
            #the other player is ko already..    
            #we still miss the hit
            self.sounds.playMiss()
    #----------
    def stand(self):
        newBitMask = BitMask32()
        newBitMask.setRange(0,3)
        self.setSBM(newBitMask)
    #-----------
    def crouch(self):
        newBitMask = BitMask32()
        newBitMask.setRange(0,1)
        newBitMask.setBit(3)
        self.setSBM(newBitMask)
        
    #-----------
    def cancelTransition(self,task=0):
        if self.transitionTimer:
            self.transitionTimer.pause()
            self.transitionTimer
    #-----------
    def cancelActive(self,task=0):
        if self.activeTimer:
            self.activeTimer.pause()
            self.activeTimer = None
    
    #----------
    def enterKo(self):
        taskMgr.doMethodLater(0.2,self.cancelActive,"cancelActive") #timer to allow double-KO
        newBitMask = BitMask32()
        self.setSBM(newBitMask)
        self.fighter.play("ko")
    def filterKo(self,request,args):
        #this blocks the fsm. but will be forced to idle by the fighter class
        return
    def exitKo(self):
        pass
          
    #-----------
    def enterHit(self):
        self.stand()
        self.fighter.play("hit")
        self.fighterinstance.setSpeed(-1,0)
        self.transitionTimer= Sequence(Wait(self.fighter.getDuration()), Func(self.inputHandler.pollEvents ) )
        self.transitionTimer.start()
    
    def filterHit(self,request,options):
        if self.transitionTimer.getT() > self.transitionTimer.getDuration()-0.1 :  #allow player to hit the next strike back
            return request
   
    def exitHit(self):
        self.fighterinstance.setSpeed(0,0)
        self.cancelTransition()
        self.cancelActive()
        
    #-------------------------

    def enterCrouchHit(self):
        self.crouch()
        self.fighter.play("crouch-hit")
        self.fighterinstance.setSpeed(-1,0)
        self.transitionTimer= Sequence(Wait(self.fighter.getDuration()), Func(self.inputHandler.pollEvents ) )
        self.transitionTimer.start()
    
    def filterCrouchHit(self,request,options):
        if self.transitionTimer.getT() > self.transitionTimer.getDuration()-0.1 :  #allow player to hit the next strike back
            return request
   
    def exitCrouchHit(self):
        self.fighterinstance.setSpeed(0,0)
        self.cancelTransition()
        self.cancelActive() 

    #---------
    
    def enterDefense(self):
        self.stand()
        newBitMask = BitMask32()
        #newBitMask.setBit(1)
        newBitMask.setBit(2)
        self.setDBM(newBitMask)
        self.fighter.stop()
        self.fighter.loop('defense')

    def filterDefense(self,request,options):
        if request != "Defense":
            return request

    def exitDefense(self):
        newBitMask = BitMask32()
        self.setDBM(newBitMask)
        self.cancelTransition()
        self.cancelActive()

    #---------

    def enterRunIn(self):
        self.stand()
        self.fighter.loop("runIn")
        self.fighterinstance.setSpeed(20.23 ,0)
        
    def filterRunIn(self,request,options):
        if request != "RunIn":
            return request

    def exitRunIn(self):
        self.fighter.stop()
        self.fighterinstance.setSpeed(0 ,0)
    
    #---------------------
     
    def enterRunOut(self):
        self.stand()
        self.fighter.loop("runOut")
        self.fighterinstance.setSpeed(-4.41 ,0)
        
    def filterRunOut(self,request,options):
        if request != "RunOut":
            return request

    def exitRunOut(self):
        self.fighter.stop()
        self.fighterinstance.setSpeed(0 ,0)
    
    
        #---------------------
    def enterJumpIn(self):
        self.fighterinstance.faceOpponent(False)
        self.fighter.stop()
        self.fighter.play('jump-in')
        self.fighterinstance.setSpeed(7.92,0)
        #TODO:add a parallele here, modifying the bitmasks during jump
        #till then. jump all the time
        newBitMask = BitMask32()
        newBitMask.setRange(2,3)
        self.setSBM(newBitMask)
        
        self.transitionTimer= Sequence(Wait(self.fighter.getDuration()), Func(self.inputHandler.pollEvents ) )
        self.transitionTimer.start()

    def filterJumpIn(self,request,args):
        if self.transitionTimer.getT() > self.transitionTimer.getDuration()-0.1 :  #allow player to hit the next strike 0.2 to 0 seconds befor the animation finished
            return request

    def exitJumpIn(self):
        self.stand()
        self.fighterinstance.setSpeed(0,0)
        self.fighterinstance.faceOpponent(True)
        self.cancelTransition()
        
     
        #---------------------
    def enterJumpOut(self):
        self.fighterinstance.faceOpponent(False)
        self.fighter.stop()
        self.fighter.play('jump-out')
        self.fighterinstance.setSpeed(-7.92,0)
        #TODO:add a parallele here, modifying the bitmasks during jump
        #till then. jump all the time
        newBitMask = BitMask32()
        newBitMask.setRange(2,3)
        self.setSBM(newBitMask)
        
        self.transitionTimer= Sequence(Wait(self.fighter.getDuration()), Func(self.inputHandler.pollEvents ) )
        self.transitionTimer.start()

    def filterJumpOut(self,request,args):
        if self.transitionTimer.getT() > self.transitionTimer.getDuration()-0.1 :  #allow player to hit the next strike 0.2 to 0 seconds befor the animation finished
            return request

    def exitJumpOut(self):
        self.stand()
        self.fighterinstance.setSpeed(0,0)
        self.fighterinstance.faceOpponent(True)
        self.cancelTransition()   
        
    #---------------------
    def enterJump(self):
        self.fighterinstance.faceOpponent(False)
        self.fighter.stop()
        self.fighter.play('jump')
        #TODO:add a parallele here, modifying the bitmasks during jump
        #till then. jump all the time
        newBitMask = BitMask32()
        newBitMask.setRange(2,3)
        #newBitMask.setBit(3)
        self.setSBM(newBitMask)
        
        self.transitionTimer= Sequence(Wait(self.fighter.getDuration()), Func(self.inputHandler.pollEvents ) )
        self.transitionTimer.start()

    def filterJump(self,request,args):
        if self.transitionTimer.getT() > self.transitionTimer.getDuration()-0.1 :  #allow player to hit the next strike 0.2 to 0 seconds befor the animation finished
            return request

    def exitJump(self):
        self.stand()
        self.fighterinstance.faceOpponent(True)
        self.cancelTransition()

    #------------
    
    def enterIdle(self):
        #self.fighterinstance.setSpeed(0,0)
        self.stand()
        self.fighter.loop("idle")
        Func(self.inputHandler.pollEvents).start() #slightly hacky but we cant call that WITHIN the transition of entering idle. so it will be called next frame.
        #doesnt look logic but saves craploads of uncool code, trust me
    
    def filterIdle(self,request,options):
        if request != "Idle":
            return request
        
    def exitIdle(self):
        #self.fighterinstance.setSpeed(0,0) #cant hurt
        self.cancelTransition()
        self.cancelActive()
        
        
    #------------
    
    def enterCrouch(self):
        self.crouch()
        #self.fighterinstance.setSpeed(0,0)
        self.fighter.loop("crouch")
        #Func(self.inputHandler.pollEvents).start() #slightly hacky but we cant call that WITHIN the transition of entering idle. so it will be called next frame.
        #doesnt look logic but saves craploads of uncool code, trust me
    
    def filterCrouch(self,request,options):
        if request != "Crouch":
            return request
        
    def exitCrouch(self):
        #self.fighterinstance.setSpeed(0,0) #cant hurt
        pass
    
     #---------------
    
    def enterCrouchPunch(self):
        self.crouch()
        self.fighterinstance.faceOpponent(False)
        self.fighter.stop()
        self.fighter.play('crouch-punch')
        self.transitionTimer= Sequence(Wait(self.fighter.getDuration()), Func(self.inputHandler.pollEvents ) )
        self.transitionTimer.start() 
        attackMask = BitMask32()
        attackMask.setBit(1)
        self.activeTimer = Sequence( Wait(0.12),
                                     Func(self.attack,attackMask,5,5 ) #attack, bitmasks, range, damage
                                   )
        self.activeTimer.start()


    def filterCrouchPunch(self,request,args):
        if self.transitionTimer.getT() > self.transitionTimer.getDuration()-0.2 :  #allow player to hit the next strike 0.2 to 0 seconds befor the animation finished
            return request

    def exitCrouchPunch(self):
        self.fighterinstance.faceOpponent(True)
        self.cancelTransition()
        self.cancelActive()
    #---------------
    
    def enterCrouchKick(self):
        self.crouch()
        self.fighterinstance.faceOpponent(False)
        self.fighter.stop()
        self.fighter.play('crouch-kick')
        self.transitionTimer= Sequence(Wait(self.fighter.getDuration()), Func(self.inputHandler.pollEvents ) )
        self.transitionTimer.start() 
        attackMask = BitMask32()
        attackMask.setBit(1)
        self.activeTimer = Sequence( Wait(0.12),
                                     Func(self.attack,attackMask,6.5,5 ) #attack bitmask, range, damage
                                   )
        self.activeTimer.start()


    def filterCrouchKick(self,request,args):
        if self.transitionTimer.getT() > self.transitionTimer.getDuration()-0.2 :  #allow player to hit the next strike 0.2 to 0 seconds befor the animation finished
            return request

    def exitCrouchKick(self):
        self.fighterinstance.faceOpponent(True)
        self.cancelTransition()
        self.cancelActive()
 #-------------------------
     


    def enterCrouchDefense(self):
        self.crouch()
        newBitMask = BitMask32()
        newBitMask.setBit(1)
        #newBitMask.setBit(2)
        self.setDBM(newBitMask)
        self.fighter.stop()
        self.fighter.loop('crouch-defense')

    def filterCrouchDefense(self,request,options):
        if request != "CrouchDefense":
            return request

    def exitCrouchDefense(self):
        newBitMask = BitMask32()
        self.setDBM(newBitMask)
        self.cancelTransition()
        self.cancelActive()

    #---------------
    
    def enterPunch(self):
        self.stand()
        self.fighterinstance.faceOpponent(False)
        self.fighter.stop()
        self.fighter.play('punch')
        self.transitionTimer= Sequence(Wait(self.fighter.getDuration()), Func(self.inputHandler.pollEvents ) )
        self.transitionTimer.start() 
        attackMask = BitMask32()
        attackMask.setBit(2)
        self.activeTimer = Sequence( Wait(0.12),
                                     Func(self.attack,attackMask,5,5 ) #attack, bitmasks, range, damage
                                   )
        self.activeTimer.start()


    def filterPunch(self,request,args):
        if self.transitionTimer.getT() > self.transitionTimer.getDuration()-0.2 :  #allow player to hit the next strike 0.2 to 0 seconds befor the animation finished
            return request

    def exitPunch(self):
        self.fighterinstance.faceOpponent(True)
        self.cancelTransition()
        self.cancelActive()

    #-------------
    def enterKick(self):
        self.stand()
        self.fighterinstance.faceOpponent(False)
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

    def exitKick(self):
        self.fighterinstance.faceOpponent(True)
        self.cancelTransition()
        self.cancelActive()
  
    
    #----------------
    
    """
  
    #------------
    def enterLStep(self):
        self.fighter.loop("side-step")
        self.fighterinstance.setSpeed(0,4.41)
    def filterIdle(self,request,options):
        if request != "LStep":
            return request
    def exitLStep(self):
        self.fighter.stop()
        self.fighterinstance.setSpeed(0,0)
 

        

   
        
    #-----------------   
    """ 
