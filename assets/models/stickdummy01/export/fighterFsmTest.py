from direct.fsm.FSM import FSM
from direct.actor.Actor import Actor

from direct.interval.MetaInterval import Sequence,Parallel
from direct.interval.FunctionInterval import Func,Wait

from direct.showbase.ShowBase import ShowBase
from direct.showbase import DirectObject

class inputHandler(DirectObject.DirectObject):
    def __init__(self):
        self.statearray = None
        self.inputarray = None
        
    def mapInput(self,fsm=None,inputKeyArray=None,FSMStateArray=None ):
        self.ignoreAll()
        if not (fsm and inputKeyArray and FSMStateArray):
            self.statearray= None
            self.inputarray = None
            
            return
        
        if len(inputKeyArray) == len(FSMStateArray):
            for x in range(len(inputKeyArray)):
                self.accept(inputKeyArray[x],fsm.request, [FSMStateArray[x] ])
            
        
        self.statearray= FSMStateArray 
        self.inputarray = inputKeyArray
        #depending on the input keys,request the fsm state.
        #this is a bit of a detour for the inputs, but good for separation with network and cpu controlls, aswell as combos, keeps the fsm clean
           
        
    #def setKey(key,):
    #    #one a button or combo was pressed...
    #    if combodetect:
    #        fsm.request(self.statearray[self.inputarray.index('thekey')])
    #    #....
    

class FighterFSM(FSM):  #inherits from direct.fsm.FSM
                    ##this class has to be written for each character in the game 
                    ####unfortunately that much coding per char is required until we can autogenerate based on artists input
                    ## i am not sure where to put the fighter actor. logically it belongs to the fighter class, but the fsm does a lot more with it.
                    ## guess it will end up in the fsm as this is the file created for each fighter individually.
                    ## or if we should inherit Fighter from FSM and simply stuff everything in there wich would be bad cause we copy all shared code around
    def setup(self,inputHandler,FighterClassInstance):
        
        self.fighter = Actor('./stickfigure', 
                                        {
                                          'rpunch' :'stickfigure-r_punch',
                                          'lpunch' :'stickfigure-l_punch',
                                          'hit'    :'stickfigure-hit'    ,
                                          'defense':'stickfigure-defense',
                                          'idle'   :'stickfigure-idle'   ,
                                          'kick'   :'stickfigure-kick'   ,
                                          'run'    :'stickfigure-run'    ,

                                        })
        self.fighter.reparentTo(render)
        #self.fighter = FighterClassInstance.ActorNodePath #so we can directly play and loop the animation there.
        #self.fighterinstance = FighterClassInstance
        self.inputHandler = inputHandler #instance of the InputHandler class that 
        self.activeInterval = None #we will store our active sequence,parallel or interval here, so we can easily clean it up 
                                  #(altho we could go with naming them all the same,too. wich would be even more elegant)
        self.transitionTimer = None #usually holds a sequence like sequence(Wait(time),self.request('nextstate'))
        self.request("Idle")
        
    def enterIdle(self):
        #self.fighterinstance.setSpeed(0,0)
        self.fighter.loop("idle")
        self.inputHandler.mapInput(self,["1","2","3","4"],["RPunch","LPunch","Kick","Defense"])
        print "entered idle"
        
    def exitIdle(self):
        #self.fighterinstance.setSpeed(0,0) #cant hurt
        self.transitionTimer = None
        self.inputHandler.mapInput()
    
    #-------------------------
    
    #example of a punch, wich default returns to idle, if no buttons are pressed. also blocks button presses/requests until sort befor the end. 
    #at the end it is possible to transition to any legal state we defined earlier 
    def enterRPunch(self):
        print "entering rpunch"
        #self.fighterinstance.setSpeed(0,0) #just for illustration
        self.fighter.stop()
        self.fighter.play('rpunch')
        self.transitionTimer= Sequence(Wait(self.fighter.getDuration()), Func(self.request,"Idle" ) )
        self.transitionTimer.start()
        self.inputHandler.mapInput(self,["2"],["LPunch"]) #allows us to combo a punch followed by a kick.

    def filterRPunch(self,request,args):
        if self.transitionTimer.getT() > self.transitionTimer.getDuration()-0.2 :  #allow player to hit the next strike 0.2 to 0 seconds befor the animation finished
            print "combo r"
            return request

    def exitRPunch(self):
        print "exiting rpunch"
        self.transitionTimer = None
        self.inputHandler.mapInput()
        pass
        

    #---------------------------
   
    def enterLPunch(self):
        print "entering lpunch"
        #self.fighterinstance.setSpeed(0,0) #just for illustration
        self.fighter.stop()
        self.fighter.play('lpunch')
        self.transitionTimer= Sequence(Wait(self.fighter.getDuration()), Func(self.request,"Idle" ) )
        self.transitionTimer.start()
        self.inputHandler.mapInput(self,["1"],["RPunch"]) #allows us to combo a punch followed by a kick.

    def filterLPunch(self,request,args):
        if self.transitionTimer.getT() > self.transitionTimer.getDuration()-0.2 :  #allow player to hit the next strike 0.2 to 0 seconds befor the animation finished
            print "combo l"
            return request

    def exitLPunch(self):
        print "exiting lpunch"
        self.transitionTimer = None
        self.inputHandler.mapInput()
        
    #--------------------------------    
        
    def enterKick(self):
        print "entering kick"
        #self.fighterinstance.setSpeed(0,0) #just for illustration
        self.fighter.stop()
        self.fighter.play('kick')
        self.transitionTimer= Sequence(Wait(self.fighter.getDuration()), Func(self.request,"Idle" ) )
        self.transitionTimer.start()
        #self.inputHandler.mapInput(self,["1"],["RPunch"]) #allows us to combo a punch followed by a kick.

    def filterLPunch(self,request,args):
        if self.transitionTimer.getT() > self.transitionTimer.getDuration()-0.2 :  #allow player to hit the next strike 0.2 to 0 seconds befor the animation finished
            print "kick end"
            return request

    def exitLPunch(self):
        print "exiting kick"
        self.transitionTimer = None
        self.inputHandler.mapInput()
        
    #-----------------  

        
    def enterDefense(self):
        print "entering Defense"
        #self.fighterinstance.setSpeed(0,0) #just for illustration
        self.fighter.stop()
        self.fighter.loop('defense')
        #self.transitionTimer= Sequence(Wait(self.fighter.getDuration()), Func(self.request,"Idle" ) )
        #self.transitionTimer.start()
        self.inputHandler.mapInput(self,["4-up"],["Idle"]) #allows us to combo a punch followed by a kick.


    def exitDefense(self):
        print "exiting Defense"
        self.transitionTimer = None
        self.inputHandler.mapInput()
        
    #-----------------       


base = ShowBase()
IH = inputHandler()
fsmtest = FighterFSM("player1")
fsmtest.setup(IH,None)
base.run() 
