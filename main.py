import pygame
import pymunk
import pymunk.pygame_util
import math
import random, re

from win32api import GetKeyState
import win32api
import win32con
import win32gui
import pyautogui as pg
import keyboard as kb
WIDTH = 300
HEIGHT = 300
FPS=144
DT = 1/FPS
fuchsia = (0, 0, 0)
pygame.font.init()
font = pygame.font.Font(".\Windows Regular.ttf", 50)
    
def draw(space, window, drawOptions, boxes, buttons):
    
    window.fill(fuchsia)
    width, height = pygame.display.get_surface().get_size()
    for i, shape in enumerate(boxes):
        
        rotation = shape.body.angle
        position = shape.body.position
        if (position[0] < 0) or (position[0] > width) or (position[1] > height):
            boxes.pop(i)
            buttons.pop(i)
            space.remove(shape.body, shape)
            continue
        
        text = pygame.transform.rotate(buttons[i], -rotation*(180/math.pi))
        text_width = text.get_width()
        text_height = text.get_height()
        window.blit(text, (position[0]-text_width/2, position[1]-text_height/2))
    pygame.display.update()
    
def createBounds(space):
    width, height = pygame.display.get_surface().get_size()
    rects = [
        [(width/2, height), (width, 10)],
        #[(width/2, 0), (width*100, 10)],
        [(0, height/2), (10, height*100)],
        [(width, height/2), (10, height*100)]
    ]
    
    for pos, size in rects:
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        shape = pymunk.Poly.create_box(body, size)
        shape.elasticity = 1
        shape.friction = 1
        space.add(body, shape)
        
def createBox(space, pos, size, mass, color, boxes):
    body = pymunk.Body()
    body.position = pos
    shape = pymunk.Poly.create_box(body, size)
    shape.elasticity = .5
    shape.friction = .5
    shape.mass = mass
    space.add(body, shape)
    boxes.append(shape)
def createBall(space, radius, mass, color):
    body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    body.position = (300, 300)
    shape = pymunk.Circle(body, radius)
    shape.mass = mass
    shape.elasticity = 1.1
    shape.friction = 3
    space.add(body, shape)
    return shape

def main():
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    run = True
    
    clock = pygame.time.Clock()
    
    space = pymunk.Space()
    space.gravity = (0, 981)
    boxes = []
    buttons = []
    createBounds(space)
    explosionR = 300
    drawOptions = pymunk.pygame_util.DrawOptions(screen)
    mouse = createBall(space, 100, 0, (255,0,0,255))
    
    hwnd = pygame.display.get_wm_info()["window"]
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                        win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
    win32gui.SetWindowPos(pygame.display.get_wm_info()['window'], win32con.HWND_TOPMOST, 0,0,0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)
    
    state_left = win32api.GetKeyState(0x01)
    state_right = win32api.GetKeyState(0x02)
    state_middle = win32api.GetKeyState(0x04)
    def onKeyboardPress(key:kb.KeyboardEvent):
        unicode = None
        if bool(re.search(r'^[a-zA-Z0-9()$%_/.,!#$^&*@~{}:"|<>?_+]*$', key.name)):
            unicode = key.name
        text = font.render(unicode or str.upper(key.name), True, (255, 255, 255))
        text_width = text.get_width()
        text_height = text.get_height()
        createBox(space, (random.randint(20, 1900), -100), (text_width, text_height), 10, (255, 0, 0, 255), boxes)
        buttons.append(text)
        
    kb.on_press(onKeyboardPress) 
    while run:
        x, y = pg.position()    
        mouse.body.position = (x, y)

        a = win32api.GetKeyState(0x01)
        b = win32api.GetKeyState(0x02) 
        c = win32api.GetKeyState(0x04)
        if a != state_left:
            state_left = a
            if a < 0:
                for box in boxes:
                    position = box.body.position
                    magnitudeX = math.pow((x-position[0]), 2)
                    magnitudeY = math.pow((y-position[1]), 2)
                    magnitude = math.sqrt(magnitudeX+magnitudeY)
                    if magnitude > explosionR:
                        continue
                    
                    percent = (magnitude/explosionR)
                    impulse = magnitude-(percent*magnitude)
                    print(impulse)
                    box.body.apply_impulse_at_world_point((math.sqrt(magnitudeX)*1000, math.sqrt(magnitudeY)*1000), (math.sqrt(magnitudeX)+impulse, math.sqrt(magnitudeY)+impulse))
        if b != state_right:  # Button state changed 
            state_right = b 
            if b < 0: 
                for box in boxes:
                    position = box.body.position
                    magnitudeX = math.pow((x-position[0]), 2)
                    magnitudeY = math.pow((y-position[1]), 2)
                    magnitude = math.sqrt(magnitudeX+magnitudeY)
                    if magnitude > explosionR:
                        continue
                    
                    percent = (magnitude/explosionR)
                    impulse = magnitude-(percent*magnitude)
                    box.body.apply_impulse_at_world_point((math.sqrt(magnitudeX)*50, math.sqrt(magnitudeY)*50), (math.sqrt(magnitudeX)+impulse, math.sqrt(magnitudeY)+impulse))
        if c != state_middle:  # Button state changed 
            state_middle = c
            if c < 0: 
                for box in boxes:
                    position = box.body.position
                    magnitudeX = math.pow((x-position[0]), 2)
                    magnitudeY = math.pow((y-position[1]), 2)
                    magnitude = math.sqrt(magnitudeX+magnitudeY)
                    
                    percent = (magnitude/explosionR)
                    impulse = magnitude-(percent*magnitude)
                    box.body.apply_impulse_at_world_point((math.sqrt(magnitudeX)*1000, math.sqrt(magnitudeY)*1000), (math.sqrt(magnitudeX)+impulse, math.sqrt(magnitudeY)+impulse))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False
                break

        draw(space, screen, drawOptions, boxes, buttons)

        space.step(DT)
        clock.tick(FPS)
        
    pygame.quit()
        
if "__main__" == __name__:
    pygame.init()
    main()