
from direct.showbase import DirectObject

class InputHandler(DirectObject.DirectObject):
    def __init__(self,keymap,side):
        #lets start by creating a mapping a key to a number, so we get independant of keyboards, controllers, cpu and networking.
        #this code, still is keyboard dependant is it maps keys to an event number (the index of the key)
        #using ["a","b","c"] , will make key a the event 0, b event 1 and so on.
        #given my godlike power to define indices at will...
        #i hearby delcare index  1 to 4 will map to up,down,left, right.
        #given the rotation this might end up messed.. a bit
        #further i declare thet event 5 shall be punch, 6 kick, 7 defense
        #index 42 shall play a cute animation on cute characters and some raw and macho-like animation on raw-macho like chars
        #dont dare to disobey.
        #negative event numbers map to key-lift events . so we cant use event 0 as -0 == 0 , stuffing "" as index 0
        keymap.insert(0,"")
        #keymap = ["","arrow_up","arrow_down","arrow_left","arrow_right","1","2","3"] #added button 1,2 and 3 , totaly at will. wanna change your keymap, change this array
        self.side = side
        self.keystatus = set()
        for index,key in enumerate(keymap):
            self.accept(key,self.setKey,[index,1] )
            self.accept(key+"-up",self.setKey,[index,0])
        self.events = [] #will store the combos event numbers and state requests

        
    def setKey(self,eventnr,SetOrClear):
        #swap left-right depending on the player side, for the left player, left will be left. aah .. confusing. someone else should fix it .. once it gets troublesome
        if self.side and eventnr == 3:
            eventnr = 4
        elif self.side and eventnr ==4:
            eventnr = 3
            
        if SetOrClear:
            self.keystatus.add(eventnr)
        else:
            self.keystatus.remove(eventnr)
        for event in self.events:
               ##set if the key goes down and the combo matches  OR     if the key goes up with no other combo specified.    
               #like used when defending, or walking , walking states transition via idle.
            if  (event[0] == eventnr and event[1] == self.keystatus) or  ( event[0]==-eventnr  )   :  
                event[2][0].request(event[2][1])   
    
    def pollEvents(self,eventsToTest=[1,2,3,4]):
        eventsToTest=set(eventsToTest)        
        
        
        for event in self.events:
               ##set if the key goes down and the combo matches  OR     if the key goes up with no other combo specified.    
               #like used when defending, or walking , walking states transition via idle.
            if  (event[0] in eventsToTest& self.keystatus) and  ( len(event[1])==1  )   :  
                event[2][0].request(event[2][1])
        
        
        
    def clearMapping(self):
        self.events = []
    
    def mapEvent(self,fsm,triggerevent,action,activeevents=[]):

        activeevents = set(activeevents)
        activeevents.add(triggerevent)
        self.events.append([triggerevent,activeevents,[fsm,action]])

