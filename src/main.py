from direct.showbase.ShowBase import ShowBase
from Match import Match
base = ShowBase()

Match(None,None,["f","t","r","d","x","v","l"],["arrow_up","arrow_down","arrow_left","arrow_right","1","2","3"])

base.disableMouse()
base.camera.setY(-30)
base.camera.setZ(5)
base.run() 
