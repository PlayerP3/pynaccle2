import pygame,sys,math
from .animatedsprite import AnimatedSprite
from .screen import gameScreen
import moderngl
from pyglm import glm

class Chunk(AnimatedSprite):
    
    def __init__(self):
       
       super().__init__(self)
       
       self.inaccessible = False
       self.zlayer_drawing = 0

       
        

    # function to create a chunk obj after building the surface on the win
    def create_chunk_sprite(self,winSurface:pygame.Surface):

        self.image = winSurface
        self.sprite = winSurface
        self.hurtbox.center = (0,0)
        self.dissolveTimer.timer_speed = 1.3
        self.shader = 'dissolve'
        

    def update_sprite(self):
        pass

    def update(self):

        self.submit_to_render()

    def init(self):


        self.texture = gameScreen.ctx.texture(self.sprite.get_size(),components=4,dtype='f1')
     
        self.texture.filter = (moderngl.NEAREST,moderngl.NEAREST)

        self.texture.swizzle = self.swizzle

        # get rgba/byte information for each pixel in surface
        self.texture.write(self.sprite.get_view('1'))

        self.write_noise_texture(*self.sprite.get_size())

      

    def spawn(self,pos=(0,0),vertice='center'):
        
        self.is_active = True
        
        pass


    def surf_to_texture(self):

        # use 0 channel
        self.texture.use(0)

    def set_uniforms(self,nameVal:dict={}):

        if nameVal:

            for n in nameVal:
                gameScreen.shaderPrograms[self.shader][n] = nameVal[n]

    def set_default_uniforms(self):

        gameScreen.shaderPrograms[self.shader]['memSlot'] = 0
        # self.shaderPrograms[self.shader]['alpha'] = self.alpha
        gameScreen.shaderPrograms[self.shader]['screenSize'] = (gameScreen.windows[self.surface_to_draw_on].win_width,gameScreen.windows[self.surface_to_draw_on].win_height)
        # gameScreen.shaderPrograms[self.shader]['screenSize'] = (gameScreen.fullscreen_width,gameScreen.fullscreen_height)

        gameScreen.shaderPrograms[self.shader]['spriteSize'] = self.sprite.get_size()
        gameScreen.shaderPrograms[self.shader]['spriteOffset'] = (self.sprite_offsetx,self.sprite_offsety)
        gameScreen.shaderPrograms[self.shader]['position'] = (self.hurtbox.center)
        gameScreen.shaderPrograms[self.shader]['rotation'] = math.radians(float(self.direction))
        gameScreen.shaderPrograms[self.shader]['bgOffset'] = (gameScreen.windows[self.surface_to_draw_on].bg_offset_x,gameScreen.windows[self.surface_to_draw_on].bg_offset_y)
        gameScreen.shaderPrograms[self.shader]['zoom'] = self.zoom
        gameScreen.shaderPrograms[self.shader]['screenZoom'] = gameScreen.windows[self.surface_to_draw_on].zoom

    #     self.transformationMatrix = glm.mat4(1.0)
    #     self.transformationMatrix = glm.rotate(self.transformationMatrix,glm.radians(self.direction),glm.vec3(1.0,0.0,0.0))
    #     self.transformationMatrix = glm.scale(self.transformationMatrix,glm.vec3(self.zoom,self.zoom,0.0))

    #     # print(gameScreen.windows[self.surface_to_draw_on].projectionMatrix)
    #     # print(self.transformationMatrix)
    #     print(self.shader)
    #     gameScreen.shaderPrograms[self.shader]['transformationMatrix'].write(bytes(self.transformationMatrix))
    #     gameScreen.shaderPrograms[self.shader]['projectionMatrix'].write(bytes(gameScreen.windows[self.surface_to_draw_on].projectionMatrix))
    # # add shader dependent uniforms
    def set_shader_dependent_uniforms(self):

        if self.shader == 'dissolve':

            self.dissolveTimer.start_timer()
            self.dissolveTimer.run_timer()

            # add uniforms
            gameScreen.shaderPrograms[self.shader]['dissolveValue'] = self.dissolveTimer.elapsed_time
            self.noiseTexture.use(1)
            gameScreen.shaderPrograms[self.shader]['dissolveTexture'] = 1

        
