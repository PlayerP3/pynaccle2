import pygame,random,json,os,math,sys
from pygame.math import Vector2
from .moveableobject import Moveable_Object
from .utils import *
from .timer import Timer
from .objectsystem import objectManager

# from statemachine import StateMachine




class Weapon():

    def __init__(self,name:str='Weapon',magazine_size:int=8,total_ammo_stock:int=0,select_fire:str='fullauto',
                 
                fire_rate:float=2,reload_speed:float=3,triggerResetSpeed:float=0,weight:float=0.1,
                
                casted_rays:int=2,raycast_depth:int=1,raycast_width:int=1,raycast_angle_offset:int=0,
                
                shot_spread_pattern:str='perfect',shot_spread_number:int=0,is_dual_wield:bool=False,dualWieldCopy:str='same',img_path:str='',

                inWeaponBox:bool = True):

        self.name = name
        self.weight = weight

        # if same we keep the same gun obj and just have a different sprite where bullets come out from
        # if unique we make a new weapon for the right hand
        self.dualWieldCopy = dualWieldCopy


        self.img_path = img_path
        self.fire_rate = fire_rate
        self.reload_speed = reload_speed
        self.magazine_size = magazine_size
        self.bullets_remaining_in_mag = magazine_size

        self.total_ammo_stock = total_ammo_stock
     
        # shooting vars
        self.wielded_by = None
        self.is_shooting = False
        self.is_reloading = False
        self.select_fire = select_fire
        self.is_dual_wield = is_dual_wield

        self.shot_spread_pattern = shot_spread_pattern
        self.shot_spread_number = shot_spread_number

        # these are endpoints and start points for the bullets
        self.shooting_start_position = (0,0)
        self.projectile_target_position = (0,0)

        # these are only endpoints for the bullets and are mostly used when the projectile queue delay is 0
        self.final_endpoints = []
        self.spread_final_endpoints = []

        # before being added to the active pool, the bullet object first needs to get through this queue
        self.projectile_queue = []

        # trigger reset speeed contorls tbns
        self.triggerResetSpeed = triggerResetSpeed

        # timers
        self.shooting_timer = Timer(timer_replay=True)
        self.reloading_timer = Timer()

        # raycast vars
        self.casted_rays = casted_rays
        self.raycast_depth = raycast_depth
        self.raycast_width = raycast_width
        self.raycast_angle_offset = raycast_angle_offset

        # whether it appear in weapon box or not
        self.inWeaponBox = inWeaponBox

        # store attributes for different projectiles
        self.projectile_attributes = {}

    def init(self):

        # update bullets remainig in mag
        self.bullets_remaining_in_mag = self.magazine_size

        # set speed for reload timer
        self.reloading_timer.timer_speed = self.reload_speed
        self.shooting_timer.timer_speed = self.fire_rate
    
    # reloading
    def reloading_ammo(self):

        # run timer
        self.reloading_timer.run_timer()

        # if the reload has finished then set reloading to false and add all the entities back to the inactive pool
        if self.reloading_timer.timer_complete:

            # set reloading to be false
            self.is_reloading = False

            # since it has reloaded update what the max ammo count currently is
            self.managing_ammo_count()


    # manage ammo count
    def managing_ammo_count(self):

        # if the weapon is not dual wield or its dual wield and not alternating clicks then run this ammo count management
        if not self.is_dual_wield or self.is_dual_wield :

            # subtract the number of bullets remaining from the magazine, to see how many bullets were shot before reload
            number_of_bullets_shot = self.magazine_size - self.bullets_remaining_in_mag

            # hadnle if the max ammo capacity is just 0
            if self.total_ammo_stock == 0:
                self.bullets_remaining_in_mag = self.bullets_remaining_in_mag

            # in this case we cannot add how much the magazine needs back to it, so we add whatever is remaining in the ammo capacity
            elif (self.total_ammo_stock - number_of_bullets_shot) < 0:

                # so for the bullets remaining it will add the remainder in the ammo capacity
                self.bullets_remaining_in_mag += self.total_ammo_stock

                # and for the max ammo capacity we just deduct itself
                self.total_ammo_stock -= self.total_ammo_stock

                # then set it so it can never go below 0 technically
                self.total_ammo_stock = max(0,self.total_ammo_stock)

            # if we have a max ammo capacity of 30 or more, when we reload, we can just give the bullets in the mag its full capacity which is the magazine size
            elif (self.total_ammo_stock - number_of_bullets_shot) >= 0:

                # self.bullets_remaining_in_mag = self.magazine_size
                self.bullets_remaining_in_mag += number_of_bullets_shot

                ### now we can update the actual value in the ammo capacity
                # now this should be subtracted from the max ammo capacity
                self.total_ammo_stock -= number_of_bullets_shot

                # now ensure the max ammo capacity never goes below 0
                self.total_ammo_stock = max(0,self.total_ammo_stock)

    

    # can shot be fired for normal gun shooting
    def can_shot_be_fired(self) -> bool:

        # calculate bullet start pos
        # self.find_bullet_start_point(start=self.hurtbox.center,target=self.wielded_by.shooting_target,
        #                              depth_end=self.hurtbox.topleft)

        # determines where the bullets originate from
        # self.adjust_dual_wield_position(player=player,win=win)

        # if the gun is full auto
        if self.select_fire in ['semiauto','fullauto','pumpaction']:

            # prevent shooting if the time between shots hasnt been reached yet
            # if not self.shooting_timer.timer_complete:
            #     pass

            # start deducting from the time between shots
            # if the player is shooting and there are entities in the inactive pool and self.inactive_pool and (self.total_ammo_stock != 0 and self.bullets_remaining_in_mag != 0)
            # if self.is_shooting:

            # then actually take the shot before the time is subtracted and not self.is_reloading
            # and also if the player is not reloading,
            # only check for avaible entities if there are actual bullets in the mag
            if (self.shooting_timer.timer_complete) and (self.bullets_remaining_in_mag > 0):

                # self.init_projectiles()

                # variable which gives possible end points for bullets and the ray number it is on as well 
                raynumber_endpoint = find_raycast(number_of_casted_rays=self.casted_rays, raycast_depth=self.raycast_depth,
                                                        raycast_width=self.raycast_width,starting_point=self.wielded_by.hurtbox.center,target_point=self.wielded_by.shooting_target_position,
                                                        raycast_angle_offset=self.raycast_angle_offset)

                # this stores the middle line/end point
                self.final_endpoints = [raynumber_endpoint[ind] for ind in find_median_values(array_of_values=raynumber_endpoint.keys(),number_to_return=1)] # return as many end points as there are bullets to be shot, so the number of spread per shot plus 1 for the main bullet, or better yet the numebr of fov rays
                
                # if there are spread shots
                if self.shot_spread_number > 0:

                    # if spread pattern is perfect
                    if self.shot_spread_pattern == 'perfect':

                        # if spread pattern perfect, the final endpoints variable has endpoints that are arranged starting from the middle line
                        # so all we need to do is get a list of endpoints the size of the number of spread bullets and without the first element in the final endpoints list
                        # self.spread_final_endpoints = self.final_endpoints[1:self.number_of_spread_bullets_per_shot+1]
                        self.spread_final_endpoints = [raynumber_endpoint[ind] for ind in find_median_values(array_of_values=raynumber_endpoint.keys(),number_to_return=self.shot_spread_number+1)] # gave it plus 1 because the middle line is returned but it will be removed in the next line of code

                        # if middle line in final endpoints then remove it
                        if self.final_endpoints[0] in self.spread_final_endpoints:
                            self.spread_final_endpoints.remove(self.final_endpoints[0])

                    # elif the pattern si random
                    elif self.shot_spread_pattern == 'random':

                        # then we take a random sample from the possible rays provided, again here we dont care about
                        # in the returned rays, do not include the middle line
                        self.spread_final_endpoints = random.sample([raynumber_endpoint[ind] for ind in find_median_values(array_of_values=raynumber_endpoint.keys(),number_to_return=self.casted_rays) if raynumber_endpoint[ind] != self.final_endpoints[0]],self.shot_spread_number)

                        # if middle line in final endpoints then remove it
                        if self.final_endpoints[0] in self.spread_final_endpoints: # code might be buggy in that we dont need to get rid of the line but change it to smth else so the right amount of bullets still come out
                            self.spread_final_endpoints.remove(self.final_endpoints[0])



                # do a quick check if there the whole magazine size has been fired, if it has then force a reload
                if self.bullets_remaining_in_mag == 0: # here bullets being 0 means that all has been fired

                    # check we have reserve bullets to actually do reloading
                    if self.total_ammo_stock > 0:

                        # if we do have ammo then reload
                        # self.is_reloading = True

                        return

            # # then actually take the shot before the time is subtracted and not self.is_reloading
            # # and also if the player is not reloading,
            # # only check for avaible entities if there are actual bullets in the mag
            # if (self.shooting_timer.timer_complete) and not self.is_reloading and (self.bullets_remaining_in_mag > 0):

                self.init_projectiles()

            # run timer
            # run timer
            self.shooting_timer.run_timer()

    # This function already does all the list management for the bullet so i dont think we need to do that again in the actual meat of everything
    def init_projectiles(self): 

        ## NORMAL CLICK SHOTS
        for bullet_object in self.projectile_attributes:
       
            # loop through where each bullet is being sent to out of all the available end points
            for i in range(len(self.final_endpoints)):

                # set a bullet to be the first thing in the inacitve pool
                bullet = objectManager.inactive_pool[bullet_object][i]

                # third conditional means we only ever try to run this code if there is atually a bullet in the inactive pool to use
                if not bullet.is_active and not bullet.fired and objectManager.inactive_pool[bullet_object]: # second condiitonal prevents bullet being fired twice until reload. this is important because after bullets collided they are sent back to the inactive pool, but we dont want inactive bullets that have already been fired

                    # set projectile manager
                    bullet.projectile_manager = self

                    set_attributes(game_object=bullet,attributes=self.projectile_attributes[bullet_object])

                    # init the projectile
                    bullet.init(self.projectile_attributes[bullet_object])

                    store_original_vars(game_object=bullet)

                    # active to false because when we init active is set to true by default
                    bullet.is_active = False

                    bullet.pathing = 'regular'

                    # setting start and target pos
                    bullet.start_position = self.shooting_start_position
                    bullet.hurtbox.center = self.shooting_start_position
                    bullet.target_position = self.final_endpoints[i]

                    bullet.length_to_target = (Vector2(bullet.target_position) - Vector2(bullet.hurtbox.center)).length()

                    # set bullet direction/current angle
                    direction_vectorX, direction_vectorY = Vector2(bullet.target_position) - Vector2(bullet.start_position)

                    # update movement vector
                    bullet.update_movement_vectors(unique_id='movement',direction_vectorX=direction_vectorX,direction_vectorY=direction_vectorY,
                                                                acceleration=bullet.acceleration,Xcceleration_rate=0,max_value=bullet.acceleration)
                    
                    # find current angle
                    current_angle = math.atan2(direction_vectorY,direction_vectorX) # add offset of 45 degrees

                    bullet.direction = math.floor((math.degrees(current_angle)+90)% 360)

                    # set time bullet will wait until in projectile queue before it is sent to active pool
                    bullet.time_until_active = 0 # always 0 so it gets shot immediately

                    # start time until active timer
                    bullet.time_until_active_timer.timer_limit = bullet.time_until_active
                    bullet.time_until_active_timer.timer_init()
                    
                    # add bullet to projectile queue before it is added to active pool
                    self.projectile_queue.append(bullet)
                    
                    # remove bullet obj from inactive pool
                    objectManager.inactive_pool[bullet_object].remove(bullet)

                    # remove one from the display ammo because a bullet has been shot
                    self.bullets_remaining_in_mag -= 1
                
                    # add one to the alternate shot tracker but if its the length of the range then reset it to 0
                    self.alternating_shot_tracker += 1

    def run_behaviour(self):


        # self.hurtbox.center = self.wielded_by.rect.center

        # the direction will be the angle from player center to cross hair
        # set bullet x and y vel
        # dirX,dirY = Vector2(self.wielded_by.crosshair.rect.center) - Vector2(self.wielded_by.rect.center)


        # # find current angle

        # current_angle = float(math.atan2(dirY,dirX))  # add offset of 45 degrees

        # self.direction = f'{math.floor(math.degrees(current_angle)% 360)}'

        # reload check, putting reload here means we can only reload if there are entities in the active pool
        self.reloading_ammo()

        # check if bullets can be fired
        self.can_shot_be_fired()

        # if there is a projectile in the queue
        if self.projectile_queue:

            to_remove = []

            # go through each bullet in the projectile queue
            for bullet in self.projectile_queue:


                # if bullet.adjust_final_target:

                #     bullet.target_position = self.wielded_by.shooting_target

                if bullet.ready_to_be_shot():

                    to_remove.append(bullet)

            # remove bullets ready to be shot
            if to_remove:

                for blt in to_remove:

                    # remove from queue and add to acitve pool
                    objectManager.active_pool.append(blt)
                    self.projectile_queue.remove(blt)

            # if empty start burst countdown to prevent shooting
            if not self.projectile_queue:
                self.burst_countdown_active = True

    def shoot(self):

        # if there is a projectile in the queue
        if self.projectile_queue:

            to_remove = []

            # go through each bullet in the projectile queue
            for bullet in self.projectile_queue:


                # if bullet.adjust_final_target:

                #     bullet.target_position = self.wielded_by.shooting_target

                if bullet.ready_to_be_shot():

                    to_remove.append(bullet)

            # remove bullets ready to be shot
            if to_remove:

                for blt in to_remove:

                    # remove from queue and add to acitve pool
                    objectManager.active_pool.append(blt)
                    self.projectile_queue.remove(blt)

            # if empty start burst countdown to prevent shooting
            if not self.projectile_queue:
                self.burst_countdown_active = True

        pass


