#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# game.py
# @Author : David Guez (guezdav@gmail.com)
# @Link   : 
# @Date   : 14/08/2020, 9:21:03

import pygame
import os

SIZE = WIDTH,HEIGHT = 800,600
SCREEN = pygame.display.set_mode(SIZE)
ALL_ELEMENTS=[]
GAME_DIR = os.path.join(os.path.expanduser("~"),'pygamedir')
IMG_DIR = os.path.join(GAME_DIR,'images')
SOUND_DIR = os.path.join(GAME_DIR,'sound')

font_list = {}
actions=[]
responses=[]
cont_action=True
last_draw_time=0

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

class EventResponder:
    def __init__(self, action):
        self._action = action
    def act(self,event,*args,**kwarg):
        self._action(event,*args,**kwarg)
    def should_respond(self,event,*args,**kwarg):
        return False

class KeyboardResponder(EventResponder):
    def __init__(self,key,action):
        super().__init__(action)
        self._key_code = pygame.key.key_code(key)
    def should_respond(self,event):
        return event.type==pygame.KEYDOWN and event.key==self._key_code

class JoystickResponder(EventResponder):
    def __init__(self,button,action):
        super().__init__(action)
        self._button = button
    def should_respond(self,event):
        return event.type==pygame.KEYDOWN and event.key==self._key_code

class MouseResponder(EventResponder):
    def __init__(self,button,action):
        super().__init__(action)
        self._button = button
    def should_respond(self,event):
        return event.type==pygame.KEYDOWN and event.key==self._key_code

class TimerResponder(EventResponder):
    def __init__(self,tick,action):
        super().__init__(action)
        self._tick = tick
    def should_respond(self,event):
        return False # TODO

class DrawingResponder(EventResponder):
    def __init__(self,action):
        super().__init__(action)
    def should_respond(self,event):
        return False # TODO

class Image(Element):
    def __init__(self,img_file,x=0,y=0):
        super().__init__(x,y)
        self.img = pygame.image.load(os.path.join(IMG_DIR,img_file))
        self.rect = self.img.get_rect()
    def _draw(self):
        self.rect.left   = self.x
        self.rect.bottom = self.y
        SCREEN.blit(self.img, self.rect)


def add_response(response_type):
    global responses
    responses.append(response_type)

def remove_response(response_type):
    global responses
    try:
        idx = responses.index(response_type)
        del responses[idx]
    except:
        return

def when(event , action,**kwargs):
    responder=None
    if event=='draw':
        responder = DrawingResponder(action)
    elif event=='key':
        if 'letter' in kwargs:
            responder = KeyboardResponder(kwargs['letter'],action)
        else:
            responder = KeyboardResponder(None,action)
    elif event=='joystick':
        responder = JoystickResponder(None,action)
    elif event=='mouse':
        responder = MouseResponder(None,action)
    
    if responder is not None:
        add_response(responder)
    return responder




class Text(Element):
    def __init__(self,txt,x=0,y=0,font_name='freesansbold.ttf',font_size=32,color=[255,255,255],antialias=False):
        super().__init__(x,y)
        self.antialias=antialias
        self.color=color
        self.txt = txt
        if (font_name,font_size) in font_list:
            self.font = font_list[font_name,font_size]
        else:
            self.font = pygame.font.Font(font_name,font_size)
            font_list[font_name,font_size] = self.font
        
    def _draw(self):
        surf = self.font.render(self.txt,self.antialias, self.color)
        rect = surf.get_rect()
        rect.left = self.x
        rect.top = self.y
        SCREEN.blit(surf , rect)

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


def add_action(action):
    global actions
    actions.append(action)

def start(t=1000/50):

    DRAW_EVENT_ID=pygame.USEREVENT+1
    pygame.time.set_timer(DRAW_EVENT_ID,t)

    while cont_action :
        event = pygame.event.wait()
        if event.type == DRAW_EVENT_ID :
            draw()
        

def stop():
    global cont_action
    cont_action = False

def move(element,dx,dy):
    element.move(dx,dy)
def move_to(element,x,y):
    element.x=x
    element.y=y


def is_pressed(v):
    pygame.event.pump()
    code = pygame.key.key_code(v)
    K = pygame.key.get_pressed()
    return K[code]

def init():
    if not os.path.exists(IMG_DIR) :
        os.makedirs(IMG_DIR)
    if not os.path.exists(SOUND_DIR) :
        os.makedirs(SOUND_DIR)
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