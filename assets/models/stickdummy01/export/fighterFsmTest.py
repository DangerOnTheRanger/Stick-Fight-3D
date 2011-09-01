from direct.fsm.FSM import FSM
from direct.actor.Actor import Actor

from direct.interval.MetaInterval import Sequence,Parallel
from direct.interval.FunctionInterval import Func,Wait

from direct.showbase.ShowBase import ShowBase
from direct.showbase import DirectObject

class inputHandler(DirectObject.DirectObject):
    def __init__(self):
        #lets start by creating a mapping a key to a number, so we get independant of keyboards, controllers, cpu and networking.
        #this code, still is keyboard dependant is it maps keys to an event number (the index of the key)
        #using ["a","b","c"] , will make key a the event 0, b event 1 and so on.
        #given my godlike power to define indices at will...
        #i hearby delcare index  1 to 4 will map to up,down,left, right.
        #further i declare thet event 5 shall be punch, 6 kick, 7 defense
        #index 42 shall play a cute animation on cute characters and some raw and macho-like animation on raw-macho like chars
        #dont dare to disobey.
        #negative event numbers map to key-lift events . so we cant use event 0 as -0 == 0 , stuffing "" as index 0
        keymap = ["","arrow_up","arrow_down","arrow_left","arrow_right","1","2","3"] #added button 1,2 and 3 , totaly at will. wanna change your keymap, change this array

        self.keystatus = set()
        for index,key in enumerate(keymap):
            self.accept(key,self.setKey,[index,1] )
            self.accept(key+"-up",self.setKey,[index,0])
        self.events = [] #will store the combos event numbers and state requests
        
    def setKey(self,eventnr,SetOrClear):
        if SetOrClear:
            self.keystatus.add(eventnr)
        else:
            self.keystatus.remove(eventnr)
        for event in self.events:
               ##set if the key goes down and the combo matches  OR     if the key goes up with no other combo specified.    
               #like used when defending, or walking , walking states transition via idle.
            if  (event[0] == eventnr and event[1] == self.keystatus) or  ( event[0]==-eventnr  )   :  
                event[2][0].request(event[2][1])   
        
    def clearMapping(self):
        self.events = []
    
    def mapEvent(self,fsm,triggerevent,action,activeevents=[]):

        activeevents = set(activeevents)
        activeevents.add(triggerevent)
        self.events.append([triggerevent,activeevents,[fsm,action]])

    

class FighterFSM(FSM):  #inherits from direct.fsm.FSM
                    ##this class has to be written for each character in the game 
                    ####unfortunately that much coding per char is required until we can autogenerate based on artists input
                    ## i am not sure where to put the fighter actor. logically it belongs to the fighter class, but the fsm does a lot more with it.
                    ## guess it will end up in the fsm as this is the file created for each fighter individually.
                    ## or if we should inherit Fighter from FSM and simply stuff everything in there wich would be bad cause we copy all shared code around
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
        self.mapEvent( 5, "RPunch" )
        self.mapEvent( 5, "LPunch", [2])
        self.mapEvent( 6, "Kick" )  
        self.mapEvent( 7, "Defense" )
        print "entered idle"
        
    def exitIdle(self):
        #self.fighterinstance.setSpeed(0,0) #cant hurt
        self.transitionTimer = None
        self.clearMapping()
    
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
        self.mapEvent(5,"LPunch") #allows us to combo a punch followed by a kick.

    def filterRPunch(self,request,args):
        if self.transitionTimer.getT() > self.transitionTimer.getDuration()-0.2 :  #allow player to hit the next strike 0.2 to 0 seconds befor the animation finished
            print "combo r"
            return request

    def exitRPunch(self):
        print "exiting rpunch"
        self.transitionTimer = None
        self.clearMapping()
        pass
        

    #---------------------------
   
    def enterLPunch(self):
        print "entering lpunch"
        #self.fighterinstance.setSpeed(0,0) #just for illustration
        self.fighter.stop()
        self.fighter.play('lpunch')
        self.transitionTimer= Sequence(Wait(self.fighter.getDuration()), Func(self.request,"Idle" ) )
        self.transitionTimer.start()
        self.mapEvent(5,"RPunch")

    def filterLPunch(self,request,args):
        if self.transitionTimer.getT() > self.transitionTimer.getDuration()-0.2 :  #allow player to hit the next strike 0.2 to 0 seconds befor the animation finished
            print "combo l"
            return request

    def exitLPunch(self):
        print "exiting lpunch"
        self.transitionTimer = None
        self.clearMapping()
        
    #--------------------------------    
        
    def enterKick(self):
        print "entering kick"
        self.fighter.stop()
        self.fighter.play('kick')
        self.transitionTimer= Sequence(Wait(self.fighter.getDuration()), Func(self.request,"Idle" ) )
        self.transitionTimer.start()

    def filterKick(self,request,args):
        if self.transitionTimer.getT() > self.transitionTimer.getDuration()-0.2 : 
            print "kick end"
            return request

    def exitLPunch(self):
        print "exiting kick"
        self.transitionTimer = None
        self.clearMapping()
        
    #-----------------  

        
    def enterDefense(self):
        print "entering Defense"
        self.fighter.stop()
        self.fighter.loop('defense')
        self.mapEvent(-7,"Idle")


    def exitDefense(self):
        print "exiting Defense"
        self.transitionTimer = None
        self.clearMapping()
        
    #-----------------       


base = ShowBase()
IH = inputHandler()
fsmtest = FighterFSM("player1")
fsmtest.setup(IH,None)
base.run() 
