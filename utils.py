import random,string
import pygame,math,sys
from pygame.math import Vector2
from .screen import gameScreen

# given a dictionary of stat value pairs, change hte value of the stats with getattr
def set_attributes(game_object,attributes:dict):

    for att,val in attributes.items():
        setattr(game_object,att,val)

# given a dictionary of stat value pairs, change hte value of the stats with getattr
def store_original_vars(game_object):

    game_object.original_vars = {k:v for k,v in game_object.__dict__.items()}

# function to link set attirbutes, init and storing original values on obj start
def start(game_object,attributes:dict):

    set_attributes(game_object=game_object,attributes=attributes)
    game_object.init()
    store_original_vars(game_object=game_object)

# clamp function, return value not lower and not higher than min.max
def clamp(n:float, min:float, max:float) -> float:
    if n < min:
        return min
    elif n > max:
        return max
    else:
        return n
    
# give weapon to game object
def give_weapon(gameobj:object,weaponName:str,weaponClass:classmethod,weaponParams:dict):

    # skip if giving first weapon
    if gameobj.weapon:
        
        # first end weapon state
        gameobj.weapon.state.completed()

        # find first element in list which is current weapon
        current_weapon = gameobj.inventory.inventory['weapons'][0]
        
    # set weapon to give to player
    weapon_to_give = weaponName

    # handle inventory 
    if len(gameobj.inventory.inventory['weapons']) < gameobj.weaponCarryLimit:

        # remove current weapon and add to end of list
        gameobj.inventory.inventory['weapons'].insert(0,weapon_to_give)


    elif len(gameobj.inventory.inventory['weapons']) >= gameobj.weaponCarryLimit:

        # remove current weapon and add to end of list
        gameobj.inventory.inventory['weapons'].remove(current_weapon)
        gameobj.inventory.inventory['weapons'].insert(0,weapon_to_give)

    # check if the weapon is not in the cache
    if weapon_to_give not in gameobj.cachedWeapons:
        
        # create weapon obj and init new weapon
        weapon = weaponClass()
        set_attributes(game_object=weapon,attributes=weaponParams[weapon_to_give])
        weapon.init()
        store_original_vars(game_object=weapon)

        gameobj.weapon = weapon
        gameobj.weapon.wielded_by = gameobj

        # enter state
        gameobj.weapon.state = gameobj.weapon.states['PICKUP']
        gameobj.weapon.state.enter()

        # add weapon to cache
        gameobj.cachedWeapons[weaponName] = weapon

    # check if the weapon is not in the cache
    elif weapon_to_give in gameobj.cachedWeapons:

        gameobj.weapon = gameobj.cachedWeapons[weaponName]
        gameobj.weapon.wielded_by = gameobj

        # enter state
        gameobj.weapon.state = gameobj.weapon.states['PICKUP']
        gameobj.weapon.state.enter()

    # add weapon to roulette pool if it has been picked before
    weaponParams[weaponName]['inWeaponBox'] = True

# swap weapon function
def swap_weapon(gameObject:object):

    if len(gameObject.inventory.inventory['weapons']) > 1:

        # first end weapon state
        gameObject.weapon.state.completed()

        # find first element in list which is current weapon
        current_weapon = gameObject.inventory.inventory['weapons'][0]
        
        # find second element in list which is next weapon
        next_weapon = gameObject.inventory.inventory['weapons'][1]

        # remove current weapon and add to end of list
        gameObject.inventory.inventory['weapons'].pop(0)
        gameObject.inventory.inventory['weapons'].append(current_weapon)

        # set new weapon
        gameObject.weapon = gameObject.cachedWeapons[next_weapon]
        # give_weapon(gameobj=self,weaponName=next_weapon,weaponClass=Gun,weaponParams=gun_parameters)
        gameObject.weapon.wielded_by = gameObject

        # enter state
        gameObject.weapon.state = gameObject.weapon.states['PULLOUT']
        gameObject.weapon.state.enter()

