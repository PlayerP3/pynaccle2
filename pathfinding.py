# A* we are trying to get to our end goal using the shortest path possible and theres a heuristic built in to allow that
# Euclidian distance is the exact length of space between two points. i.e the length from point A to point B
# always be checking your shortest route with what is at the top of the priority queue
# # the final graph contains the coordinates for a given node and its object

from .utils import *
from .timer import Timer
from .tilemap import tilemapProcessor
from .globs import *
from .objectsystem import objectManager
# from utils import *
# from Drawing_TileMaps import engine

# create variable for all tiles
all_tiles_astar = None

# comapring tuples
def cmpT(t1, t2):
    return sorted(t1) == sorted(t2)

# function that takes the top left coordinates for the rect we created in the tilemap and returns the centered coordinates
# which is just adding 25 to x and y
# def centre_coors(top_left_coors):

#     new_coors = (top_left_coors[0]+25,top_left_coors[1]+25)

#     return new_coors


# function to build astar graph
def build_astar_graph():

    for tile in tilemapProcessor.accessible_tiles:

        tilemapProcessor.astar_graph[tile] = Node()

# function to build true clearance graph
def build_true_clearance_graph():

    for tile in tilemapProcessor.astar_graph:

        clearance = 1

        # create rect tuple
        rect = [*tile,32,32]

        # get tiles within the current tile we are expanding 
        subtiles = breakdown_rect(tile,rect_width=rect[3],rect_height=rect[2],tile_size=32)

        # subtract walls list from subtiles
        subtiles_without_walls = list(set(subtiles) - set(tilemapProcessor.inaccessible_tiles))

        while len(subtiles_without_walls) == len(subtiles):

            # expand rect
            rect = [rect[0],rect[1],rect[2]+32,rect[3]+32]

            # center expansion at tile pos
            centered_rect = reposition_rect(rect=rect,point=tile)

            # get tiles within the current tile we are expanding 
            subtiles = breakdown_centered_rect(point=(centered_rect[0],centered_rect[1]),rect_width=centered_rect[3],rect_height=centered_rect[2],tile_size=32)

            # subtract walls list from subtiles
            subtiles_without_walls = list(set(subtiles) - set(tilemapProcessor.inaccessible_tiles))

            clearance += 1

        tilemapProcessor.astar_graph[tile].clearance = clearance



    # get tile/square, and set a i value  to  1
    # break it down using tile size, if there is no wall tile in it , expand right and down, if there is a wall tile in it, set i value to that
    # incrmeent i value by 1


