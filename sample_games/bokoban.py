import pygame
import pykidgame.game as game
import numpy as np

BLOCK_SIZE= 32
NB_BLOCK  = 20

fond = game.Image('resources/wall_tiles.jpg')

grille = np.array((NB_BLOCK,NB_BLOCK))
game_size = grille*BLOCK_SIZE

class Object:
    def pos(self,i, j):
        return i * BLOCK_SIZE, j * BLOCK_SIZE

    def __init__(self, i,j,image_file):
        self.image = game.Image(image_file, *self.pos(i,j))
        self.goto(i,j)
    def goto(self,i,j):
        self.i = i
        self.j = j
        x,y = self.pos(i,j)
        self.image.x = x
        self.image.y = y


class Bonhomme(Object):
    def __init__(self, i,j):
        super().__init__(i, j, 'resources/bonhomme.png')

class Boite(Object):
    def __init__(self, i,j):
        super().__init__(i, j, 'resources/boite.png')

class Place(Object):
    def __init__(self, i,j):
        super().__init__(i, j, 'resources/place.png')

bonhomme = Bonhomme(10,10)
boite = Boite(15,10)
place = Place(16,10)
def a_droite():
    bonhomme.image.angle(-90)
    if bonhomme.i < NB_BLOCK:
        bonhomme.goto(bonhomme.i+1,bonhomme.j)
def en_bas():
    bonhomme.image.angle(180)
    if bonhomme.j < NB_BLOCK:
        bonhomme.goto(bonhomme.i,bonhomme.j+1)
def a_gauche():
    bonhomme.image.angle(90)
    if bonhomme.i >0:
        bonhomme.goto(bonhomme.i-1,bonhomme.j)
def en_haut():
    bonhomme.image.angle(0)
    if bonhomme.i > 0:
        bonhomme.goto(bonhomme.i,bonhomme.j-1)

game.init(size=game_size)
game.when('key',letter=pygame.K_RIGHT,action=a_droite)
game.when('key',letter=pygame.K_LEFT,action=a_gauche)
game.when('key',letter=pygame.K_DOWN,action=en_bas)
game.when('key',letter=pygame.K_UP,action=en_haut)
game.start()