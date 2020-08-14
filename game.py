#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# game.py
# @Author : David Guez (guezdav@gmail.com)
# @Link   : 
# @Date   : 14/08/2020, 9:21:03

import pygame

SIZE = WIDTH,HEIGHT = 800,600
SCREEN = pygame.display.set_mode(SIZE)
ALL_ELEMENTS=[]

class Element:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.show=True
        ALL_ELEMENTS.append(self)
    def _draw(self):
        pass
    def draw(self):
        if self.show:
            self._draw()
    def move(self,x,y):
        self.x += x
        self.y += y

class Image(Element):
    def __init__(self,img_file,x=0,y=0):
        super().__init__(x,y)
        self.img = pygame.image.load(img_file)
        self.rect = self.img.get_rect()
    def _draw(self):
        self.rect.left   = self.x
        self.rect.bottom = self.y
        SCREEN.blit(self.img, self.rect)

class Text(Element):
    def __init__(self,txt,x=0,y=0):
        super().__init__(x,y)
        self.txt = txt
    def _draw(self):
        pass

class Line(Element):
    def __init__(self,x=0,y=0,w=100,h=100,color=[255,255,255],line_width=1,antialias=False):
        super().__init__(x,y)
        self.w=w
        self.h=h
        self.color=color
        self.line_width=line_width
        self.antialias=antialias
    def _draw(self):
        if self.antialias:
            pygame.draw.aaline( SCREEN, self.color, (self.x,self.y) , (self.x+self.w,self.y+self.h) )
        else:
            pygame.draw.line( SCREEN, self.color, (self.x,self.y) , (self.x+self.w,self.y+self.h),self.line_width )

class Rect(Element):
    def __init__(self,x=0,y=0,w=100,h=100,color=[255,255,255],line_width=1):
        super().__init__(x,y)
        self.w=w
        self.h=h
        self.color=color
        self.line_width=line_width
    def _draw(self):
        R = pygame.Rect(self.x,self.y,self.w,self.h)
        pygame.draw.rect( SCREEN, self.color, R,self.line_width )

class Ellipse(Element):
    def __init__(self,x=0,y=0,w=100,h=100,color=[255,255,255],line_width=1):
        super().__init__(x,y)
        self.w=w
        self.h=h
        self.color=color
        self.line_width=line_width
    def _draw(self):
        R = pygame.Rect(self.x,self.y,self.w,self.h)
        pygame.draw.ellipse( SCREEN, self.color, R,self.line_width )



def is_pressed(v):
    pygame.event.pump()
    code = pygame.key.key_code(v)
    K = pygame.key.get_pressed()
    return K[code]

def start():
    pygame.init()

def wait(t=20):
    pygame.time.wait(t)

def finish():
    pygame.quit()

def draw():
    SCREEN.fill([0,0,0])
    for el in ALL_ELEMENTS:
        el.draw()
    pygame.display.flip()