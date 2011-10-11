class FighterState(object):

    def __init__(self):
        self._speed = None
        self._health = None
        self._fsmState = None
        self._facing = None
        self._position = None
        self._heading = None
        self._name = None
        self._wins = None
        self._side = None
    
    def update(self,newState):
        if  newState.speed != None:  
            self._speed = newState.speed
        if  newState.health != None: 
            self._health = newState.health
        if  newState.fsmState != None:  
            self._fsmState = newState.fsmState
        if  newState.facing != None: 
            self._facing = newState.facing    
        if  newState.position != None:
            self._position = newState.position
        if  newState.heading != None:  
            self._heading = newState.heading
        if  newState.name != None:  
            self._name = newState.name
        if  newState.wins != None:  
            self._wins = newState.wins
        if  newState.side != None: 
            self._side = newState.side
        
    def getStatus(self):
        new = FighterState()
        new.update(self)
        return new
    ##########
    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        if type(value)!= list:
            value = list(value)
        self._speed = value
    ############  
    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        self._health = value
    ##########
    @property
    def fsmState(self):
        return self._fsmState

    @fsmState.setter
    def fsmState(self, value):
        self._fsmState = value
    ########
    @property
    def facing(self):
        return self._facing

    @facing.setter
    def facing(self, value):
        self._facing = value
    
    ###########
    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        if type(value)!= list:
            value = list(value)
        self._position = value
    #######
    
    @property
    def heading(self):
        return self._heading

    @heading.setter
    def heading(self, value):
        self._heading = value
    ##########
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
    ##########
    @property
    def wins(self):
        return self._wins

    @wins.setter
    def wins(self, value):
        self._wins = value    
    ###
    @property
    def side(self):
        return self._side

    @side.setter
    def side(self, value):
        self._side = value    
        
