from direct.showbase import DirectObject
from operator import attrgetter ,itemgetter
from configFile import readKeys
from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import Func,Wait

class EventRecorder():
    def __init__(self):
        self.eventhistory =[]
    
    def addEvent(self,eventNum):
        self.eventhistory.insert(0,[globalClock.getRealTime(),eventNum]) #add the new event with timestamp at the beginning of the list
        self.cleanUp()
        
    def cleanUp(self):
        while 1:
            if not len(self.eventhistory):
                break
            if self.eventhistory[-1][0] + 0.5 < globalClock.getRealTime(): #the 0.3 specifies how long the backlog of events is kept
                self.eventhistory.pop(-1) #pop out old elements
            else:
                break
        #print self.eventhistory
    
    def testEvents(self,eventChain=[]):
        """ tests a list of events against the actually pressed buttons. returns true if no list is given or if the set matches.
        """
        self.cleanUp()
        if not len(eventChain):
            return True
        if len(self.eventhistory) < len(eventChain): 
            return False
        if (globalClock.getRealTime()-self.eventhistory[len(eventChain)-1][0]) > len(eventChain)*0.1: #if you took more than 0.1 seconds on average to press a key..
            return False
            
        getevent = itemgetter(1)
        eventsNoTime = map(getevent, self.eventhistory)
        eventsNoTime.reverse()
        
        if eventsNoTime[-len(eventChain):] == eventChain:
            return True
        
        
        
class StateTrigger(object):
    def __init__(self, triggerEvent, state, eventMap = [0], eventOrder = []):
        self.trigger = triggerEvent #stores the key that triggers the state
        self.eventMap = set(eventMap) #stores all key-conditions that must be met in order to trigger
        self.eventMap.add(self.trigger) #adds the trigger event in case someone forgot it,
        self.eventCount = len(self.eventMap) #store the length of the event map. higher numbers will be tested first for matching keys.
        self.state = state #the state to request from the fsm if the everything matches
        self.eventOrder = eventOrder #for the future, used to test for sequences of button smashes, so you have to get the right buttons in the right order.
        self.eventOrderCount = len(self.eventOrder) # 2nd sort parameter, long sequences will be tested befor short ones... some timers .. should count the last input
        self.lastInput = None #for the future, used to store the time-stamp of the last keypress so we can cancel old combos, and not trigger to early on long ones
        if triggerEvent:
            eventMap.insert(0, triggerEvent)
        self.eventOrig = eventMap[0] #now this one is.. a bit cryptic. it stores the first key of the keyMap (or the triggerEvent if given)
        self.eventDist = self.eventOrig #even more crpytic, this one will store the result of the difference between eventOrig and eventNr 
                                        #neccessary to get the events that match the last-pressed button first.
                                        #and since we work through the results in revers order.. we need to do something silly as 1000-the number 
    def calcEventDist(self, eventNr):
        self.eventDist = 1000 - abs(self.eventOrig - eventNr)

    def __repr__(self):
        return repr((self.eventCount, self.trigger, self.state , self.eventMap,
                     self.eventOrder, self.eventOrderCount, self.eventDist))
    #some getter and setter stuff to set the timers and blah. do it later.. TODO: do it now.
    def getOrder(self):
        return self.eventOrder

