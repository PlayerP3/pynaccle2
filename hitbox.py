import pygame

class Hitbox():

    def __init__(self,x:float=0,y:float=0,w:float=32,h:float=32,offsetX:float=0,offsetY:float=0,frameNumber:int=0):

        self.hitbox = pygame.FRect(x,y,w,h)
        self.offsetX = offsetX
        self.offsetY = offsetY
        self.frameNumber = frameNumber

    def collided(self,pos:tuple,gameobj):

        self.hitbox.center = (pos[0]+self.offsetX,pos[1]+self.offsetY)
        
        if self.hitbox.colliderect(gameobj.hurtbox):
            return True
        
        return False


class HitboxManager():

    def __init__(self):
        
        self.metaData = None


hitboxSystem = HitboxManager()