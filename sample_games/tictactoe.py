import pygame
import pykidgame.game as game

GAME_SIZE=[600 , 600]
game.init(size=GAME_SIZE)
tictac = game.Image('resources/tictac.png', x=0, y=0)


def placer(i,j,quoi):
    fichier = 'resources/'+quoi+'.png'
    game.Image(fichier, x=i*200, y=j*200)

tour = 'X'

def jouer(event):
    global tour
    i = int(event.pos[0]/200)
    j = int(event.pos[1]/200)
    placer(i,j,tour)
    if tour=='X':
        tour='O'
    else:
        tour='X'

game.when('mouse',jouer,on_up=True)

game.start()