class InputHandler(DirectObject.DirectObject):
    def __init__(self, fsm, side):
        #TODO: add temporary mapping.. see the todo in pollEvents
        #lets start by creating a mapping a key to a number, so we get independant of keyboards, controllers, cpu and networking.
        #this code, still is keyboard dependant is it maps keys to an event number (the index of the key)
        #using ["a","b","c"] , will make key a the event 1, b event 2 and so on.
        #given my godlike power to define indices at will...
        #i hearby delcare index  1 to 4 will map to up,down,left, right.
        #further i declare thet event 5 shall be punch, 6 kick, 7 defense , 8 special1
        #index 9 shall play a cute animation on cute characters and some raw and macho-like animation on raw-macho like chars
        #dont dare to disobey.
        #to leave event indices unset, stuff with  "" 
        #example keymap = ["","arrow_up","arrow_down","arrow_left","arrow_right","1","2","3"] 

        #negative event numbers map to key-lift events . so we cant use event 0 as -0 == 0 , stuffing "" as index 0 , 0 will double as "no event key neccessary"
        ##TODO: load the keymap from a config file!
        keymap = readKeys()
        keymap = keymap[side]
        # The keymap stores button presses as a positive number, and button releases
        # as negative, so we make sure index 0 isn't used, since 0 = -0
        keymap.insert(0, "")
        self.fsm = fsm
        self.side = side
        self.keystatus = set()

        # Bind our event 
        for index, key in enumerate(keymap):
            self.accept(key, self.setKey, [index, 1])
            self.accept(key + "-up", self.setKey, [index, 0])
            self.keystatus.add(-index)
        self.eventRecorder = EventRecorder() #will store the keys pressed in the past
        self.stateTimer = Sequence() #this will contain a sequence with a Wait and Func interval, requesting the next state
                               #unless overwritten by a more recent state (as in double-tab combo)
        self.nextState = None  #the state into wich the the stateTimer will change so we can avoid lockups when requesting the same state over and over again
        self.permaTriggers = [] #contains the "permanent" mapped inputs, cant be deleted by the fsm.

        self.permaTriggers.append(StateTrigger(1, "Jump", [-2])) #-2 means no jumping when the user presses down.
        self.permaTriggers.append(StateTrigger(1, "JumpIn", [-2, 4]))
        self.permaTriggers.append(StateTrigger(1, "JumpOut", [-2, 3]))
        self.permaTriggers.append(StateTrigger(0, "Crouch", [2]))  #0 means, no special trigger key
        self.permaTriggers.append(StateTrigger(0, "RunIn", [4]))
        self.permaTriggers.append(StateTrigger(0, "RunOut", [3]))
        self.permaTriggers.append(StateTrigger(5, "Punch", [-2])) #ne regular punch when crouching
        self.permaTriggers.append(StateTrigger(7, "Defense", [-2, 7])) # turn the first 7 (trigger key) to 0 if you like the make attack->defense with static buttons
        self.permaTriggers.append(StateTrigger(6, "Kick", [-2]))
        self.permaTriggers.append(StateTrigger(5, "CrouchPunch", [2])) #crouch punch needs crouching *nodnod*
        self.permaTriggers.append(StateTrigger(6, "CrouchKick", [2])) #so does kicking ..
        self.permaTriggers.append(StateTrigger(7, "CrouchDefense", [2, 7])) # 
        self.permaTriggers.append(StateTrigger(1, "EvadeUp",   [0], eventOrder=[1,1])) #there was some.. really odd bug that added event 1, to the event map of
        self.permaTriggers.append(StateTrigger(2, "EvadeDown", [0], eventOrder=[2,2])) #this line here.when i did not specify the [0]. i dont know why! so i added 0

    def setKey(self, eventnum, setOrClear):
        #swap left-right depending on the player side, for the left player,
        #left will be left. something in my head tells me this is not clever, but it works.
        #TODO: have an eye on the side-swapping.. it might fight back and
        #jump at you from behind, tearing your spine out and eat your balls. will happen. promise.
        
        if self.side and eventnum == 3:
            eventnum = 4
        elif self.side and eventnum == 4:
            eventnum = 3
            
        
        if setOrClear:
            self.keystatus.add(eventnum)
            self.keystatus.discard(-eventnum)
            self.eventRecorder.addEvent(eventnum)
        else:
            self.keystatus.add(-eventnum)
            self.keystatus.discard(eventnum)
            if self.stateTimer.isPlaying():
                self.stateTimer.insert(-2,Wait(0.05)) #if a key lifts while a new state is requested, delay it to see if a double-tap or other combo follows
           

        for trigger in self.permaTriggers:
            trigger.calcEventDist(eventnum) #update the key-distance-weighting for sorting it corretcy in the pollEvents thing.

        self.pollEvents(eventnum)

    def _getPermaTriggers(self):
        return sorted(
                      self.permaTriggers,
                      key = attrgetter('eventOrderCount', 'eventCount', 'eventDist'),
                      reverse = True)

    def _triggerKeyMatchesEventNum(self, eventnr, trigger):
        return trigger.trigger and trigger.trigger == eventnr or trigger.trigger == 0

    def requestState(self,state="Idle"):
        if "enter" + state in dir(self.fsm):
            if self.fsm.state:
                self.fsm.request(state)
                print "requested",state
        else:
            print "requested state not in FSM", state 
        self.nextState = None
        self.stateTimer.pause()
        
    def pollEvents(self, eventnr = 0):
        #olympic sorting! it sorts the eventTriggers by eventCount,eventOrderCount and eventDist in descending order
        #event count comes first as it defines the number of buttons to be pressed, more complex need to be catched first
        #eventOrderCount is the length of the combo which order must be correctly pressed to work out
        #eventDist is the weighting between the last event received and the triggerEvent, 
                            #or the first eventNr passed to the eventTrigger in the eventMap parameter if the trigger event was 0
        #the eventDist causes to trigger the event of the last pressed button, in all other parameters are equal
        #like left-right-left-right running with one button permanently pressed
        #TODO:merge the permaTriggers with temporary triggers, sort the result and continue with that.
        for trigger in self._getPermaTriggers():
            #print trigger.state, trigger.getOrder(), trigger.eventMap, self.keystatus
            #if all buttons match the current button-states
            if trigger.eventMap.issubset(self.keystatus):
                #if the triggerkey matches, or if there is none assigned
                if self._triggerKeyMatchesEventNum(eventnr, trigger) and self.eventRecorder.testEvents(trigger.getOrder()):
                    #the trigger logic may get deeper with the order of events,
                    if self.nextState != trigger.state:
                        self.nextState = trigger.state
                        self.stateTimer.pause()
                        self.stateTimer = Sequence(Wait(0.04),Func(self.requestState,trigger.state))
                        self.stateTimer.start()
                        return
                    else:
                        return
        self.stateTimer.pause()
        self.stateTimer = Sequence(Wait(0.04),Func(self.requestState))
        self.stateTimer.start()
