#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# game.py
# @Author : David Guez (guezdav@gmail.com)
# @Link   : 
# @Date   : 14/08/2020, 9:21:03

import pygame
import os, sys
from inspect import signature
from collections.abc import Iterable
from copy import copy

DRAW_EVENT_ID=pygame.USEREVENT

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


def reset_everything():
    global font_list , actions, responses, cont_action, last_draw_time
    font_list = {}
    actions=[]
    responses=[]
    cont_action=True
    last_draw_time=0


def search_image(img_name):
    ext_list = ['','.png','.gif','.jpg','.jpeg','.bmp']
    dname = os.path.dirname(sys.argv[0])
    for e in ext_list :
        tst = os.path.join(dname, img_name + e)
        if os.path.exists( tst ):
            return tst
    for e in ext_list :
        tst = os.path.join( IMG_DIR , img_name + e )
        if os.path.exists( tst ):
            return tst
    return None

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
        sig = signature(action)
        if len(sig.parameters)==0 :
            self._action = lambda e : action()
        else:
            self._action = action
    def act(self,event):
        self._action(event)
    def should_respond(self,event):
        return False

class KeyboardResponder(EventResponder):
    def __init__(self,action,letter=None,on_down=True,on_up=False):
        super().__init__(action)
        self._key_code = None if letter is None else pygame.key.key_code(letter)
        self._state=[]
        if on_down :
            self._state.append(pygame.KEYDOWN)
        if on_up :
            self._state.append(pygame.KEYUP)
    def should_respond(self,event):
        return event.type in self._state and ( self._key_code is None or event.key==self._key_code )

class JoystickResponder(EventResponder):
    def __init__(self,action,on_down=True,on_up=False,on_motion=True,axis=None,buttons=None,joy_num=None):
        super().__init__(action)

        if buttons is None:
            self._buttons = None
        elif isinstance(buttons,Iterable):
            self._buttons = copy(buttons)
        else:
            self._buttons = [ buttons ]

        if axis is None:
            self._axis = None
        elif isinstance(axis,Iterable):
            self._axis = copy(axis)
        else:
            self._axis = [ axis ]

        self._joy_num=joy_num
        self._state=[]
        if on_down :
            self._state.append(pygame.JOYBUTTONDOWN)
        if on_up :
            self._state.append(pygame.JOYBUTTONUP)
        if on_motion :
            self._state.append(pygame.JOYAXISMOTION)

    def should_respond(self,event):
        return event.type in self._state and (self._joy_num is None or event.joy == self._joy_num) \
            and ( self._buttons is None or event.button in self._buttons ) \
            and (self._axis is None or event.axis in self._axis)

class MouseResponder(EventResponder):
    def __init__(self,action,on_down=True,on_up=False, on_motion=True,on_wheel=True,buttons=None):
        super().__init__(action)

        if buttons is None:
            self._buttons = None
        elif isinstance(buttons,Iterable):
            self._buttons = copy(buttons)
        else:
            self._buttons = [ buttons ]

        self._state=[]
        if on_down :
            self._state.append(pygame.MOUSEBUTTONDOWN)
        if on_up :
            self._state.append(pygame.MOUSEBUTTONUP)
        if on_motion :
            self._state.append(pygame.MOUSEMOTION)
        if on_wheel :
            self._state.append(pygame.MOUSEWHEEL)
    def should_respond(self,event):
        return event.type in self._state and ( self._buttons is None or event.button in self._buttons )
        

class TimerResponder(EventResponder):
    def __init__(self,action,timer_id=None):
        super().__init__(action)
        if timer_id is None:
            self._time_id = None
        else:
            self._time_id = timer_id + pygame.USEREVENT +1
    def should_respond(self,event):
        return (event.type>DRAW_EVENT_ID and self._time_id is None) or (event.type == self._time_id)

class DrawingResponder(EventResponder):
    def __init__(self,action):
        super().__init__(action)
    def should_respond(self,event):
        return event.type == DRAW_EVENT_ID

class Image(Element):
    def __init__(self,img_file,x=0,y=0):
        super().__init__(x,y)
        img_file = search_image(img_file)
        if img_file is None:
            return
        self.img = pygame.image.load(img_file)
        self.rect = self.img.get_rect()
    def _draw(self):
        self.rect.left= self.x
        self.rect.top = self.y
        SCREEN.blit(self.img, self.rect)

def number_of_joysticks():
    return pygame.joystick.get_count()

def add_timer(timer_id , every , duration=None):
    pygame.time.set_timer(pygame.USEREVENT + 1 + timer_id, int(every))
    if duration is not None :
        def create_fn():
            ini_time = pygame.time.get_ticks()
            def stop_this_clock(event):
                this_time = pygame.time.get_ticks()
                if this_time - ini_time >= duration :
                    pygame.time.set_timer(pygame.USEREVENT + 1 + timer_id, 0)
            return stop_this_clock
        when('timer',create_fn(),time_id=timer_id)


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
        passed_keys=['letter','on_down','on_up']
        passed_args= { k:v for k,v in kwargs.items() if k in passed_keys }
        responder = KeyboardResponder(action,**passed_args)
    elif event=='joystick':
        passed_keys=['on_down','on_up', 'on_motion','buttons','axis','joy_num']
        passed_args= { k:v for k,v in kwargs.items() if k in passed_keys }
        responder = JoystickResponder(action,**passed_args)
    elif event=='mouse':
        passed_keys=['on_down','on_up', 'on_motion','on_wheel','buttons']
        passed_args= { k:v for k,v in kwargs.items() if k in passed_keys }
        responder = MouseResponder(action,**passed_args)
    elif event=='timer':
        passed_keys=['time_id']
        passed_args= { k:v for k,v in kwargs.items() if k in passed_keys }
        responder = TimerResponder(action,**passed_args)
    
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
    pygame.time.set_timer(DRAW_EVENT_ID,int(t))

    while cont_action :
        event = pygame.event.wait()
        if event.type == DRAW_EVENT_ID :
            draw()
        for response in responses :
            if response.should_respond(event) :
                response.act(event)

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