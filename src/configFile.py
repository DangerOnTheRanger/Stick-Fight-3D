import ConfigParser

def genNewCfg():
    config = ConfigParser.RawConfigParser()

    "f","t","r","d","x","v","l"
    config.add_section('player1')
    config.set('player1', 'up',     'w')
    config.set('player1', 'down',   'a')
    config.set('player1', 'left',   's')
    config.set('player1', 'right',  'd')
    config.set('player1', 'punch',  'b')
    config.set('player1', 'kick',   'n')
    config.set('player1', 'defense','m')
    
    config.add_section('player2')
    config.set('player2', 'up',     'arrow_up')
    config.set('player2', 'down',   'arrow_down')
    config.set('player2', 'left',   'arrow_left')
    config.set('player2', 'right',  'arrow_right')
    config.set('player2', 'punch',  '1')
    config.set('player2', 'kick',   '2')
    config.set('player2', 'defense','3')

    # Writing our configuration file to 'example.cfg'
    with open('game.cfg', 'wb') as configfile:
        config.write(configfile)

def readKeys():
    config = ConfigParser.RawConfigParser()
    config.read('game.cfg')
    keymap =[]
    for p in ["player1","player2"]:
        i = []
        i.append( config.get(p, 'up') )    
        i.append( config.get(p, 'down') )    
        i.append( config.get(p, 'left') )    
        i.append( config.get(p, 'right') )    
        i.append( config.get(p, 'punch') )    
        i.append( config.get(p, 'kick') )
        i.append( config.get(p, 'defense') )        
        keymap.append(i)
    return keymap

def readCharacter(pathToChar):
    config = ConfigParser.RawConfigParser()
    if pathToChar[-1]!="/":
        pathToChar+="/"    
    config.read(pathToChar+'character.cfg')
    outputDict =dict()
    outputDict['actorFile'] = config.get("base","actorFile")
    for attack in ["kick","punch","crouch-punch","crouch-kick"]:
        outputDict[attack] = dict({"delay" : float(config.get(attack,"delay")) ,
                                   "attackbit" : int(config.get(attack,"attackbit")),
                                   "range" : float(config.get(attack,"range")),
                                   "damage" : float(config.get(attack,"damage")),
                                   "blockeddamage" : float(config.get(attack,"blockeddamage")),
                                   "angle" : float(config.get(attack,"angle")),
                                 } )
    for move in ["run-in","run-out","jump-in","jump-out","evade-ccw"]:
        outputDict[move] = dict({"speedx" : float(config.get(move,"speedx")) ,
                                 "speedy" : float(config.get(move,"speedy"))
                                 } )
                                 
    return outputDict 