class Bullet(Moveable_Object):

    def __init__(self,pathing:str=None,motion_stop:float=-1,homing:bool=False,stop_at_target_position:bool=False,travelTimeTimeLimit:float=0):
        
        # time until bullet become active and is removed from projectile queue
        self.time_until_active_timer = Timer(timer_limit=0)

        # timer for 
        self.travelTimeTimer = Timer()

        # trvael time time limit
        self.travelTimeTimeLimit = travelTimeTimeLimit

        # pathing var
        self.pathing = pathing
        
        # vars that change the way the bullet behaves after being shot
        self.motion_stop = motion_stop
        self.homing = homing
        self.stop_at_target_position = stop_at_target_position

        # if a bullet has already been fired
        self.fired = False

        # projectile manager which helps init the bullet
        self.projectile_manager = None

        super().__init__(self)


    def init(self):

        self.travelTimeTimer.timer_limit = self.travelTimeTimeLimit
        self.travelTimeTimer.timer_init()

        super().init()


    # function that controls when a bulelt is fromed, and the countdown before it becomes active
    def ready_to_be_shot(self) -> bool:

        # taget corrs = whererver player is pointing, start coors is wherever the player/wapeon styat point is 
        # if bullet is not acitve run this code
        if not self.is_active:

            # run timer
            self.time_until_active_timer.run_timer()

            # if time until active has been reached
            if self.time_until_active_timer.timer_complete:

                # activate bullet
                self.is_active = True
                self.fired = True

                # update parameters for where it starts from
                # self.start_position = self.projectile_manager.shooting_start_position
                # self.hurtbox.center = self.start_position

                # adjust target pos
                # self.target_position = self.projectile_manager.wielded_by.shooting_target_position

                # # change direction vectors to the target position
                # self.movement_vectors['movement']["direction_vectorX"],self.movement_vectors['movement']["direction_vectorY"] = Vector2(self.target_position) - Vector2(self.start_position)

                # # bullet will stop at the target point
                # if self.stop_at_target_position:
                #     self.movement_vectors['movement']['target_point'] = self.target_position

                return True

            return False
        
    # funtion to determine how long the bullet has been travelling for, after its travelled for a set time it should be set to inactive
    def travel_time(self):

        # run timer
        self.travelTimeTimer.run_timer()

        # if life span is set to 0 then make the bullet never get deactivated over time
        if self.travelTimeTimer.timer_limit == -1:
            return

        # if its been travelling for a given time
        elif self.travelTimeTimer.timer_complete:

            # if the timer is over then just explode it
            # self.explode()
            # if self.has_exploded:
            #     return

            # make bullet inactive,reset timer
            self.is_active = False



    # handle collision damage etc
    def handle_collision(self,game_object:object,axis:str):

        if not self.is_active or not game_object.is_active:
            return

        # set damage variable by checking if there was a crit
        damage = 0
        crit = proc(self.critical_chance)

        if crit:
            damage = self.damage*self.critical_multiplier

        elif not crit:
            damage = self.damage

        # FOR PLAYER BULLETS
        if self.object_of_origin == 'Player':

            # ENEMY OBJECT OF ORIGIN COLLISIONS
            # if projectile is colliding with smth from the enemy or self.object_of_origin == "None"
            if game_object.object_of_origin == 'Enemy' :


                # if it is the boss itself that has been collided with
                if game_object.__class__.__name__ == "Enemy":

                    self.apply_damage(gameobj=game_object,damage=damage)
                    

            # if game_object.object_of_origin == 'Game':

            #     if game_object.__class__.__name__ == 'Wall':

            #         if axis == 'x':
            #             if self.movement[0] < 0:
            #                 self.hurtbox.left = game_object.hurtbox.right

            #             elif self.movement[0] > 0:
            #                 self.hurtbox.right = game_object.hurtbox.left

            #         elif axis == 'y':
            #             if self.movement[1] < 0:
            #                 self.hurtbox.top = game_object.hurtbox.bottom

            #             if self.movement[1] > 0:
            #                 self.hurtbox.bottom = game_object.hurtbox.top

            if game_object.object_of_origin == 'Player':
                return
            
        # if not piercing
        self.is_active = False

    # apply damage function, handles death too
    def apply_damage(self,gameobj:Moveable_Object,damage:float):

        gameobj.health -= damage
        gameobj.health = max(0,gameobj.health)

        if gameobj.health <= 0:
            self.projectile_manager.wielded_by.money += self.moneyOnKill
            gameobj.is_active = False
            
            # store the enemies that were killed this frame
            self.projectile_manager.wielded_by.killedThisFrame.append(gameobj)

        elif gameobj.health > 0:
            self.projectile_manager.wielded_by.money += self.moneyOnHit


        # # init damage number
        # if pynaccle.display_dmg_num == 1:
        #     dmgnum = pynaccle.inactive_pool['DamageNumber'][0]
        #     dmgnum.init(f"{damage}")
        #     dmgnum.spawn(gameobj.hurtbox.center)
        #     dmgnum.update_movement_vectors(unique_id='movement',direction_vectorX=0,
        #                                     direction_vectorY=-1,acceleration=self.acceleration,Xcceleration_rate=0,
        #                                     Xcceleration_rate_change='negative',
        #                                     max_value=self.acceleration,reduce_on_wall_collision=False,reset_on_max_value=False)
        #     pynaccle.inactive_pool['DamageNumber'].remove(dmgnum)
        #     pynaccle.active_pool.append(dmgnum)



    # combines movement and collision function
    def update(self):

        # only show the orbital and draw it if it is active
        if self.is_active:

            # update position
            self.update_position()

            # draw surface
            # self.draw_surface(position=self.hurtbox.center)
            self.submit_to_render()

            # self.draw_rect(position=self.hurtbox.center)

            # self.draw_hitbox()

            # update movement vars
            self.update_movement()

            # movement
            self.move_and_collide()

            # handle how long bullet is allowed to travel for
            self.travel_time()

           