class Node():

    def __init__(self,cost:int=0,heuristic:int=0,topleftcoors:tuple=(0,0),neighbours:list=[],clearance:int=1) -> None:

        # the cost from moving from the previous node to this current node. There can be multiple previous nodes to this node, but for this we will assume they all have the same cost
        self.cost = cost

        # the distance to the end goal
        self.heuristic = heuristic

        # the total. starts with the heuristic and the cost of moving from all other nodes to this current node
        # so dist to final node + (current accumulated cost from start node to the current one)
        self.total = heuristic + cost

        self.personal_cost = heuristic + cost

        # the actual cooridnates of the point. This is the top left position of the rect
        # self.coordinates = coors
        self.topleftcoors = topleftcoors

        # get the center coordinates that i want the final path to be
        self.center_coors = find_tile_centre(point=topleftcoors)

        # the neighbours of the node and the cost from this node to that node
        self.neighbours = neighbours

        # the node that it passed through. this is updated when the node is expanded to, not when it is itself expanded
        self.previous_node = None

        # store clearance value
        self.clearance = clearance

        # variable to take the total cost. this is updated when the node is expanded to, not when it is itself expanded
        # self.total_cost = 0

    # calculate the total score for the given node, given the path to that node and its heuristic.
    # so we add up the bare cost of moving to each of the nodes before the current node we are looking at
    def calculate_total(self,current_node_path:list,astar_graph:dict):

        # FORGOT THAT WHEN CALCULATING THE TOTAL YOUI NEED TO ADD THE COST OF THIS NODE AS WELL
        # there was a glitch in this function, where if this node is visited/exapnded onto multiple times, it keeps stacking the total because the actual attribute self.total is being updated
        # but the starting total should always be the same for a node because it is its heuristic plus the cost to that node. The extra cost is all the nodes added to reach there as well
        # so we have to make a new variable for total that doesnt change the actual attribute
        # Final comment: This is correct because the total here is the cost to this current node plus the heuristic
        # .This should only be used if we have already decide that this is the best node to move to because it has the shortest g cost from other nodes
        # total = self.total
        total = self.personal_cost

        # go through each node in the path leading to the node you want to check on
        for node in current_node_path:

            # find the cost of all the nodes in the path and add it to the heuristic of the current node to get the final total
            total += astar_graph[node].cost

        return total
    
    # returns a list of neighbourd for a node, it looks for the west, north, east and south only ,all_tiles:dict=pynaccle.accessible_tiles_for_astar
    def find_neighbours(self):

        # print(f'These are all the tiles {all_tiles}')
        # get x and y copors for current node
        x,y = self.topleftcoors

        x = int(x)
        y = int(y)

        east_neighbour = (x+tileSize,y)
        south_neighbour = (x,y+tileSize)
        north_neighbour = (x,y-tileSize)
        west_neighbour = (x-tileSize,y)

        # update what we save the tile as dpeending on if it is a tile that can be moved to
        if east_neighbour not in tilemapProcessor.accessible_tiles:

            east_neighbour = None

        if south_neighbour not in tilemapProcessor.accessible_tiles:

            south_neighbour = None

        if west_neighbour not in tilemapProcessor.accessible_tiles:

            west_neighbour = None

        if north_neighbour not in tilemapProcessor.accessible_tiles:

            north_neighbour = None

        # print(f'east neighbour = {east_neighbour}, west neighbour = {west_neighbour}, north neighbour = {north_neighbour}, south neighbour = {south_neighbour}')
        self.neighbours = [east_neighbour,west_neighbour,south_neighbour,north_neighbour]

    # init 
    def init(self,attributes:dict={}):

        for att,val in attributes.items():

            setattr(self,att,val)

        self.total = self.heuristic + self.cost
        self.find_neighbours()
        self.center_coors = find_tile_centre(point=self.topleftcoors)


    # the new way we are calculating the total we dont need to go through the whole path, we just need the distance from start node, which is the cost
    # and then we need the heuristic as well. so actually we dont need a function at all
    # so i am the one who defines the different g function costs, say maybe if i want diagonals to cost less than straight paths i would do that
    # or maybe if i dont want some tiles to be explored as opposed to other

# start point is (250,100)

