from direct.interval.SoundInterval import SoundInterval
from random import choice

class PlayerSoundFX():
    def __init__(self):
        path = "../assets/sounds/"
        self.hitsounds = []
        self.misssounds = []
        self.blocksounds = []
        #this should autoload all sounds but hey.. later later.
        for x in range(1,6):        
            Sound = loader.loadSfx(path+"hit/hit"+str(x)+".wav")
            self.hitsounds.append( SoundInterval(
                                    Sound,
                                    loop = 0,
                                    volume =1.0,
                                    )
                                 )                                                       
        for x in range(1,4):        
            Sound = loader.loadSfx(path+"block/block"+str(x)+".wav")
            self.blocksounds.append( SoundInterval(
                                    Sound,
                                    loop = 0,
                                    volume =1.0,
                                    )
                                 )    
        
        for x in range(1,7):        
            Sound = loader.loadSfx(path+"miss/miss"+str(x)+".wav")
            self.misssounds.append( SoundInterval(
                                    Sound,
                                    loop = 0,
                                    volume =1.0,
                                    )
                                 )
    def playHit(self):
        choice(self.hitsounds).start()

    def playMiss(self):
        choice(self.misssounds).start()
    
    def playBlock(self):
        choice(self.blocksounds).start()
