from direct.showbase.ShowBase import ShowBase
from match import Match
base = ShowBase()

Match(None,None,'../assets/models/floortile/floortile')

#base.disableMouse()
#base.camera.setY(-250)
#base.camera.setZ(30)
base.run() 