# end point is (700,500)
# this is going to be a class that manages A star and has the graph, the paths everything
class Pathfinding():

    def __init__(self,pathing_type:str='regular') -> None:

        self.pathing = []
        self.pathing_type = pathing_type
        self.update_path_timer = Timer(timer_replay=True,timer_limit=0.5)
        self.update_path = True

        # store the end and start point in variables
        self.pathing_start_position = (0,0)
        self.pathing_end_position_tile = (0,0) # this is topleft coordinate of tile the target is on
        self.pathing_end_position_target = (0,0) # this is the actual coordinate of the target

        # create variable for the deciding stack and the final stack
        self.deciding_stack = []

        # final stack needs to have the start point because that is where we begin and choose to move to next
        self.final_stack = [self.pathing_start_position]

        # create variable for the current node. It starts with the start point and then moves from there
        self.current_node = self.pathing_start_position
        
        # variable for allowing the end point to be switched,
        self.target_position_change = False

        # varibale to control if we run a star algorithm or not
        self.path_finding = True

        # list for already expanded nodes
        self.already_expanded = []   

    # this is a function for creating the graph, no matter the coordinates in the graph, this will assume it is a square, given the start and end nodes
    # it just doesnt include the nodes that dont actually exist. So its okay.
    # start and end should both be top left coordinates of a tile
    def a_star(self,start:tuple,end:tuple):

        # if end or start not in all tiles just retur an empty list for pathing
        if start not in tilemapProcessor.accessible_tiles or end not in tilemapProcessor.accessible_tiles:
            return []
        
        # if the object does not have enough clearance to reach the end point
        if self.clearance > tilemapProcessor.astar_graph[end].clearance:
            
            new_end = None

            # find the closest node to the end node that has enough clearance
            closest_nodes = sorted(tilemapProcessor.astar_graph.keys(),key= lambda x:(Vector2(x)-Vector2(end)).length()) 

            # go thruogh nodes based on their distance to object
            for node in closest_nodes:

                # check if clearance is equal to or greater than object clearance
                if self.clearance <= tilemapProcessor.astar_graph[node].clearance:

                    new_end = node

                    break

            # no end point can be found
            if not new_end:
                return []
            
            elif new_end:
                end = new_end
                self.pathing_end_position_tile = end

        # get astar graph
        # astar_graph = pynaccle.astar_graph.copy()

        # nodes which we have calculated the f cost for, these are all the neighboiuring nodes for the current node
        # i.e when we are thinking of what should be expanded next, it is the node with the smallest total cost in this list
        # in summary open stack is list of possible of nodes that could have been moved to
        open_stack = []

        # nodes which have been expanded, so this is the current node at any given moment
        # but closed stack is a list of nodes that have already been moved to and been the cheapest at some point in time
        # so when we remove a node from the open stack to the closed stack we are basially saying it isnt one of the possible cheapest anymore, it is the cheapest next step
        # then when we find its neighbours, we add all those to the open stack because they all have a chance of being the next cheapest
        closed_stack = []

        # add start node, which is now the current node, to the open list
        open_stack.append(start)

        # add the start point to the astar graph and make its neighbours as well
        current_node = start

        # create first instance of astra graph

        # update node values in astar graph
        tilemapProcessor.astar_graph[current_node].init({'topleftcoors':current_node,
                                               'cost':calculate_manhattan(current_node,start),
                                               'heuristic':calculate_manhattan(current_node,end)}) 

        # adjust values 
        # alreayd processed nmodesd
        # created_node_objects = []

        path_finding = True

        # start pathfinding loop
        while path_finding:

            # set the current node to whatever has the lowest f cost / total cost in the open list
            # first sort the open stack based on what has the lowest f cost function. THe one with the lowest f cost function becomes closed and is added to the closed stack

            open_stack = sorted(open_stack, key=lambda x: tilemapProcessor.astar_graph[x].total)

            # print(f'Open stack is {open_stack}')
            # print(f'Start point is {open_stack}, closed stack is {closed_stack}')
            # current node is node with smallest total in open stack

            current_node = open_stack[0]

            # remove current node from open stack and add to closed
            open_stack.remove(current_node)
            closed_stack.append(current_node)

            # end loop and return path if final node is found
            if current_node == end:

               # put the end point in the final path because we have reached it
                final_path = [end]

                # now we are using a loop which is basically tracing the path back from the end node to the start node
                node_tracker = end

                # so before we were getting glitches because we were simply writing the clsoed stack as the final path,m but that is not true. It just reperesents everythign that was
                # expanded, not necessatrily the final path, to get the final path you start going back from the end node
                while start not in final_path:

                    # add the previous node (the node that was expanded to reach the current node) to the final path
                    final_path.append(tilemapProcessor.astar_graph[node_tracker].previous_node)

                    # now set the current node in the tracing back to be that previous node
                    node_tracker = tilemapProcessor.astar_graph[node_tracker].previous_node

                    # print(node_tracker)

                # there is this weird thing i experienced before where a list like what i am returning has the same id or whaetevr, so even though i
                # send the list to two different variables they are still connected so what i do to one affects the other
                # so we need to have two separate variables for the final path list

                # print('compelte path =',[astar_graph[p].center_coors for p in final_path[::-1]])
          
                # because the final path list starts from the end node and works its way back the path that the entity has to follow is actually starting from the end point
                # to prevent that we reverse the final path order so it starts form the start node. return twice because two variables need this information
                return [tilemapProcessor.astar_graph[p].center_coors for p in final_path[::-1]]
            
            # set neighboiurs for current node,
            # print(f'List comprehenstion neighbours = {astar_graph[current_node].neighbours}')
            neighbour_nodes = [node for node in tilemapProcessor.astar_graph[current_node].neighbours if node]

            # print(pynaccle.astar_graph[current_node].neighbours)

            # print(current_node)
            # print(astar_graph[current_node].neighbours)
            # print(pathing_end_position_tile)
            # print('ff')
          
            # print(f'Neighbouring nodes = {neighbour_nodes}')
            # loop through neighbouring ndoes
            for neighbour in neighbour_nodes:

                # was having a glitch where a node object was being created twice so its previous node was being overwritten, so now we only create one if it hasnt been already created
                # if node not in created_node_objects:

                #     astar_graph[node] = Node(cost=calculate_manhattan(node,find_tile_centre(point=start_position)),heuristic=calculate_manhattan(node,find_tile_centre(point=pathing_end_position_tile)),topleftcoors=node,neighbours=find_neighbours(current_node=node,all_tiles=pynaccle.accessible_tiles))
                #     created_node_objects.append(node)

                # if the node is in the closed stack meaning it has been selected as the cheapest in an expansion and been moved to already then ignore it because we dont move back in the graph
                if neighbour in closed_stack:
                    continue

                # update 
                tilemapProcessor.astar_graph[neighbour].init({'topleftcoors':neighbour,
                                               'cost':calculate_manhattan(neighbour,start),
                                               'heuristic':calculate_manhattan(neighbour,end)}) 

                # if the node is not in the open stack meaning they havent been put up as an option to move to yet or if the cost to this node is smaller than the cost for the current node then we can consider it as a possible option in the open stack
                if (neighbour not in open_stack or (tilemapProcessor.astar_graph[neighbour].total < tilemapProcessor.astar_graph[current_node].total)) and tilemapProcessor.astar_graph[neighbour].clearance > self.clearance:

                    # print(neighbour)
                    # print(pynaccle.astar_graph[neighbour].clearance)
                    # print(self.clearance)
                    # make the parent of the node be the current node right now
                    # astar_graph[current_node].previous_node = node
                    tilemapProcessor.astar_graph[neighbour].previous_node = current_node

                    # if the node isnt already in the open stack, meaning if it is not
                    open_stack.append(neighbour)

    

        return []
    
    def bigger_than_tile_size(self,node:Node):

        if self.hitbox.height > tileSize:
            pass
    
    def bigger_than_tile_size(self,node:Node):

        if self.hitbox.height > tileSize:

            x = int(node.topleftcoors[0])
            y = int(node.topleftcoors[1])

            south_neighbour = (x,y+tileSize)
            north_neighbour = (x,y-tileSize)

            # if wall
            if north_neighbour not in tilemapProcessor.accessible_tiles or south_neighbour not in tilemapProcessor.accessible_tiles:

                node.total += 100
        # if hitbox bigger than tile size 
        # if issue is height, nodes above and below wall have increased cost
        # if issue is width, ndoes to the left and right have increased cost
        # if issue is both width and height then nodes left right up down all have increased cost

        pass

    def update_movement_vectors2(self,start_position:tuple,target_position:tuple) -> None:

            # set bullet direction/current angle
            direction_vectorX, direction_vectorY = Vector2(target_position) - Vector2(start_position)

            # update movement vector
            self.update_movement_vectors(unique_id='movement',direction_vectorX=direction_vectorX,direction_vectorY=direction_vectorY,
                                                        acceleration=self.acceleration,Xcceleration_rate=0,max_value=self.acceleration,target_point=target_position)
            
    def determine_pathing_type(self):

        # if it is time to update path
        if self.find_new_pathing():

            # defualt pathing should be astar
            self.pathing_type = 'regular'

            # FUNCTION TO FIND IF THERE IS A WALL IN OUR FACE AND WE HAVE TO CHOOSE A NEW PATHIGN
            # self.detect_wall_collisions()
            self.check_obstacle_collision()

    def find_new_pathing(self):

        # run timer
        self.update_path_timer.run_timer()

        # if the timer until astar has reached the maximum
        if self.update_path_timer.timer_complete:

            # set it so astar can be checked
            self.update_path = True

            return True

        return False
    
    def check_obstacle_collision(self):

        # update raycast properties
        self.movement_raycast.init({'starting_position':self.hurtbox.center,'target_position':self.pathing_end_position_target,'raycast_depth':find_dist_between_points(self.hurtbox.center,self.pathing_end_position_target)})

        # get raycast and detect collision with game objects
        self.movement_raycast.detect_collision_with_raycast()
        
        # get closest collision
        closest_object = self.movement_raycast.get_closest_object()
        
        # if clsoest object is wall then lets go astar
        if closest_object.__class__.__name__ == 'Wall':
    
            self.pathing_type = 'astar'

                  


    def update_pathing_and_cache(self):
        
        # determine pathing type
        self.determine_pathing_type()

        # if it is not time to update the path
        if not self.update_path:

            # if theres only one element left in the pathing and its not the player center
            # if the pathing is decided to be regular but its not time to update pathing, just follow the player because it shoiuldnt be A*
            if ((len(self.pathing) == 1) and (self.pathing[-1] != self.target_position)) or (self.pathing_type == 'regular'):
                
                # set the end point to be the player rect as well
                self.target_position = self.pathing_end_position_target

                # only put the end point in the pathing
                self.pathing = [self.target_position]

                # update movement vectors
                self.update_movement_vectors2(start_position=self.hurtbox.center,target_position=self.pathing[0])

            elif self.pathing_type == 'astar':
                
                
                if not self.pathing:
                    self.pathing = [self.target_position]

                    # set target to be the next thing in the pathing
                    self.target_position = self.pathing[0]

                    
                # bug where update is false, so we come here, but self.pathing has the initial target position in it so it tis to run this code 
                # but before the in ital tagret position is None because we havent updated it yet
                elif self.pathing:

                    # update movement vectors
                    self.update_movement_vectors2(start_position=self.hurtbox.center,target_position=self.pathing[0])
            
                    ########################
                    # find length to target
                    self.length_to_target =  find_dist_between_points(self.pathing[0],self.hurtbox.center)

                    if self.length_to_target <= 1 :
                        
                        # if the entity is at the end point then dont remove the last point
                        if self.target_position == self.pathing_end_position_tile or self.pathing_end_position_tile == self.pathing[0]:
                            return

                        # remove the next point in the path if its not the end point
                        # if self.target != self.end_point or self.end_point != self.pathing[0]:
                        # print(self.pathing)
                        del self.pathing[0]


                        # if for some reason the code has bugged and deleted pathing we will make the path be the target
                        if not self.pathing:
                            self.pathing = [self.target_position]

                        # set target to be the next thing in the pathing
                        self.target_position = self.pathing[0]

                    ########################

  

        # if it is time to update
        elif self.update_path:

            # print(f'This is entity pathing type : {entity.pathing_type}')
            # if the pathing is just chasing down the enemy
            if self.pathing_type == 'regular':

                # set the end point to be the player rect as well
                self.target_position = self.pathing_end_position_target

                # only put the end point in the pathing
                self.pathing = [self.target_position]

               # update movement vectors
                self.update_movement_vectors2(start_position=self.hurtbox.center,target_position=self.target_position)

            ## check if pathing needs to be changed
            elif self.pathing_type == 'astar':
                
                # if the tile the player is on has changed
                if self.pathing_end_position_tile != find_tile_topleft(point=self.pathing_end_position_target):

                    # update path cache, new pathing is set in function
                    self.update_path_cache()


            # set update pathing to false
            self.update_path = False


    # function to see how we insert the self rect center into the pathing list
    def adjust_pathing_start_end_position(self):
        
        
        if len(self.pathing) > 1:

            # return
            # self.pathing.remove(self.pathing[0])

            # get first and second points, first point, second point
            f,s = self.pathing[0:2]

            # find distance to self rect center, dist from self to second point, dist from first point to second point
            self_to_s = find_dist_between_points(self.hurtbox.center,s)
            first_to_s = find_dist_between_points(s,f)
            
            if first_to_s < self_to_s:

                # self.pathing.insert(0,self.hurtbox.center)
                self.pathing = self.pathing[1:]
                # self.pathing[0] = self.hurtbox.center
                pass

            
        

            elif self_to_s < first_to_s:
                
                self.pathing = self.pathing[1:]
                # self.pathing[0] = self.hurtbox.center


            # get first and second points, last point, lasty but one point
            # lb1,l = self.pathing[-2:]

            # # find distance to self rect center, dist from end to second point, dist from last point to last but one point
            # end_to_l = find_dist_between_points(self.pathing_end_position_target,l)
            # end_to_lb1 = find_dist_between_points(self.pathing_end_position_target,lb1)
            
            # if end_to_l < end_to_lb1:

            #     self.pathing.append(self.pathing_end_position_target)

            # elif end_to_lb1 < end_to_l:
                
            #     self.pathing[-1] = self.pathing_end_position_target

        # funtion for finding a new path
   
    def update_path_cache(self):

        # change entitiy start point
        self.start_position = self.current_tile_position

        # change what the current entity end point is. This is centered
        self.pathing_end_position_tile = find_tile_topleft(self.pathing_end_position_target)

        # create key for path cache
        key_for_cache = (self.start_position[0],self.start_position[1],self.pathing_end_position_tile[0],self.pathing_end_position_tile[1])

        # go through each path in the cache and check if the start and end point is equal to the current start and end point
        # for path in path_cache:
        if key_for_cache in objectManager.path_cache:

            # get path from the cache
            path = objectManager.path_cache[key_for_cache]

            # we only care if at least the start point is in the path and the end point must be at the end
            # this means if youre on a tile that belongs to a cached path, you dont need to run astar again
            # or also if the start point and end point are in one of the path caches or ((self.start_position in path) and (self.target_position in path))
            # if ((self.start_position in path) and (self.target_position == path[-1])):
            if (self.start_position in path) and (self.pathing_end_position_tile in path):

                # find the index for the start point
                start_position_index = path.index(self.start_position)

                # find index for end point
                pathing_end_position_tile_index = path.index(self.pathing_end_position_tile)

                # now do diferent things depending on what
                # if the start point is in the path, then the pathing should begin from that point onwards, rather than the start of the full path
                self.pathing = path.copy()[start_position_index:pathing_end_position_tile_index]

                # if the path is empty then set player position as target in pathing
                if not self.pathing:
                    self.pathing = [self.pathing_end_position_target]

                # we want to properly set the start position depending on how close the first point or the object center is to the next point
                self.adjust_pathing_start_end_position()

                self.target_position = self.pathing[0]

                # end the function because theres no new path that needs to be made
                return None,None

        # get pathing
        self.pathing = self.a_star(start=self.start_position,end=self.pathing_end_position_tile)

        # if no pathing then return nothing
        if not self.pathing:
            return None,None
        
        # make copy of path which is what we will return
        path_to_return = self.pathing.copy()

        # based on the start and end point of the cache create a key for the path to return dictionary
        path_start = path_to_return[0]
        path_end = path_to_return[-1]

        # create key for dictionary
        key_to_return = (path_start[0],path_start[1],path_end[0],path_end[1])

        # after a star is done change what the start and end coors are
        self.adjust_pathing_start_end_position()  # ok so this is actually important because we dont need the current tile start position, what we need is where the entity actually is

        # change the ending in the path to be the player position, this is important because we want the entitiy to chase the player when close enough rather than the tile they are on
        # self.pathing[-1] = self.pathing_end_position_target

        # reset what the target is for the actual movememt function which follows the path
        self.target_position = self.pathing[0]

        # update movement vectors
        self.update_movement_vectors2(start_position=self.hurtbox.center,target_position=self.target_position)

        # set new key and path
        new_key = key_to_return
        new_path = path_to_return

        # if a new path was found in the function
        if new_path:

            # check whether that new key is already a key
            if new_key not in objectManager.path_cache:

                # copy the path
                copy_path = new_path.copy()

                # add path to path cache
                # self.path_cache.append(copy_path)
                objectManager.path_cache[new_key] = copy_path

    


    def draw_pathing(self):
        return

        if len(self.pathing) >= 2:

            draw_lines(points=self.pathing)













