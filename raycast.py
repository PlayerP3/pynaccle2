import random,math,string
from pygame.math import Vector2
from .objectsystem import objectManager
from .utils import *
from .screen import gameScreen


class Raycast():

    def __init__(self,casted_rays:int=1,raycast_depth:int=1,raycast_width:int=10,raycast_angle_offset:float=0,starting_position:tuple=(0,0),target_position:tuple=(0,0)):

        self.display = False
        self.casted_rays = casted_rays
        self.raycast_depth = raycast_depth
        self.raycast_width = raycast_width
        self.raycast_angle_offset = raycast_angle_offset
        self.starting_position = starting_position
        self.target_position = target_position
        self.objects_colliding_with_raycast = {} # stores the ray number and the objects e.g 0 : [wall,player]
        self.raynumber_ray = {}
        

        # fog of war circular raycast var
        self.fow_casted_rays = 360
        self.fow_raycast_depth = 30
        self.fow_raycast_width = 100
        self.fow_raycast_angle_offset = 180

    # reinit
    def init(self,attributes:dict={}):

        for att,val in attributes.items():

            setattr(self,att,val)

    # store the raycast which is the raynumbers and then the actual ray/line
    def get_raycast(self):

        # if target and start are the same return nothing 
        self.raynumber_ray = find_raycast2(starting_position=self.starting_position,target_position=self.target_position,casted_rays=self.casted_rays,
                      raycast_depth=self.raycast_depth,raycast_width=self.raycast_width,raycast_angle_offset=self.raycast_angle_offset)

    def get_middle_line(self):

        return [self.raynumber_ray[ind] for ind in find_median_values(array_of_values=self.raynumber_ray.keys(),number_to_return=1)]
        
    # MIGHT BE VERY COMPUTATIONALLY EXPENSIVE
    # get list of objs colliding with raycast
    def find_objects_colliding_with_raycast(self):

        # reset dict 
        self.objects_colliding_with_raycast = {}

        # go through all the rays in the raycast
        for rnum in self.raynumber_ray:

            self.objects_colliding_with_raycast[rnum] = []
        

            ray = self.raynumber_ray[rnum]
        
            # find all tiles that the line intersects
            intersected_tiles = bresenham(int(ray[0][0]),int(ray[0][1]),int(ray[1][0]),int(ray[1][1]))

            # get all objects on the intersected tiles
            for tile in list(set(intersected_tiles)):
                
                if tile in objectManager.object_positions:

                    self.objects_colliding_with_raycast[rnum].extend(objectManager.object_positions[tile])

        # filter objects colldied with
        self.filter_objects_colliding_with_raycast()

    # keep objects we are interested in detecting collisions for with raycast
    def filter_objects_colliding_with_raycast(self,filtered_obj_classes=['Wall']):

        # removing ray numbers
        rnum_to_delete = []

        # keep walls only
        for rnum,gobjs in self.objects_colliding_with_raycast.items():

            # filter gobjs to only keep walls
            gobjs = [myobj for myobj in gobjs if myobj.__class__.__name__ in filtered_obj_classes]

            # store to delete ray number entry in dict of ray number gobjs colldied with
            if not gobjs:
                rnum_to_delete.append(rnum)

            elif gobjs:
                self.objects_colliding_with_raycast[rnum] = gobjs

        # delete empty ray numbers in the collision dict
        for rnum in rnum_to_delete:
            del self.objects_colliding_with_raycast[rnum]

    # get closest object that hit the raycast
    def get_closest_object(self):

        if self.objects_colliding_with_raycast:

            collided_objects = []

            # get list of collided objects
            for rnum,gobjs in self.objects_colliding_with_raycast.items():

                collided_objects.extend(gobjs)

            return min(list(set(collided_objects)),key = lambda item:(Vector2(self.starting_position)-Vector2(item.hurtbox.center)).length())

        else:
            return None 

    def display_fog_of_war(self):

        # if there are any valid collisions remaining 
        if self.objects_colliding_with_raycast:
            
            # get ray numbber and ray and game objects that colldied with the ray
            for rnum,gobjs in self.objects_colliding_with_raycast.items():

                # get ray at ray number
                ray = self.raynumber_ray[rnum]

                # find closest object 
                closest_object = min(gobjs,key=lambda x:(Vector2(ray[0])-Vector2(x.hurtbox.center)).length())
                
                # if gobj.hurtbox.clipline(ray):

                t = (closest_object.hurtbox.topleft,closest_object.hurtbox.topright)
                b = (closest_object.hurtbox.bottomleft,closest_object.hurtbox.bottomright)
                l = (closest_object.hurtbox.topleft,closest_object.hurtbox.bottomleft)
                r = (closest_object.hurtbox.topright,closest_object.hurtbox.bottomright) 

                # get hurtbox segments
                hurtbox_segments = [t,b,l,r]

                # find intersection between segment and ray
                intersections = [intersect_segments(*ray,*seg) for seg in hurtbox_segments]

                # filter to only keep real hits
                intersections = [intsct for intsct in intersections if intsct]

                # find closest intersection if there is actually any intersection found
                if intersections:

                    # get the closest intersection
                    # if min more realistic and dont see past wall
                    # if max stillr elaistic but you can see wall, but nothjign past it
                    poi = max(intersections,key=lambda x:(Vector2(ray[0])-Vector2(x)).length())

                    # but actually if the end point for the ray is in the wall then go with that instead
                    # fixes issues with max where a ray is int he wall but it doesnt look good if its colliding with just one segment
                    if closest_object.hurtbox.collidepoint(ray[1]):
                        
                        poi = ray[1]

                    self.raynumber_ray[rnum] = (ray[0],poi)

                else:
                    continue

        # drawing the actual fog
        
        # get endpoints for drawing the little circle at the back of the raycast
        fow_raynumber_ray = find_raycast2(starting_position=self.starting_position,target_position=self.target_position,casted_rays=self.fow_casted_rays,
                      raycast_depth=self.fow_raycast_depth,raycast_width=(360-self.fow_raycast_width),raycast_angle_offset=self.fow_raycast_angle_offset)

        fow_endpoints = [(ray[1][0],ray[1][1]) for rnum,ray in fow_raynumber_ray.items()]

        # invert endpoints
        fow_endpoints = fow_endpoints[::-1]

        # get ray endpoints from normal view
        endpoints = [(ray[1][0],ray[1][1]) for rnum,ray in self.raynumber_ray.items()]

        # add normal view to fog of war
        fow_endpoints.extend(endpoints)

        # Draw the visible area polygon, because the fog surface has a white keycolour we cutout the visible area based on the triangles forming
        if len(fow_endpoints) > 2:

            # so because we are blitting the window onto the fog surface, it also follows the color key rules where anything white is shown
            # draw triangles and fill with white so we can see everything not in the fog
            self.draw_polygon(endpoints=fow_endpoints,ignore_offset=False)

        gameScreen.windows['fog_of_war'].win.fill((0,0,0))
        
        # draw wincopy onto fog surface
        self.draw_fog_onto_copy(ignore_offset=True)

        # draw fog of war surface
        self.draw_surface(ignore_offset=True)

    def draw_fog_onto_copy(self,asset_type:str='surface',game_object_origin:str='game',is_animated:bool=False,
                       animation_length:int=0,position:tuple=(0,0),value:int=0,is_critical:bool=False,initial_width:int=0,initial_height:int=0,
                       zlayer:int=0,alpha:int=100,ignore_offset:bool=False):

        # pos_rect = gameScreen.windows['win'].win.get_frect(center=position)

        # pos_rect = self.sprite.get_frect(center=position)#
        position = (position[0] - (gameScreen.windows['win'].win.get_width()/gameScreen.windows['fog_of_war'].zoom)//2,position[1] - (gameScreen.windows['win'].win.get_height()//gameScreen.windows['fog_of_war'].zoom)//2)

        random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

        gameScreen.windows['fog_of_war'].drawing_queue[random_id] = {'game_object':'obj',
                                        'asset_to_draw':gameScreen.windows['wincopy'].win,
                                        'asset_type':asset_type,
                                        'z_layer':zlayer,
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
                                        'initial_width':initial_width,
                                        'initial_height':initial_height,
                                        'scale_factor_timer':1,
                                        'alpha':alpha,
                                        'ignore_offset':ignore_offset,
                                        'schedule_deletion':True}
        
    # adjust alpha on fog of war surface to determien if we see objects like transparency wise
    def draw_surface(self,asset_type:str='surface',game_object_origin:str='game',is_animated:bool=False,
                       animation_length:int=0,position:tuple=(0,0),value:int=0,is_critical:bool=False,initial_width:int=0,initial_height:int=0,
                       zlayer:int=2,alpha:int=100,ignore_offset:bool=False):

        # pos_rect = gameScreen.windows['fog_of_war'].win.get_frect(center=position)

        position = (position[0] - (gameScreen.windows['fog_of_war'].win.get_width()/gameScreen.windows['win'].zoom)//2,position[1] - (gameScreen.windows['fog_of_war'].win.get_height()//gameScreen.windows['win'].zoom)//2)


        random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

        gameScreen.windows['win'].drawing_queue[random_id] = {'game_object':'obj',
                                        'asset_to_draw':gameScreen.windows['fog_of_war'].win,
                                        'asset_type':asset_type,
                                        'z_layer':zlayer,
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
                                        'initial_width':initial_width,
                                        'initial_height':initial_height,
                                        'scale_factor_timer':1, 
                                        'alpha':alpha,
                                        'ignore_offset':ignore_offset,
                                        'schedule_deletion':True}
        
    def draw_polygon(self,asset_type:str='polygon',game_object_origin:str='game',is_animated:bool=False,
                    animation_length:int=0,position:tuple=(0,0),value:int=0,is_critical:bool=False,initial_width:int=0,initial_height:int=0,endpoints:list=[],
                    zlayer:int=1,alpha:int=1,ignore_offset:bool=False):

        # pos_rect = gameScreen.windows['win'].win.get_frect(center=position)

        position = (position[0] - (gameScreen.windows['fog_of_war'].win.get_width()/gameScreen.windows['win'].zoom)//2,position[1] - (gameScreen.windows['fog_of_war'].win.get_height()//gameScreen.windows['win'].zoom)//2)


        random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

        gameScreen.windows['fog_of_war'].drawing_queue[random_id] = {'game_object':'obj',
                                        'asset_to_draw':None,
                                        'asset_type':asset_type,
                                        'z_layer':zlayer,
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
                                        'initial_width':initial_width,
                                        'initial_height':initial_height,
                                        'scale_factor_timer':1,
                                        'alpha':alpha,
                                        'endpoints':endpoints,
                                        'ignore_offset':ignore_offset,
                                        'schedule_deletion':True}

    def draw_lines(self,asset_to_draw=None,asset_type:str='line',game_object_origin:str='Map',is_animated:bool=False,
                       animation_length:int=0,position:tuple=(0,0),value:int=0,is_critical:bool=False,z_layer:int=2):

        for rnum in self.raynumber_ray:

            ray = self.raynumber_ray[rnum]

            startpos,endpos = ray

            random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=12))


            gameScreen.windows['win'].drawing_queue[random_id] = {'game_object':'Dmg num',
                                                        'asset_to_draw':asset_to_draw,
                                                        'asset_type':asset_type,
                                                        'z_layer':z_layer,
                                                        'game_object_origin':game_object_origin,
                                                        'is_animated':is_animated,
                                                        'animation_length':animation_length,
                                                        'animation_timer':animation_length,
                                                        'position':position,
                                                        'value':value,
                                                        'is_critical':is_critical,
                                                        'sin_waveY':0,
                                                        'sin_waveX':0,
                                                        'sin_waveX_movement':random.choice(['positive','negative']),
                                                        'scale_factor_timer':1,
                                                        'alpha_value':1,
                                                        'startpos':startpos,
                                                        'endpos':endpos,
                                                        'schedule_deletion':True}


    
     
    # function to display the raycast
    def apply_fog_of_war(self):

        self.get_raycast()

        self.find_objects_colliding_with_raycast()

        self.display_fog_of_war()

    # find objects colliding with raycast
    def detect_collision_with_raycast(self):

        # create raycast
        self.get_raycast()

        # find objects colliding with it
        self.find_objects_colliding_with_raycast()

        # draw raycast
        if self.display:
            endpoints = []

            for rnum,ray in self.raynumber_ray.items():

                endpoints.append(ray[1])

            endpoints.insert(0,self.starting_position)
            
            if len(endpoints) > 2:
            
                self.draw_polygon(zlayer=5,endpoints=endpoints)