import pygame
import moderngl,os,random,string
import sys
from array import array
from pygame.math import Vector2
import numpy as np
import math
from .animatedsprite import AnimatedSprite
from .screen import gameScreen



class RenderObject(AnimatedSprite):

    def __init__(self,shader:str='default',swizzle='BGRA'):
        
        AnimatedSprite.__init__(self)

        self.shader = shader
        self.swizzle = swizzle
        self.texture = None
        self.pp = None


    def init(self):

        # compenents = rgba channels so 4 = all rgba. f1 dtype is 8 bit numbers
        self.texture = gameScreen.ctx.texture(self.image.get_size(),components=4,dtype='f1')
     
        self.texture.filter = (moderngl.NEAREST,moderngl.NEAREST)

        self.texture.swizzle = self.swizzle

        # get rgba/byte information for each pixel in surface
        self.texture.write(self.image.get_view('1'))


    def set_shader(self,shader:str='default'):
    
        self.shader = shader

        
    def surf_to_texture(self):

        
        # use 0 channel
        self.texture.use(0)

    def set_uniforms(self,nameVal:dict={}):

        if nameVal:

            for n in nameVal:
                gameScreen.shaderPrograms[self.shader][n] = nameVal[n]

    def set_default_uniforms(self):

        gameScreen.shaderPrograms[self.shader]['memSlot'] = 0
        gameScreen.shaderPrograms[self.shader]['alpha'] = 0
        # self.shaderPrograms[self.shader]['alpha'] = self.alpha
        gameScreen.shaderPrograms[self.shader]['screenSize'] = (gameScreen.windows[self.surface_to_draw_on].win_width,gameScreen.windows[self.surface_to_draw_on].win_height)
        gameScreen.shaderPrograms[self.shader]['spriteSize'] = self.image.get_size()
        gameScreen.shaderPrograms[self.shader]['spriteOffset'] = (self.sprite_offsetx,self.sprite_offsety)
        gameScreen.shaderPrograms[self.shader]['position'] = self.hurtbox.center
        gameScreen.shaderPrograms[self.shader]['rotation'] = math.radians(0)
        gameScreen.shaderPrograms[self.shader]['bgOffset'] = (gameScreen.windows[self.surface_to_draw_on].bg_offset_x,gameScreen.windows[self.surface_to_draw_on].bg_offset_y)
        gameScreen.shaderPrograms[self.shader]['zoom'] = gameScreen.windows[self.surface_to_draw_on].zoom

        if self.pp:
            gameScreen.shaderPrograms[self.shader]['zoom'] = 1.1
        

    def submit_to_render(self,surfaceToDrawOn:str='win'):

        self.surface_to_draw_on = surfaceToDrawOn

        # random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

        gameScreen.windows[self.surface_to_draw_on].drawing_queue[self] = {'assetToDraw':self}

    def render(self):

        print(self.__class__.__name__)

        # run surf to textyre
        self.surf_to_texture()

        # set default uniforms
        self.set_default_uniforms()

        # set specifc uniforms
        self.set_uniforms()

        # render
        gameScreen.renderObjects[self.shader].render(mode=moderngl.TRIANGLE_STRIP)

        # free up object
        # self.texture.release()






# screen = pygame.display.set_mode((800,600),pygame.OPENGL|pygame.DOUBLEBUF|pygame.FULLSCREEN)

# display = pygame.Surface((800,600))



objs = []

card1 = RenderObject()
card1.set_shader()
card1.img_path='pynaccle/Sprites/Cards/Hearts/1_23x36.png'
card1.load_or_update_image()
card1.image = card1.image.convert_alpha()
card1.init()
card1.hurtbox.center = (0,0)

card2 = RenderObject()
card2.set_shader()
card2.img_path='pynaccle/Sprites/Cards/Hearts/1_23x36.png'
card2.load_or_update_image()
card2.init()
card2.image = card2.image.convert_alpha()
card2.hurtbox.center = (200,0)

card3 = RenderObject()
card3.set_shader('highlight')
card3.img_path='pynaccle/Sprites/Cards/Hearts/1_23x36.png'
card3.load_or_update_image()
card3.init()
card3.image = card2.image.convert_alpha()
card3.hurtbox.center = (50,200)

card4 = RenderObject()
card4.pp = 1
card4.set_shader('highlight')
card4.img_path='pynaccle/Sprites/Cards/Hearts/1_23x36.png'
card4.load_or_update_image()
card4.init()
card4.image = card2.image.convert_alpha()
card4.hurtbox.center = (50,50)


gameScreen.add_window('win',1200,800,1,(0,0))




# add surface ot frame buffer object


# ctx = moderngl.create_context()

clock = pygame.time.Clock()

# img = pygame.image.load('pynaccle/Sprites/Cards/Hearts/1_23x36.png')

ccs = [RenderObject() for i in range(1000)]

for bb in ccs:

    bb.set_shader()
    bb.img_path='pynaccle/Sprites/Cards/Hearts/1_23x36.png'
    bb.load_or_update_image()
    bb.init()
    bb.image = bb.image.convert_alpha()
    bb.hurtbox.center = (random.randrange(-400,600),random.randrange(-400,400))


while True:




    gameScreen.screen.fill((0,0,0))
    # mysurf.blit(img)
    # display.blit(img,pygame.mouse.get_pos())
    
    gameScreen.ctx.clear(0.0, 0.0, 0.0)
    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if event.key == pygame.K_SPACE:
                card1.hurtbox.centerx -= 2
 
     
    # gameScreen.bind_window('win')
    # card1.render()
    card2.hurtbox.centerx-= 5

    card4.submit_to_render()
    card3.submit_to_render()
    card1.submit_to_render()
    card2.submit_to_render()

    for bb in ccs:

        m = 1
        
        if m == 1:
            bb.hurtbox.centerx += 1
            # bb.hurtbox.centerx += random.randrange(-4,5)
            # bb.hurtbox.centery -= random.randrange(-3,3)

        if m == 2:
            bb.hurtbox.centerx -= 2
            bb.hurtbox.centery += 1

        bb.submit_to_render()

    # card2.render()
    gameScreen.render_windows()



    pygame.display.flip()

    
    
    clock.tick(60)


    import numpy as np

# def create_noise_texture(ctx, width, height):
#     # random noise, values 0-255
#     noise = np.random.randint(0, 255, (height, width), dtype=np.uint8)
    
#     texture = ctx.texture((width, height), 1, noise.tobytes())  # 1 = single channel (red)
#     texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
#     return texture