# remove weapon function
def remove_weapon(gameObject:object):

    # swap weapon
    swap_weapon(gameObject=gameObject)

    # now remove weapon in second slot
    secondSlotWeapon = gameObject.inventory.inventory['weapons'][1]
    gameObject.inventory.inventory['weapons'].remove(secondSlotWeapon)

# function to find out if an event proced given the percentage chance
# pro chance is given as a percentage i.e 10% or 50%
def proc(proc_chance:float):

    # dvidie by 100
    proc_chance = proc_chance/100


    if proc_chance >= 1:
        proc_chance = 1

    elif proc_chance <= 0:
        proc_chance = 0

    # random.random generates a random floating point number
    if random.random() < proc_chance:
        return True

    return False

# given a group of events/items with weights, return an item
# items with higher weight have a greater chance of being selected
# dict needs to have key as a string, and v as the weight
def proc_using_weights(ItemWeights:dict):

    # get only the item name and the weight for this specific pool into a dictionary
    DictOfItems = {}

    # extract all the weights for all items
    for item in ItemWeights:

        DictOfItems[item] = ItemWeights[item]

    # get the sum of all the weightings
    SumOfWeights = sum(list(DictOfItems.values()))

    # order dictg of items so all the items with a weight of 0 are just excluded first
    OrderedDictOfItems = sorted(DictOfItems,key=lambda x:DictOfItems[x])

    # create a random number between 0.1 and the sum of all weightings. 0.1 and the sum of weights are inclusive
    # this also ensures that items with a wieght of 0 are excluded
    random_number = random.uniform(0.1,SumOfWeights)

    # set previous chance and next chance vars
    # because the random number is goign to be 0.1 or greater it will always be caught
    # because the first chance just has to be geater than 0
    previous_chance = 0
    next_chance = 0

    # go through dict of items orderered by their weight
    for item in OrderedDictOfItems:

        # update next chance
        next_chance += DictOfItems[item]

        if (random_number > previous_chance) and (random_number <= next_chance):

            # uncomment to find result
            # print(random_number,'num')
            # print(item,'item')
            return item

        else: # update previous chance
                previous_chance = next_chance


# linear interpolation value
# t is the fraction of time that has elapsed, start is the start value, end is the end value we want to reach
def linear_lerp(start:float,end:float,t:float):

    # limit t
    t = min(1,t)
    
    return start + (end - start) * t
  
# calculate manhattan distance
def calculate_manhattan(point_A_coors, point_B_coors):

    x_val = abs(point_A_coors[0]-point_B_coors[0])
    y_val = abs(point_A_coors[1]-point_B_coors[1])

    return x_val + y_val

# given two points, find the distance between them
def find_dist_between_points(p1:tuple,p2:tuple):

    return (Vector2(p1) - Vector2(p2)).length()

# given two points, return True if theya re within a certain distance to each other
def is_within_range(p1:tuple,p2:tuple,distance:float):

    if find_dist_between_points(p1,p2) <= distance:
        return True
    return False

