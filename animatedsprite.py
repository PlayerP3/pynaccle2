import pygame,os,re,math,random,string,sys
import numpy as np
import json
import moderngl
from pygame.math import Vector2
from pyglm import glm
from .globs import delta
# from .timer import Timer
from .screen import gameScreen
from .pens import *
from .timer import Timer,AnimationPlayer


GameSprites = {}
TextSprites = {}
spriteTextures = {}
noiseTextures = {}

   
class AnimatedSprite():

    def __init__(self,shader:str='default',swizzle='BGRA',zlayer_drawing:int=1,rect_colour:str='red',object_of_origin:str='Game',rect_width:float=23,rect_height:float=36,
                 hurtbox_width:float=32,hurtbox_height:float=32,sprite_offsetx:float=0,sprite_offsety:float=0,spawnOffsetX:float=0,spawnOffsetY:float=0,
                 text_colour:str='green',surface_to_draw_on:str='win',penToUse='arial20',ignoreCameraOffset:bool=False,padding:int=10,zoom:float=1,

                 name:str='AnimatedSprite',img_path:str=os.path.join(os.path.dirname(__file__),'Sprites','Cards','Hearts','1_23x36.png'),img_width:int=32,img_width_scale:int=1,img_height:int=32,img_height_scale:int=1,
                 spriteWidth:float=32,spriteWidthScale:float=1,spriteHeight:float=32,spriteHeightScale:float=1,hasSpriteSheet:bool=False,animation_delay:int=1,animation_speed:float=1,alpha:float=1.0,
                 dissolveTimerSpeed:float=1/2,

                 draw_sine_wave_speed:float=1,draw_sine_wave_amplitude:float=1,

                 animationSpeed:float=1,animationType:str='forward',

                 starting_direction:float=0.0,
                 sprite_movement_type:str='none',flip_range:list=[],vertice:str='center',is_text:bool=False):

       

        # set name
        self.name = name
    

        # dealing with text
        self.is_text = is_text
        self.penToUse = penToUse

        # surf to draw on
        self.surface_to_draw_on = surface_to_draw_on
        self.ignoreCameraOffset = ignoreCameraOffset
        self.zoom = zoom

        # set sprite
        self.hasSpriteSheet = hasSpriteSheet
        self.sprite:pygame.Surface = None
        self.currentFrame = 0
        self.image = None
        self.mask = None
        self.mask_img = None
        self.alpha = alpha
        self.padding = padding
        # self.alpha_timer = Timer()
        self.sprite_offsetx = sprite_offsetx
        self.sprite_offsety = sprite_offsety
        self.spawnOffsetX = spawnOffsetX
        self.spawnOffsetY = spawnOffsetY
        self.spawnLocation = (0,0)

        # render obj vars
        self.shader = shader
        self.swizzle = swizzle
        self.texture = None
        self.noiseTexture = None
        self.dissolveTimer = Timer(timer_speed=dissolveTimerSpeed,timer_limit=1)
        self.transformationMatrix = glm.mat4(1.0)

        # rect is used for movement and collision
        self.rect = pygame.FRect(0,0,rect_width,rect_height)

        # this rect is used for movement and collision
        self.hurtbox = pygame.FRect(0,0,hurtbox_width,hurtbox_height)

        self.hitboxData = {}
        self.hitboxes = {}

        self.hurtbox_width = hurtbox_width
        self.hurtbox_height = hurtbox_height

        # hitbox is used for sprite drawing/otherstuff
        # self.hitbox = pygame.FRect(0,0,rect_width,rect_height)
    
        # drawing vars
        self.zlayer_drawing = zlayer_drawing
        self.rect_colour = rect_colour
        self.text_colour = text_colour

        # set activity
        self.is_active = False
        # self.is_active_timer = Timer(timer_speed=0,timer_limit=0)

        # get animationt imer
        # self.animation_timer = Timer()
        # self.alpha_timer = Timer()

        self.object_of_origin = object_of_origin

        # direction variable in json is [start,stop,increment], then we make the list here in the initialising
        self.direction = starting_direction

        self.animation_count = 0
        self.animation_delay = animation_delay
        self.animation_speed = animation_speed

        self.animationSpeed = animationSpeed
        self.animationType = animationType
        self.animationPlayer = AnimationPlayer()

        self.sprite_collection = {}

        self.img_path = img_path
        self.img_width = img_width
        self.img_width_scale = img_width_scale
        self.img_height = img_height
        self.img_height_scale = img_height_scale

        # vars for individual sprites in the spritesheet
        self.spriteWidth = spriteWidth
        self.spriteHeight = spriteHeight
        self.spriteWidthScale = spriteWidthScale
        self.spriteHeightScale = spriteHeightScale

        # clearance value
        self.clearance = 1

        # choose if the sprite will be moving/floating like draw_sine or not
        self.sprite_movement_type = sprite_movement_type

        self.draw_sine_wave_timer = 0
        self.draw_sine_wave_speed = draw_sine_wave_speed
        self.draw_sine_wave_amplitude = draw_sine_wave_amplitude

        self.flip_range = flip_range

        # lerp timer for anything with a sprite
        self.lerpTimer = Timer(timer_limit=1)

        # controls whetehr an object is dran on a center, or topleft
        self.vertice = vertice

        # stores the variables of an obj after init
        self.original_vars = None

    # loading sprite sheets
    def load_sprite_sheet(self):

        # create sprite collection
        sprite_collection = {}

        # create texture collection
        textureCollection = {}

        # get each frame and store it
        for j in range((self.img_height//self.spriteHeight)):

            for i in range((self.img_width//self.spriteWidth)):

                # create empty frame
                surf = pygame.Surface((self.spriteWidth,self.spriteHeight),pygame.SRCALPHA)

                # blit specific frame of image, has to be minus because of the way the image is blitted on the surf
                surf.blit(self.image,(0-(i*self.spriteWidth),0))

                # add padding/empty alpha to sprites to help with stuff like outlines
                sprite_collection[i] = self.pad_sprites(surf)

                # create and add texture to texture cache
                textureCollection[i] = self.write_sprite_texture(sprite_collection[i])

        return sprite_collection,textureCollection
    
    def load_or_update_image(self,SpriteCache:dict=GameSprites):
        
        # load image from memory if it is in json already
        if self.img_path in SpriteCache:

            if 'loaded_image' in SpriteCache[self.img_path]:

                self.image = SpriteCache[self.img_path]['loaded_image']
                self.img_width = self.image.get_width()
                self.img_height = self.image.get_height()

                if not self.is_text:
                    # breakdown image path to get sprite width and height
                    spriteName,whSprite = self.img_path.rstrip('.png').split('_')

                    self.spriteWidth,self.spriteHeight = [int(x) for x in whSprite.split('x')]

                elif self.is_text:
                    self.spriteWidth = self.img_width
                    self.spriteHeight = self.img_height

                
        # load image and store it in json if it does not exist
        elif self.img_path not in SpriteCache:
            
            if not self.is_text:
                SpriteCache[self.img_path] = {'loaded_image':pygame.image.load(self.img_path).convert_alpha()}
                self.image = SpriteCache[self.img_path]['loaded_image']
                self.img_width = self.image.get_width()
                self.img_height = self.image.get_height()

                # breakdown image path to get sprite width and height
                spriteName,whSprite = self.img_path.rstrip('.png').split('_')
                self.spriteWidth,self.spriteHeight = [int(x) for x in whSprite.split('x')]

            elif self.is_text:
                self.create_text_image()

            # set frames in animation player
            self.animationPlayer.totalFrames = (self.img_width//self.spriteWidth)
            self.animationPlayer.timer_limit = self.animationPlayer.totalFrames

    # reinit the sprite and rect 
    def init_sprite(self,SpriteCache:dict=GameSprites):

        # load image, but if it is in memory then just take that
        self.load_or_update_image()

        # process the sprite sheet
        if 'spriteSheet' not in SpriteCache[self.img_path] and 'textureSheet' not in SpriteCache[self.img_path]:

            SpriteCache[self.img_path]['spriteSheet'],SpriteCache[self.img_path]['textureSheet'] = self.load_sprite_sheet()

        # if self.img_path == "Sprites/Roulette/Roulette_38x18.png":
        #     print(self.img_width)
        #     print(self.spriteWidth)
        #     print( SpriteCache[self.img_path]['spriteSheet'])
        #     print( SpriteCache[self.img_path]['textureSheet'])
        #     sys.exit()

        # set sprite and texture
        self.sprite = SpriteCache[self.img_path]['spriteSheet'][self.animationPlayer.currentFrameNumber]
        self.texture = SpriteCache[self.img_path]['textureSheet'][self.animationPlayer.currentFrameNumber]
        
        # compenents = rgba channels so 4 = all rgba. f1 dtype is 8 bit numbers

        # create noise texture
        self.write_noise_texture()

    # create texture from current sprite
    def write_sprite_texture(self,sprite:pygame.Surface):

        # create tex, set channels, set dtype
        texture = gameScreen.ctx.texture(sprite.get_size(),components=4,dtype='f1')
     
        # filter
        texture.filter = (moderngl.NEAREST,moderngl.NEAREST)

        # set channel order 
        texture.swizzle = self.swizzle

        # get rgba/byte information for each pixel in surface
        texture.write(sprite.get_view('1'))

        return texture
    
    # create a noise texture when there is a new dimension in the game
    def write_noise_texture(self,width:int=32,height:int=32,components:int=4,minRGB:int=90,maxRGB:int=175):

        # get dimensions
        dimensions = f"({width},{height})"

        if dimensions not in noiseTextures:

            data = np.random.randint(minRGB, maxRGB, size=(width, height,components), dtype=np.uint8)
            noisePoints = data.tobytes()
            texture = gameScreen.ctx.texture((width,height),components=components)
            texture.write(noisePoints)

            noiseTextures[dimensions] = texture

        self.noiseTexture = noiseTextures[dimensions]

        

    # pad sprites with alpha
    def pad_sprites(self,sprite:pygame.Surface):

        # create empty surf
        paddedSurf = pygame.Surface((sprite.width+self.padding,sprite.height+self.padding),pygame.SRCALPHA)

        # add sprite to it
        paddedSurf.blit(sprite,(self.padding//2,self.padding//2))

        return paddedSurf

    # make damage number
    def create_text_image(self,SpriteCache:dict=GameSprites):

        # load image from memory if it is in json already
        # if self.img_path in SpriteCache:
        #     if 'loaded_image' in SpriteCache[self.img_path]:
        #         self.image =  SpriteCache[self.img_path]['loaded_image']

        #         # set width and heigh to be that of the image
        #         self.img_width = self.image.get_width()
        #         self.img_height = self.image.get_height()


        # load image and store it in json if it does not exist
        # elif self.img_path not in SpriteCache:

        surf = penHolder[self.penToUse].render(f"{self.img_path}",True,self.text_colour)

        # text needs to be drawn on a new surf
        # randsurf = pygame.Surface((surf.get_width(),surf.get_height()),pygame.SRCALPHA)

        # randsurf.blit(surf)

        GameSprites[self.img_path] = {'loaded_image':surf}

        # set image
        self.image = surf
  
        # self.image = randsurf

        # set width and heigh to be that of the image, sprite width is always the same as img width for text
        self.img_width = self.image.get_width()
        self.img_height = self.image.get_height()
        self.spriteWidth = self.img_width
        self.spriteHeight = self.img_height
    

    def update_sprite(self,SpriteCache:dict=GameSprites):

        # dimensions of the sprite
        # dimensions = f"({int(self.img_width*self.spriteWidthScale)},{int(self.img_height*self.spriteHeightScale)})"

        
        # resize or rotate the sprite
        self.init_sprite()

        # animation_frames = list(self.sprite_collection[self.direction].keys())
        # animation_frames = list(SpriteCache[self.img_path][f"({int(self.spriteWidth*self.spriteWidthScale*gameScreen.windows[self.surface_to_draw_on].zoom)},{int(self.spriteHeight*self.spriteHeightScale*gameScreen.windows[self.surface_to_draw_on].zoom)})"][self.direction].keys())

        # sprite_index = (self.animation_count//self.animation_delay) % len(animation_frames)

        # # play animation
        self.animationPlayer.run_timer()

        # # # self.sprite = self.sprite_collection[self.direction][sprite_index]
        self.sprite = SpriteCache[self.img_path]['spriteSheet'][self.animationPlayer.currentFrameNumber]
        self.texture = SpriteCache[self.img_path]['textureSheet'][self.animationPlayer.currentFrameNumber]

        

        # self.animation_count += (delta*self.animation_speed)

        # map index to draw_sine wave timer
        # if self.sprite_movement_type == 'sine':
        #     sprite_index = (self.draw_sine_wave_timer//(math.pi/2)) % len(animation_frames)
    

    # for objects that can be rotated in different directions, call this function to rotate them and save it
    # here sprite collection is all the frames/sprites at a given rotation angle 

    #DEPRECEATD 
    def resize_and_rotate_sprite(self,flip_range:list=[],SpriteCache:dict=GameSprites):

        # load or update the image
        self.load_or_update_image()

        # get dimensions
        dimensions = f"({self.spriteWidth},{self.spriteHeight})"

        # if the class is present but we dont have a sprite for the specific obj
        if self.img_path not in SpriteCache:

            SpriteCache[self.img_path] = {dimensions:{self.direction:self.load_sprite_sheet()}}

        # if the specific obj is there but we dont have a class for that specific rect yet
        if dimensions not in SpriteCache[self.img_path]:
            SpriteCache[self.img_path][dimensions] = {self.direction:self.load_sprite_sheet()}

        if self.direction not in SpriteCache[self.img_path][dimensions]:
            SpriteCache[self.img_path][dimensions][self.direction] = self.load_sprite_sheet()

        # elif self.direction in SpriteCache[self.img_path][dimensions]:

        #     # update sprite and mask
        #     self.sprite =  SpriteCache[self.img_path][dimensions][self.direction][0]
        #     self.mask = pygame.mask.from_surface(self.sprite)
        #     self.hitbox.width,self.rect.height = self.sprite.get_width(),self.sprite.get_height()
        #     return

        

        # # update sprite and mask
        # self.sprite =  SpriteCache[self.img_path][dimensions][self.direction][0]
        # self.mask = pygame.mask.from_surface(self.sprite)
        # self.hitbox.width,self.hitbox.height = self.sprite.get_width(),self.sprite.get_height()



    # function to get hitbox based on current frame
    def get_hitbox(self):
        pass

    # run dissolve 

    # shader vars
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
        gameScreen.shaderPrograms[self.shader]['alpha'] = self.alpha
        gameScreen.shaderPrograms[self.shader]['screenSize'] = (gameScreen.windows[self.surface_to_draw_on].win_width,gameScreen.windows[self.surface_to_draw_on].win_height)
        gameScreen.shaderPrograms[self.shader]['spriteSize'] = self.sprite.get_size()
        gameScreen.shaderPrograms[self.shader]['spriteOffset'] = (self.sprite_offsetx,self.sprite_offsety)
        gameScreen.shaderPrograms[self.shader]['position'] = (self.hurtbox.center)

        gameScreen.shaderPrograms[self.shader]['rotation'] = math.radians(float(-self.direction))
        gameScreen.shaderPrograms[self.shader]['bgOffset'] = (gameScreen.windows[self.surface_to_draw_on].bg_offset_x,gameScreen.windows[self.surface_to_draw_on].bg_offset_y)
        
        gameScreen.shaderPrograms[self.shader]['zoom'] = self.zoom
        gameScreen.shaderPrograms[self.shader]['screenZoom'] = gameScreen.windows[self.surface_to_draw_on].zoom

        

        # build transformation matrix

        # refresh transformation matrix
        # self.transformationMatrix = glm.mat4(1.0)
        # self.transformationMatrix = glm.scale(self.transformationMatrix,glm.vec3(self.sprite.get_size()[0]/gameScreen.windows[self.surface_to_draw_on].win_width,self.sprite.get_size()[1]/gameScreen.windows[self.surface_to_draw_on].win_height,0.0))
        # self.transformationMatrix = glm.rotate(self.transformationMatrix,glm.radians(self.direction),glm.vec3(1.0,0.0,0.0))
        # self.transformationMatrix = glm.translate(self.transformationMatrix,glm.vec3(self.hurtbox.centerx+gameScreen.windows[self.surface_to_draw_on].bg_offset_x,self.hurtbox.centery+gameScreen.windows[self.surface_to_draw_on].bg_offset_y,0.0))

        # # self.transformationMatrix = glm.scale(self.transformationMatrix,glm.vec3(self.zoom,self.zoom,0.0))
        # # self.transformationMatrix = glm.scale(self.transformationMatrix,glm.vec3(self.sprite.get_size()[0]/gameScreen.windows[self.surface_to_draw_on].win_width,self.sprite.get_size()[1]/gameScreen.windows[self.surface_to_draw_on].win_height,0.0))


        # gameScreen.shaderPrograms[self.shader]['transformationMatrix'].write(self.transformationMatrix)
        # gameScreen.shaderPrograms[self.shader]['projectionMatrix'].write(gameScreen.windows[self.surface_to_draw_on].projectionMatrix)
        

    # add shader dependent uniforms
    def set_shader_dependent_uniforms(self):

        if self.shader == 'dissolve':

            self.dissolveTimer.start_timer()
            self.dissolveTimer.run_timer()

            # add uniforms
            gameScreen.shaderPrograms[self.shader]['dissolveValue'] = self.dissolveTimer.elapsed_time
            self.noiseTexture.use(1)
            gameScreen.shaderPrograms[self.shader]['dissolveTexture'] = 1

        elif self.shader == 'liquidfill':

            self.dissolveTimer.start_timer()
            self.dissolveTimer.run_timer()

            # add uniforms
            gameScreen.shaderPrograms[self.shader]['fV'] = 0.3
            gameScreen.shaderPrograms[self.shader]['TIME'] = self.dissolveTimer.elapsed_time

    def submit_to_render(self,surfaceToDrawOn:str='win'):

        self.surface_to_draw_on = surfaceToDrawOn

        # random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

        # add zlayer if it does not exist
        if self.zlayer_drawing not in gameScreen.windows[self.surface_to_draw_on].drawing_queue:

            gameScreen.windows[self.surface_to_draw_on].drawing_queue[self.zlayer_drawing] = []

        if self not in gameScreen.windows[self.surface_to_draw_on].drawing_queue[self.zlayer_drawing]:
            gameScreen.windows[self.surface_to_draw_on].drawing_queue[self.zlayer_drawing].append(self)
        

    def render(self):

        # update the sprite
        self.update_sprite()

        # run surf to textyre
        self.surf_to_texture()

        # set default uniforms
        self.set_default_uniforms()

        # add shader depndent uniforms
        self.set_shader_dependent_uniforms()

        # set specifc uniforms
        self.set_uniforms()

        # render
        gameScreen.renderObjects[self.shader].render(mode=moderngl.TRIANGLE_STRIP)

    def draw_surface(self,asset_type:str='surface',game_object_origin:str='game',is_animated:bool=False,schedule_deletion:bool=True,
                       animation_length:int=0,position:tuple=(0,0),value:int=0,is_critical:bool=False,initial_width:int=0,initial_height:int=0,
                       zlayer:int=1):

        # update sprite
        self.update_sprite()

        position = (position[0]+self.sprite_offsetx,position[1]+self.sprite_offsety)

        pos_rect = None

        if self.vertice == 'center':

            # pos_rect = self.sprite.get_frect(center=position)#
            
            # to have the sprite centered at a specific position we need to effectively push it top and left
            position = (position[0] - (self.sprite.get_width()/gameScreen.windows[self.surface_to_draw_on].zoom)//2,position[1] - (self.sprite.get_height()/gameScreen.windows[self.surface_to_draw_on].zoom)//2)

        # elif self.vertice == 'topleft':

        #     # pos_rect = self.sprite.get_frect(topleft=position)
        #     position = position

        random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=12))


        gameScreen.windows[self.surface_to_draw_on].drawing_queue[random_id] = {'game_object':'obj',
                                        'asset_to_draw':self.sprite,
                                        'debug':self,
                                        'asset_type':asset_type,
                                        'z_layer':self.zlayer_drawing,
                                        'surface_to_draw_on':self.surface_to_draw_on,
                                        'game_object_origin':game_object_origin,
                                        'is_animated':is_animated,
                                        'animation_length':animation_length,
                                        'animation_timer':animation_length,
                                        'position':position,
                                        'position_rect':pos_rect,
                                        'value':value,
                                        'is_critical':is_critical,
                                        'sin_waveY':math.radians(90),
                                        'sin_waveX':0,
                                        'sin_waveX_movement':random.choice(['positive','negative']),
                                        'initial_width':initial_width,
                                        'initial_height':initial_height,
                                        'scale_factor_timer':1,
                                        'alpha':255,
                                        'ignore_offset':self.ignoreCameraOffset,
                                        'schedule_deletion':schedule_deletion}

    def draw_rect(self,asset_type:str='rect',game_object_origin:str='game',schedule_deletion:bool=True,
                  is_animated:bool=False,animation_length:int=0,position:tuple=(0,0),value:int=0,is_critical:bool=False,rect_colour:str='blue',
                  zlayer:int=1):

        
        gameScreen.windows[self.surface_to_draw_on].drawing_queue[f"{id(self)}_rect"] = {'game_object':self,
                                                      'asset_to_draw':self.hurtbox,
                                                      'asset_type':asset_type,
                                                      'z_layer':zlayer,
                                                      'surface_to_draw_on':self.surface_to_draw_on,
                                                      'game_object_origin':game_object_origin,
                                                      'is_animated':is_animated,
                                                      'animation_length':animation_length,
                                                      'animation_timer':animation_length,
                                                      'position':position,
                                                      'position_rect':None,
                                                      'value':value,
                                                      'is_critical':is_critical,
                                                      'sin_waveY':math.radians(90),
                                                      'sin_waveX':0,
                                                      'sin_waveX_movement':random.choice(['positive','negative']),
                                                      'initial_width':None,
                                                      'initial_height':None,
                                                      'scale_factor_timer':1,
                                                      'alpha_value':1,
                                                      'rect_colour':rect_colour,
                                                      'schedule_deletion':schedule_deletion}
        
    def draw_hitbox(self,asset_type:str='rect',game_object_origin:str='game',schedule_deletion:bool=True,
                  is_animated:bool=False,animation_length:int=0,position:tuple=(0,0),value:int=0,is_critical:bool=False,rect_colour:str='blue',
                  zlayer:int=1):

        
        gameScreen.windows[self.surface_to_draw_on].drawing_queue[f"{id(self)}_rect"] = {'game_object':self,
                                                      'asset_to_draw':self.hitboxes[0][0].hitbox,
                                                      'asset_type':asset_type,
                                                      'z_layer':zlayer,
                                                      'surface_to_draw_on':self.surface_to_draw_on,
                                                      'game_object_origin':game_object_origin,
                                                      'is_animated':is_animated,
                                                      'animation_length':animation_length,
                                                      'animation_timer':animation_length,
                                                      'position':position,
                                                      'position_rect':None,
                                                      'value':value,
                                                      'is_critical':is_critical,
                                                      'sin_waveY':math.radians(90),
                                                      'sin_waveX':0,
                                                      'sin_waveX_movement':random.choice(['positive','negative']),
                                                      'initial_width':None,
                                                      'initial_height':None,
                                                      'scale_factor_timer':1,
                                                      'alpha_value':1,
                                                      'rect_colour':rect_colour,
                                                      'schedule_deletion':schedule_deletion}



