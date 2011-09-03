from direct.showbase.ShowBase import ShowBase
from match import Match
base = ShowBase()

Match(None,None,'../assets/models/floortile/floortile',["f","t","r","d","x","v","l"],["arrow_up","arrow_down","arrow_left","arrow_right","1","2","3"])

#base.disableMouse()
#base.camera.setY(-250)
#base.camera.setZ(30)
base.run() 