# given a point and tile width/height. find the topleft coordinate of the tile the point is on
def find_tile_topleft(point:tuple,tile_width:int=32,tile_height:int=32):

    # separate mouse pos into x and y
    x,y = point

    # now here we integer divide by the tile size, and multiply by the tile size to get the top left corner of the rect we want to place
    # its hard to explain but if we integer divide the position of the mouse by the tile size we always get the top left coordinates
    tile_x = (x//tile_width) * tile_width
    tile_y = (y//tile_height) * tile_height

    # return the coors
    return (tile_x,tile_y)

# given a tile pos, a rect size, a tile size, return all the topleft coors within that rect
def breakdown_rect(point:tuple=(0,0),rect_width:int=32,rect_height:int=32,tile_size:int=32) -> list:

    tiles = []

    for x in range(rect_width//tile_size):
        for y in range(rect_height//tile_size):

            tiles.append((point[0]+(x*tile_size),point[1]+(y*tile_size)))
             

    return tiles

# given a tile pos, a rect size, a tile size, return all the topleft coors within that rect
def breakdown_centered_rect(point:tuple=(0,0),rect_width:int=32,rect_height:int=32,tile_size:int=32) -> list:

    tiles = []

    for x in range(rect_width//tile_size):
        for y in range(rect_height//tile_size):

            # cp = centerpoint
            cp = (point[0]+(x*tile_size),point[1]+(y*tile_size))

            # given a tile with that center, in a 32x32 grid
            tl = (cp[0] - tile_size//2, cp[1] - tile_size//2)
            tr = (cp[0] + tile_size//2, cp[1] - tile_size//2)
            bl = (cp[0] - tile_size//2, cp[1] + tile_size//2)
            br = (cp[0] + tile_size//2, cp[1] + tile_size//2)

            tiles.extend([tl,tr,bl,br])

    return list(set(tiles))

# given a rect, and a point to recenter to, return the repoisitoned rect as a list
def reposition_rect(rect:list,point:tuple=(0,0),tile_size:int=32) -> list:

    _,_,w,h = rect


    new_x = point[0] + 16 - w // 2
    new_y = point[1] + 16 - h // 2

    return [new_x,new_y,w,h]

# return random point in a circle of X radius and (x,y) center
def sample_random_point_circle(radius:float,circle_center:tuple):

        random_angle = random.randint(0,359)

        # return point on circle at that angle
        return (circle_center[0] + (radius * math.cos(math.radians(random_angle))),circle_center[1] + (radius * math.sin(math.radians(random_angle))))

# find the centre of a tile
def find_tile_centre(point:tuple,tile_width=32,tile_height=32):

    return (point[0]+(tile_width/2),point[1]+(tile_height/2)) # changed from integer division to regular


# sin wave function
def find_sine_value(t:float=0,amplitude:float=1):

    return math.sin(t) * amplitude

# helps determine where bullets are shot
def find_raycast(number_of_casted_rays:int=1,raycast_depth:int=1,raycast_width:int=10,starting_point:tuple=(0,0),target_point:tuple=(0,0),raycast_angle_offset:float=0):

    # get vector from player to gun
    # new_pos = target_pos - (Vector2(starting_pos)-Vector2(self.start_point))
    # the mouse pos can just be any position a certain depth/length away form the starting position
    # starting pos can either be where the bullet originates from. if using dual wield then to control the depth of the shot
    # it should be the entity like the player which the dual wield is attached to

        # FOV simply defines how wide you want the player fov to be. In this case we have set it be 60 because math.pi is 180 degrees
    # half FOV is FOV split into 2. So imagining an FOV 60 degrees wide and split down the middle. To the left of that middle line is 30 degrees
    # to the right of that middle line is another 30 degrees
    # depth var, affects length of FOV
    DEPTH = raycast_depth

    # calculate distance from mouse to player center, on the left is where the rays are pointing to, on the right is where the rays orgininate from
    direction_vectorX,direction_vectorY = Vector2(target_point) - Vector2(starting_point)
    controlled_depth_endpoint = (0,0)

    # get the angle of the line going from the player center to the mouse
    player_angle = math.atan2(direction_vectorY,direction_vectorX) + raycast_angle_offset # this can be offset

    # given the mouse as the end point, calculate what the max depth is, just use the x pos to find the depth
    max_depth = (target_point[0] - starting_point[0])/math.sin(player_angle)


    # middle line, the fov width is then added and subtracted to this to get the full line of sight area
    FOV_CENTER = player_angle 
    FOV_WIDTH = math.radians(raycast_width)
    STARTING_ANGLE = FOV_CENTER + FOV_WIDTH # this gets angle on the leftmost side
    ENDING_ANGLE = FOV_CENTER - FOV_WIDTH

    # CASTED RAYS varibale, number of rays we want in the FOV cone
    # CASTED_RAYS = self.weapon_fov_rays
    CASTED_RAYS = number_of_casted_rays

    # se tstep angle to be 0 byd efault, assuming we are only shooting down the middle line of the LOS
    # STEP_ANGLE = 0

    # but if casted rays are more than 1
    # get step which is start - end divide by casted rays. the -1 makes sure the ray in the middle is always drawn
    # if CASTED_RAYS > 1:
    STEP_ANGLE = (STARTING_ANGLE-ENDING_ANGLE)/(CASTED_RAYS-1)

    # get the endpoint for the cetner ray with reduced depth
    # set a MAX depth
    # if it is higher than the max depth then set the end point to the max depth
    # if max_depth >= DEPTH:

    #     # set end point using max depth
    #     controlled_depth_endpoint = (starting_point[0] + math.sin(player_angle)*DEPTH,starting_point[1] + math.cos(player_angle)*DEPTH)
    #     DEPTH = raycast_depth

    # # if the depth is below the max depth
    # elif max_depth < DEPTH:

    #     # set end poitn using the mouse pos depth
    #     controlled_depth_endpoint = target_point
    #     DEPTH = max_depth


    # now that depth has been adjusted, use the original angle to find where the bullet would have been shot to with no offset
    # having the target destination be at the center line from the player to mouse doesnt take into consideration
    # that there are bullets that use offset angles, so it messes up code for bullets that dont follow curved paths
   

    raynumber_endpoint = {}

    # # # draw all casted rays
    for ray in range(CASTED_RAYS):

        # regular target x and target y. The one before is for drawingf and ahs an offset, this is the true position of the TIP of the FOV rays
        endpoint_x = starting_point[0] + (math.cos(STARTING_ANGLE)*DEPTH)
        endpoint_y = starting_point[1] + (math.sin(STARTING_ANGLE)*DEPTH)
        endpoint = (endpoint_x,endpoint_y)

        # add the ray number and the end point to the dictionary
        raynumber_endpoint[ray] = endpoint # used for straight shot

        # increment starting angle by a single step until we reach end angle
        STARTING_ANGLE -= STEP_ANGLE

    # return the ray and end point
    return raynumber_endpoint

# helps determine where bullets are shot
def find_raycast2(starting_position:tuple=(0,0),target_position:tuple=(0,0),casted_rays:int=1,raycast_depth:int=1,raycast_width:int=10,raycast_angle_offset:float=0):

    # if target and start are the same return nothing 
    if starting_position == target_position:
        return {}
    
    # get vector from player to gun
    # new_pos = target_pos - (Vector2(starting_pos)-Vector2(self.start_point))
    # the mouse pos can just be any position a certain depth/length away form the starting position
    # starting pos can either be where the bullet originates from. if using dual wield then to control the depth of the shot
    # it should be the entity like the player which the dual wield is attached to

        # FOV simply defines how wide you want the player fov to be. In this case we have set it be 60 because math.pi is 180 degrees
    # half FOV is FOV split into 2. So imagining an FOV 60 degrees wide and split down the middle. To the left of that middle line is 30 degrees
    # to the right of that middle line is another 30 degrees
    # depth var, affects length of FOV
    DEPTH = raycast_depth

    # calculate distance from mouse to player center, on the left is where the rays are pointing to, on the right is where the rays orgininate from
    direction_vectorX,direction_vectorY = Vector2(target_position) - Vector2(starting_position)
    controlled_depth_endpoint = (0,0)

    # get the angle of the line going from the player center to the mouse
    player_angle = math.atan2(direction_vectorY,direction_vectorX) + math.radians(raycast_angle_offset) # this can be offset

    # given the mouse as the end point, calculate what the max depth is, just use the x pos to find the depth
    # max_depth = (self.target_position[0] - self.starting_position[0])/math.sin(player_angle)


    # middle line, the fov width is then added and subtracted to this to get the full line of sight area
    FOV_CENTER = player_angle 
    FOV_WIDTH = math.radians(raycast_width)
    STARTING_ANGLE = FOV_CENTER + FOV_WIDTH # this gets angle on the leftmost side
    ENDING_ANGLE = FOV_CENTER - FOV_WIDTH

    # CASTED RAYS varibale, number of rays we want in the FOV cone
    # CASTED_RAYS = self.weapon_fov_rays
    CASTED_RAYS = casted_rays

    # se tstep angle to be 0 byd efault, assuming we are only shooting down the middle line of the LOS
    # STEP_ANGLE = 0

    # but if casted rays are more than 1
    # get step which is start - end divide by casted rays. the -1 makes sure the ray in the middle is always drawn
    # if CASTED_RAYS > 1:
    STEP_ANGLE = (STARTING_ANGLE-ENDING_ANGLE)/(CASTED_RAYS-1)

    # get the endpoint for the cetner ray with reduced depth
    # set a MAX depth
    # if it is higher than the max depth then set the end point to the max depth
    # if max_depth >= DEPTH:

    #     # set end point using max depth
    #     controlled_depth_endpoint = (self.starting_position[0] + math.sin(player_angle)*DEPTH,self.starting_position[1] + math.cos(player_angle)*DEPTH)
    #     DEPTH = raycast_depth

    # # if the depth is below the max depth
    # elif max_depth < DEPTH:

    #     # set end poitn using the mouse pos depth
    #     controlled_depth_endpoint = self.target_position
    #     DEPTH = max_depth


    # now that depth has been adjusted, use the original angle to find where the bullet would have been shot to with no offset
    # having the target destination be at the center line from the player to mouse doesnt take into consideration
    # that there are bullets that use offset angles, so it messes up code for bullets that dont follow curved paths
    raynumber_ray = {}

    # # # draw all casted rays
    for ray in range(CASTED_RAYS):

        # regular target x and target y. The one before is for drawingf and ahs an offset, this is the true position of the TIP of the FOV rays
        endpoint_x = starting_position[0] + (math.cos(STARTING_ANGLE)*DEPTH)
        endpoint_y = starting_position[1] + (math.sin(STARTING_ANGLE)*DEPTH)
        endpoint = (endpoint_x,endpoint_y)

        # add the ray number and the end point to the dictionary
        raynumber_ray[ray] = (starting_position,endpoint) # used for straight shot

        # increment starting angle by a single step until we reach end angle
        STARTING_ANGLE -= STEP_ANGLE

    return raynumber_ray
    
def bressenham2(start, end, tile_size):
    x0, y0 = start
    x1, y1 = end

    dx = x1 - x0
    dy = y1 - y0

    step_x = 1 if dx > 0 else -1
    step_y = 1 if dy > 0 else -1

    dx = abs(dx)
    dy = abs(dy)

    # Current tile
    tile_x = int(x0 // tile_size)
    tile_y = int(y0 // tile_size)

    # Distance to next grid boundary
    if dx != 0:
        t_max_x = ((tile_x + (step_x > 0)) * tile_size - x0) / dx
        t_delta_x = tile_size / dx
    else:
        t_max_x = float("inf")
        t_delta_x = float("inf")

    if dy != 0:
        t_max_y = ((tile_y + (step_y > 0)) * tile_size - y0) / dy
        t_delta_y = tile_size / dy
    else:
        t_max_y = float("inf")
        t_delta_y = float("inf")

    while True:
        yield (tile_x, tile_y)

        if t_max_x < t_max_y:
            t_max_x += t_delta_x
            tile_x += step_x
        else:
            t_max_y += t_delta_y
            tile_y += step_y

        # stop when we reach end tile
        if (tile_x == int(x1 // tile_size) and
            tile_y == int(y1 // tile_size)):
            yield (tile_x, tile_y)
            break

def bresenham(x0, y0, x1, y1):
        """Yield integer coordinates on the line from (x0, y0) to (x1, y1).

        Input coordinates should be integers.

        The result will contain both the start and the end point.
        """
        dx = x1 - x0
        dy = y1 - y0

        xsign = 1 if dx > 0 else -1
        ysign = 1 if dy > 0 else -1

        dx = abs(dx)
        dy = abs(dy)

        if dx > dy:
            xx, xy, yx, yy = xsign, 0, 0, ysign
        else:
            dx, dy = dy, dx
            xx, xy, yx, yy = 0, ysign, xsign, 0

        D = 2*dy - dx
        y = 0

        for x in range(dx + 1):

            point = x0 + x*xx + y*yx, y0 + x*xy + y*yy
            px,py = point
            tile = find_tile_topleft(point=(px,py))
            # astar_tile = (tile[0] + 16,tile[1]+16)

            # if tile in Creative_Mode.all_walls:
            #     break
            # yield x0 + x*xx + y*yx, y0 + x*xy + y*yy
            yield tile
            if D >= 0:
                y += 1
                D -= 2*dx
            D += 2*dy



# intersection of two lines
def intersect_segments(p0, p1, q0, q1, eps=1e-8):
    x1, y1 = p0
    x2, y2 = p1
    x3, y3 = q0
    x4, y4 = q1

    # Direction vectors
    dx1 = x2 - x1
    dy1 = y2 - y1
    dx2 = x4 - x3
    dy2 = y4 - y3

    # Cross product (determinant)
    d = dx1 * dy2 - dy1 * dx2

    if abs(d) < eps:
        # Parallel or collinear
        return None

    # Solve for t and u
    t = ((x3 - x1) * dy2 - (y3 - y1) * dx2) / d
    u = ((x3 - x1) * dy1 - (y3 - y1) * dx1) / d

    # Check if intersection is within both segments
    if 0 <= t <= 1 and 0 <= u <= 1:
        ix = x1 + t * dx1
        iy = y1 + t * dy1
        return (ix, iy)

    return None

# given a list of values, return the median value or median x values    
def find_median_values(array_of_values:list,number_to_return:int=1):

        sortedLst = sorted(array_of_values)
        lstLen = len(array_of_values)

        if (lstLen % 2) == 0:

            middle_index = math.ceil(lstLen/2)
            start_index = middle_index - (number_to_return//2)
            return sortedLst[start_index:start_index+number_to_return]

         


        else:

            middle_index = math.ceil((lstLen-1)/2)

            start_index = middle_index - (number_to_return//2)
         
            return sortedLst[start_index:start_index+number_to_return]
        
# functions for drawing
def draw_line(startpos:tuple=(0,0),endpos:tuple=(0,0),asset_to_draw=None,asset_type:str='line',game_object_origin:str='Map',is_animated:bool=False,
                       animation_length:int=0,position:tuple=(0,0),value:int=0,is_critical:bool=False,z_layer:int=2):


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

# functions for drawing
def draw_lines(points:tuple=[(0,0),(1,1)],asset_to_draw=None,asset_type:str='lines',game_object_origin:str='Map',is_animated:bool=False,
                       animation_length:int=0,position:tuple=(0,0),value:int=0,is_critical:bool=False,z_layer:int=2):


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
                                                    'points':points,
                                                    'schedule_deletion':True}


# get mro
def get_mro(gameObject):

    return [x.__name__ for x in gameObject.__class__.__mro__]

# check if a list is in another list
def array_is_in_array(array1:list,array2:list):

    # Convert lists to sets and check for intersection
    return set(array2) & set(array1)

# delete states from memory
def clear_states(statesDict):

    # store keys for states dict
    states = list(statesDict.keys())

    for state in states:
        
        del statesDict[state]
        
    
# find if a list contains a class you want
def find_class_in_array(targetClass:object='',array:list=[]):
    
    return [x for x in array if x.__class__.__name__ == targetClass]
    
    
    

    