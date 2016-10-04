# Defines Headers, State For Carromimport sys, random
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import pymunk.pygame_util
import random
import sys
import os
from math import sqrt,sin,cos,tan
import ast

# Global Variables

Static_Velocity_Threshold=0.1 # Velocity below which an object is considered to be static



Board_Size=800
Board_Damping=0.75# Tune how much the velocity falls


Striker_Angle=(0,1)
Striker_Force=(5000)

Board_Walls_Size=Board_Size*2/90
Board_Size_Walls_Elasticity=0.9

Coin_Mass=1.5  ## weight is 5 grams but pymunk dont have any unit for mass ... set a value which suit other paramater 
Coin_Radius=15.01
Coin_Elasticity=0.9

Striker_Mass=3
Striker_Radius=20.6
Striker_Elasticity=0.9

Hole_Radius=22.21

Striker_Color=[65,125,212]
Hole_Color=[0,0,0]
Black_Coin_Color=[43,43,43]
White_Coin_Color= [169,121,47]
Red_Coin_Color=[169,53,53]
Board_Walls_Color=[56,32,12]
Board_Color=[242,209,158]

def parse_state_message(msg):

    s=msg.split(";REWARD")
    s[0]=s[0].replace("Vec2d","")
    reward=float(s[1])
    State=ast.literal_eval(s[0])
    return State, reward # Return next state and reward





def dist(p1,p2):
    return sqrt(pow(p1[0]-p2[0],2)+pow(p1[1]-p2[1],2))


#N randomly generated coin positions around the center of the board
def generate_coin_locations(N):
    # Later do collision handling
    L=[]
    for i in range(N):
        L.append((random.randrange(0.3*Board_Size,0.7*Board_Size),(random.randrange(0.3*Board_Size,0.7*Board_Size))))

    return L

def init_space(space):
    space.damping = Board_Damping
    space.threads=2

def init_walls(space):  # Initializes the four outer walls of the board
    walls = [pymunk.Segment(space.static_body, (0, 0), (0, Board_Size), Board_Walls_Size)
        ,pymunk.Segment(space.static_body, (0,0), (Board_Size, 0), Board_Walls_Size)
        ,pymunk.Segment(space.static_body, (Board_Size, Board_Size), (Board_Size, 0), Board_Walls_Size)
        ,pymunk.Segment(space.static_body, (Board_Size, Board_Size), (0,Board_Size), Board_Walls_Size)
        ]  
    for wall in walls:
        wall.color = Board_Walls_Color
        wall.elasticity = Board_Size_Walls_Elasticity
        
    
    space.add(walls)

def init_holes(space):  # Initializes the four outer walls of the board
    Holes=[]
    for i in [(39.1, 39.1),(760.9, 39.1),(760.9, 760.9),(39.1,760.9)]:
        inertia = pymunk.moment_for_circle(0.1, 0, Hole_Radius, (0,0))
        body = pymunk.Body(0.1, inertia)
        body.position = i
        shape = pymunk.Circle(body, Hole_Radius, (0,0))
        shape.color=Hole_Color
        shape.collision_type = 2
        shape.filter = pymunk.ShapeFilter(categories=0b1000)
        space.add(body, shape)
        Holes.append(shape)
        del body
        del shape
    return Holes

def init_striker(space,x, passthrough,action,Player):
    """Add a ball to the given space at a random position"""

    inertia = pymunk.moment_for_circle(Striker_Mass, 0, Striker_Radius, (0,0))
    body = pymunk.Body(Striker_Mass, inertia)
    if Player==1:
        body.position = (action[1],145)
    if Player==2:
        body.position = (action[1],Board_Size - 136)
    body.apply_force_at_world_point((cos(action[0])*action[2],sin(action[0])*action[2]),body.position+(Striker_Radius*0,Striker_Radius*0))
    #print body.position
    shape = pymunk.Circle(body, Striker_Radius, (0,0))
    shape.elasticity=Striker_Elasticity
    shape.color=Striker_Color

    mask = pymunk.ShapeFilter.ALL_MASKS ^ passthrough.filter.categories

    sf = pymunk.ShapeFilter(mask=mask)
    shape.filter = sf 
    shape.collision_type=2
    
    space.add(body, shape)
    return shape

def init_coins(space,coords_black,coords_white,coord_red,passthrough):
    #Adds coins to the board at the given coordinates 
    Coins=[]
    inertia = pymunk.moment_for_circle(Coin_Mass, 0, Coin_Radius, (0,0))
    for coord in coords_black:

        #shape.elasticity=1
        #body.position = i
        body=pymunk.Body(Coin_Mass, inertia)
        body.position=coord
        shape=pymunk.Circle(body, Coin_Radius, (0,0))
        shape.elasticity=Coin_Elasticity
        shape.color=Black_Coin_Color


        mask = pymunk.ShapeFilter.ALL_MASKS ^ passthrough.filter.categories

        sf = pymunk.ShapeFilter(mask=mask)
        shape.filter = sf 
        shape.collision_type=2

        space.add(body, shape)
        Coins.append(shape)
        del body
        del shape

        #body.apply_force_at_world_point((-1000,-1000),body.position)

        #shape.elasticity=1
        #body.position = i
    for coord in coords_white:
        body=pymunk.Body(Coin_Mass, inertia)
        body.position=coord
        shape=pymunk.Circle(body, Coin_Radius, (0,0))
        shape.elasticity=Coin_Elasticity
        shape.color=White_Coin_Color

        mask = pymunk.ShapeFilter.ALL_MASKS ^ passthrough.filter.categories

        sf = pymunk.ShapeFilter(mask=mask)
        shape.filter = sf 
        shape.collision_type=2

        space.add(body, shape)
        Coins.append(shape)
        del body
        del shape
        #body.apply_force_at_world_point((-1000,-1000),body.position)

    for coord in coord_red:
        body=pymunk.Body(Coin_Mass, inertia)
        body.position=coord
        shape=pymunk.Circle(body, Coin_Radius, (0,0))
        shape.elasticity=Coin_Elasticity
        shape.color=Red_Coin_Color
        mask = pymunk.ShapeFilter.ALL_MASKS ^ passthrough.filter.categories

        sf = pymunk.ShapeFilter(mask=mask)
        shape.filter = sf 
        shape.collision_type=2

        space.add(body, shape)
        Coins.append(shape)
        del body
        del shape
    return Coins

##load image in game

"""def load_image(name, colorkey=None):
    fullname = os.path.join('images', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    surface = pygame.display.set_mode((Board_Size, Board_Size))
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

"""

'''def load_image(name, colorkey=None):
    img = pygame.image.load(name)
    white = (255, 64, 64)
    screen = pygame.display.set_mode((Board_Size, Board_Size))
    screen.fill((white))
    running = 1
    screen.fill((white))
    screen.blit(img,(0,0))
    pygame.display.flip()'''

class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location

