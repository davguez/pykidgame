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

    def __init__(self, i,j,image_or_file):
        self.image = game.Image(image_or_file, *self.pos(i,j))
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
    img = game.image('resources/boite.png')
    def __init__(self, i,j):
        super().__init__(i, j, self.img )

class Place(Object):
    img = game.image('resources/place.png')
    def __init__(self, i,j):
        super().__init__(i, j, self.img)

class Jeu:
    def __init__(self) -> None:
        ...

boite = Boite(15,10)
place = Place(16,10)
place = Place(17,10)
bonhomme = Bonhomme(10,10)

def a_droite():
    bonhomme.image.angle(-90)
    if bonhomme.i < NB_BLOCK-1:
        bonhomme.goto(bonhomme.i+1,bonhomme.j)
def en_bas():
    bonhomme.image.angle(180)
    if bonhomme.j < NB_BLOCK-1:
        bonhomme.goto(bonhomme.i,bonhomme.j+1)
def a_gauche():
    bonhomme.image.angle(90)
    if bonhomme.i >0:
        bonhomme.goto(bonhomme.i-1,bonhomme.j)
def en_haut():
    bonhomme.image.angle(0)
    if bonhomme.j > 0:
        bonhomme.goto(bonhomme.i,bonhomme.j-1)

game.init(size=game_size)
game.when('key',letter=pygame.K_RIGHT,action=a_droite,check_every=50)
game.when('key',letter=pygame.K_LEFT,action=a_gauche,check_every=50)
game.when('key',letter=pygame.K_DOWN,action=en_bas,check_every=50)
game.when('key',letter=pygame.K_UP,action=en_haut,check_every=50)
game.start()