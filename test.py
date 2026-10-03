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

