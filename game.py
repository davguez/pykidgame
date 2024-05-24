#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# game.py
# @Author : David Guez (guezdav@gmail.com)
# @Link   : 
# @Date   : 14/08/2020, 9:21:03

from typing import List, Union
import pygame
import os, sys
from inspect import signature
from collections.abc import Iterable
from copy import copy

class GAME:
    def __init__(self):
        self.DRAW_EVENT_ID = pygame.USEREVENT

        self.SIZE = [800, 600]
        self.SCREEN = None
        self.ALL_ELEMENTS = []
        self.GAME_DIR = os.path.join(os.path.expanduser("~"), 'pygamedir')
        self.IMG_DIR = os.path.join(self.GAME_DIR, 'images')
        self.SOUND_DIR = os.path.join(self.GAME_DIR, 'sound')

        self.font_list = {}
        self.actions = []
        self.responses = []
        self.cont_action = True
        self.last_draw_time = 0


theGame = GAME()

def reset_everything():
    theGame.font_list = {}
    theGame.actions=[]
    theGame.responses=[]
    theGame.cont_action=True
    theGame.last_draw_time=0


def search_image(img_name  : Union[ str , None]):
    ext_list = ['','.png','.gif','.jpg','.jpeg','.bmp']
    dname = os.path.dirname(sys.argv[0])
    for e in ext_list :
        tst = os.path.join(dname, img_name + e)
        if os.path.exists( tst ):
            return tst
    for e in ext_list :
        tst = os.path.join( theGame.IMG_DIR , img_name + e )
        if os.path.exists( tst ):
            return tst
    return None

class Element:
    def __init__(self,x: int,y: int):
        self.x = x
        self.y = y
        self.show=True
        theGame.ALL_ELEMENTS.append(self)
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

def letter_code(letter) :
    return pygame.key.key_code(letter) if isinstance(letter , str) else letter

class KeyboardResponder(EventResponder):
    def __init__(self,action,letter=None,on_down=True,on_up=False,check_every=None):
        super().__init__(action)
        self._key_code = None if letter is None else letter_code(letter)
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
    def __init__(self,action,on_down=False,on_up=False, on_motion=False,on_wheel=False,buttons=None):
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
        else :
            self._time_id = timer_id + pygame.USEREVENT +1
    def should_respond(self,event):
        return (event.type>theGame.DRAW_EVENT_ID and self._time_id is None) or (event.type == self._time_id)

class DrawingResponder(EventResponder):
    def __init__(self,action):
        super().__init__(action)
    def should_respond(self,event):
        return event.type == theGame.DRAW_EVENT_ID

class Image(Element):
    def __init__(self,img_file:Union[str,None],x:int=0,y:int=0):
        super().__init__(x,y)
        img_file = search_image(img_file)
        if img_file is None:
            return
        self.img = pygame.image.load(img_file)
        self.rect = self.img.get_rect()
        self._angle = 0
        self._img_bank = [self.img]
        self._cur_look = 0
        self._look_way = 1
    def angle(self,angle):
        dtheta = angle-self._angle
        self.img = pygame.transform.rotate(self.img , dtheta)
        self._angle  = angle
    def next_look(self):
        if (self._cur_look + self._look_way >= len(self._img_bank)) or (self._cur_look + self._look_way<0):
            self._look_way *= -1
        self._cur_look += self._look_way
        self.img = self._img_bank[self._cur_look]
        a,self._angle = self._angle , 0
        self.angle(a)
    def _draw(self):
        self.rect.left= self.x
        self.rect.top = self.y
        theGame.SCREEN.blit(self.img, self.rect)
    def add_look(self,img_file:Union[str,None]):
        img_file = search_image(img_file)
        if img_file is None:
            return
        try:
            img = pygame.image.load(img_file)
        except:
            return
        self._img_bank.append(img)
        
        

def number_of_joysticks():
    return pygame.joystick.get_count()

def add_timer(timer_id , every:int , duration=None):
    this_event_id = pygame.USEREVENT + 1 + timer_id
    pygame.time.set_timer(this_event_id, int(every))
    if duration is not None :
        def create_fn():
            ini_time = pygame.time.get_ticks()
            def stop_this_clock(event):
                this_time = pygame.time.get_ticks()
                if this_time - ini_time >= duration :
                    pygame.time.set_timer(this_event_id, 0)
            return stop_this_clock
        when('timer',create_fn(),time_id=timer_id)


