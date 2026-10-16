b = {
}


b[0] = 1

b[12] = 32

b[4] = 22

print(b)

print((1.23//1)%7)

from array import array

x = array('f',[1,2,3])

print(x)

import numpy as np

b = np.matrix([[1,3],[2,5]])

print(b)

from pyglm import glm


from enum import Enum,auto

tasks:Enum = Enum('Tasks',names=["fillSouls","goToPoint"])

print(tasks)
print(tasks.fillSouls)

def nn(k):

    return k == tasks.fillSouls

print(nn(tasks.fillSouls))
print(tasks(1))


x = tasks.fillSouls.value

print('dd',x)

class Task(Enum):

    Fill = 'fill'
    Location = 'location'

    @property
    def permissions(self):
        if self == Task.Fill:
            return ["create", "edit", "delete"]
        elif self == Task.Location:
            return ["edit"]
        return []


print(Task.Fill.value)


class Circle:
    def __init__(self, radius):
        
        self.radius = radius
        

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = float(value)

    @property
    def diameter(self):
        return self.radius * 2

    @diameter.setter
    def diameter(self, value):
        self.radius = value / 2

cc = Circle(20)

print(cc._radius)


class UserRole(Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

    @property
    def permissions(self):
        if self is UserRole.ADMIN:
            return ["create", "edit", "delete"]
        elif self is UserRole.EDITOR:
            return ["edit"]
        return []


Boss = UserRole('admin')

print(Boss.permissions)
print(Boss.name)

print(UserRole('admin'))


class Task(Enum):


    def __init__(self,named,mm):

        self.named = named
        self.mm = mm



class FillSoul(Task):

    SOULCAP = ('cap','ll')

    

    @property
    def is_complete(self):

        if self is FillSoul.SOULCAP:
            return 'hej hej'
  

print(FillSoul.SOULCAP.is_complete)



class Tasks(Enum):
    
    PLACEHOLDER = 'placeholder'
    FILLSOULBOX = 'fillSoulBox'
    PICKUPWEAPON = 'pickUpWeapon'
    PLACEWEAPON = 'placeWeapon'
    GOTOLOCATION = 'goToLocation'
    INTERACTWITHITEM = 'interactWithItem'
    

x = Tasks('placeholder')



def breakdown_rect(point:tuple=(0,0),rect_width:int=32,rect_height:int=32,tile_size:int=32) -> list:

    tiles = []

    for x in range(rect_width//tile_size):
        for y in range(rect_height//tile_size):

            tiles.append((point[0]+(x*tile_size),point[1]+(y*tile_size)))
             

    return tiles

def calculate_manhattan(point_A_coors, point_B_coors):

    x_val = abs(point_A_coors[0]-point_B_coors[0])
    y_val = abs(point_A_coors[1]-point_B_coors[1])

    return x_val + y_val


accessible_tiles = list(set(breakdown_rect(rect_width=960,rect_height=960)) - set([(576, 800), (576, 832), (576, 864), (576, 896), (576, 928), (608, 0), (608, 32), (608, 64), (608, 96), (608, 128), (608, 160), (608, 192), (608, 224)]))
inaccessible_tiles = [(576, 800), (576, 832), (576, 864), (576, 896), (576, 928), (608, 0), (608, 32), (608, 64), (608, 96), (608, 128), (608, 160), (608, 192), (608, 224)]
astar_graph = {}

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

        east_neighbour = (x+32,y)
        south_neighbour = (x,y+32)
        north_neighbour = (x,y-32)
        west_neighbour = (x-32,y)

        # update what we save the tile as dpeending on if it is a tile that can be moved to
        if east_neighbour not in accessible_tiles:

            east_neighbour = None

        if south_neighbour not in accessible_tiles:

            south_neighbour = None

        if west_neighbour not in accessible_tiles:

            west_neighbour = None

        if north_neighbour not in accessible_tiles:

            north_neighbour = None

        # print(f'east neighbour = {east_neighbour}, west neighbour = {west_neighbour}, north neighbour = {north_neighbour}, south neighbour = {south_neighbour}')
        self.neighbours = [east_neighbour,west_neighbour,south_neighbour,north_neighbour]

    # init 
    def init(self,attributes:dict={}):

        for att,val in attributes.items():

            setattr(self,att,val)

        self.total = self.heuristic + self.cost
        self.find_neighbours()


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

        # store the end and start point in variables
        self.pathing_self_tile_pos = (0,0)
        self.pathing_gameObj_tile_pos = (0,0) # this is topleft coordinate of tile the target is on
        self.pathing_gameObj_hurtbox_pos = (0,0) # this is the actual coordinate of the target

        # create variable for the deciding stack and the final stack
        self.deciding_stack = []

        # final stack needs to have the start point because that is where we begin and choose to move to next
        self.final_stack = [self.pathing_self_tile_pos]

        # create variable for the current node. It starts with the start point and then moves from there
        self.current_node = self.pathing_self_tile_pos
        
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
        if start not in accessible_tiles or end not in accessible_tiles:
            return []

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
        astar_graph[current_node].init({'topleftcoors':current_node,
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

            open_stack = sorted(open_stack, key=lambda x: astar_graph[x].total)

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
                    final_path.append(astar_graph[node_tracker].previous_node)

                    # now set the current node in the tracking back to be that previous node
                    node_tracker = astar_graph[node_tracker].previous_node

                    # print(node_tracker)

                # there is this weird thing i experienced before where a list like what i am returning has the same id or whaetevr, so even though i
                # send the list to two different variables they are still connected so what i do to one affects the other
                # so we need to have two separate variables for the final path list

                # print('compelte path =',[astar_graph[p].center_coors for p in final_path[::-1]])
          
                # because the final path list starts from the end node and works its way back the path that the entity has to follow is actually starting from the end point
                # to prevent that we reverse the final path order so it starts form the start node. return twice because two variables need this information
                return [astar_graph[p].topleftcoors for p in final_path[::-1]]
            
            # set neighboiurs for current node,
            # print(f'List comprehenstion neighbours = {astar_graph[current_node].neighbours}')
            neighbour_nodes = [node for node in astar_graph[current_node].neighbours if node]


            # print(pynaccle.astar_graph[current_node].neighbours)

            # print(current_node)
            # print(astar_graph[current_node].neighbours)
            # print(pathing_gameObj_tile_pos)
            # print('ff')
          
            # print(f'Neighbouring nodes = {neighbour_nodes}')
            # loop through neighbouring ndoes
            for neighbour in neighbour_nodes:

                # if the node is in the closed stack meaning it has been selected as the cheapest in an expansion and been moved to already then ignore it because we dont move back in the graph
                if neighbour in closed_stack:
                    continue

                # init the neighbour of the current node
                astar_graph[neighbour].init({'topleftcoors':neighbour,
                                               'cost':calculate_manhattan(neighbour,start),
                                               'heuristic':calculate_manhattan(neighbour,end)}) 

                # if the node is not in the open stack meaning they havent been put up as an option to move to yet or if the cost (distance) to this node is smaller than the cost (distance) for the current node then we can consider it as a possible option in the open stack
                if (neighbour not in open_stack or (astar_graph[neighbour].total < astar_graph[current_node].total)):

                    # make the parent of the node be the current node right now
                    # astar_graph[current_node].previous_node = node
                    astar_graph[neighbour].previous_node = current_node

                    # if the node isnt already in the open stack, meaning if it is not
                    open_stack.append(neighbour)

    

        return []
    
for tile in accessible_tiles:

    astar_graph[tile] = Node()
        

t = Pathfinding()

v = t.a_star((0,32),(0,256))
z = t.a_star((32,32),(32,256))
x = t.a_star((64,32),(64,256))
y = t.a_star((96,32),(96,256))
ll = t.a_star((0,32),(224,256))

print(v)
print(z)
print(x)
print(y)
print(ll)