
from math import tan
class MatchCamera():
    def __init__(self,player1,player2,camera):
    
        self.p1, self.p2 = player1,player2
        self.cam = camera
        base.disableMouse()    
        self.pivot = render.attachNewNode("camera-pivot")
        self.pivot.setPos( (self.p1.getPos(render)+self.p2.getPos(render) )/2 )
        self.pivot.lookAt(self.p1)
        self.cam.ls()
        
        taskMgr.add(self.cameraTask,"cameraTask")
    
    def cameraTask(self,task):
        oldpos = self.cam.getPos()
        self.pivot.setPos( (self.p1.getPos(render)+self.p2.getPos(render) )/2 )
        dist = self.pivot.getDistance(self.p1) / tan( (self.cam.getChild(0).node().getLens().getHfov()/1.4)*(3.14/360)  ) # pi is exactly 3! 
        self.cam.lookAt(self.pivot,0,0,4)
        self.cam.setPos(self.pivot,-max(dist,20),0, max(4,dist/2.) )
        
        delta = self.cam.getPos()-oldpos
        #delta.normalize()
        self.cam.setPos(oldpos+(delta*globalClock.getDt()*2))

        
        #self.cam.setPos(oldpos+min(delta*globalClock.getDt(),self.cam.getPosDelta()) )
        
        return task.cont