def add_response(response_type):
    theGame.responses.append(response_type)

def remove_response(response_type):
    try:
        idx = theGame.responses.index(response_type)
        del theGame.responses[idx]
    except:
        return

def when(event , action,**kwargs):
    responder=None
    if event=='draw':
        responder = DrawingResponder(action)
    elif event=='key':
        passed_keys=['letter','on_down','on_up','check_every']
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
        passed_keys=['timer_id']
        passed_args= { k:v for k,v in kwargs.items() if k in passed_keys }
        if 'every' in kwargs :
            add_timer(kwargs['timer_id'] , kwargs['every'], kwargs.get('duration',None))
        responder = TimerResponder(action,**passed_args)
    
    if responder is not None:
        add_response(responder)
    return responder

def is_key_pressed(letter):
    letter = letter_code(letter)
    return pygame.key.get_pressed()[letter]
    

class Text(Element):
    def __init__(self,txt:str,x:int=0,y:int=0,font_name:str='freesansbold.ttf',font_size:int=32,color:List[int]=[255,255,255],antialias=False):
        super().__init__(x,y)
        self.antialias=antialias
        self.color=color
        self.txt = txt
        if (font_name,font_size) in theGame.font_list:
            self.font = theGame.font_list[font_name,font_size]
        else:
            self.font = pygame.font.Font(font_name,font_size)
            theGame.font_list[font_name,font_size] = self.font
        
    def _draw(self):
        surf = self.font.render(self.txt,self.antialias, self.color)
        rect = surf.get_rect()
        rect.left = self.x
        rect.top = self.y
        theGame.SCREEN.blit(surf , rect)

class Line(Element):
    def __init__(self,x:int=0,y:int=0,w:int=100,h:int=100,color:List[int]=[255,255,255],line_width:int=1,antialias=False):
        super().__init__(x,y)
        self.w=w
        self.h=h
        self.color=color
        self.line_width=line_width
        self.antialias=antialias
    def _draw(self):
        if self.antialias:
            pygame.draw.aaline( theGame.SCREEN, self.color, (self.x,self.y) , (self.x+self.w,self.y+self.h) )
        else:
            pygame.draw.line( theGame.SCREEN, self.color, (self.x,self.y) , (self.x+self.w,self.y+self.h),self.line_width )

class Rect(Element):
    def __init__(self,x:int=0,y:int=0,w:int=100,h:int=100,color:List[int]=[255,255,255],line_width=1):
        super().__init__(x,y)
        self.w=w
        self.h=h
        self.color=color
        self.line_width=line_width
    def _draw(self):
        R = pygame.Rect(self.x,self.y,self.w,self.h)
        pygame.draw.rect( theGame.SCREEN, self.color, R,self.line_width )

class Ellipse(Element):
    def __init__(self,x:int=0,y:int=0,w:int=100,h:int=100,color:List[int]=[255,255,255],line_width=1):
        super().__init__(x,y)
        self.w=w
        self.h=h
        self.color=color
        self.line_width=line_width
    def _draw(self):
        R = pygame.Rect(self.x,self.y,self.w,self.h)
        pygame.draw.ellipse( theGame.SCREEN, self.color, R,self.line_width )


def add_action(action):
    global actions
    actions.append(action)

def start(t=1000/50):
    pygame.time.set_timer(theGame.DRAW_EVENT_ID,int(t))

    while theGame.cont_action :
        event = pygame.event.wait()
        if event.type == theGame.DRAW_EVENT_ID :
            draw()
        if event.type == pygame.QUIT:
            stop()
        for response in theGame.responses :
            if response.should_respond(event) :
                response.act(event)

def stop():
    theGame.cont_action = False

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

def init(size=(800,600)):
    if not os.path.exists(theGame.IMG_DIR) :
        os.makedirs(theGame.IMG_DIR)
    if not os.path.exists(theGame.SOUND_DIR) :
        os.makedirs(theGame.SOUND_DIR)
    theGame.SIZE[:] = size
    theGame.SCREEN = pygame.display.set_mode(theGame.SIZE)
    pygame.init()

def wait(t=20):
    pygame.time.wait(t)

def finish():
    pygame.quit()

def draw():
    theGame.SCREEN.fill([0,0,0])
    for el in theGame.ALL_ELEMENTS:
        el.draw()
    pygame.display.flip()