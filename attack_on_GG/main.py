import pygame
from classes.Dashboard import Dashboard
from classes.Level import Level
from classes.Menu import Menu
from classes.Sound import Sound
from entities.Mario import Mario
from entities.Mario1 import Mario1
from server.ws_server import Server

import threading

windowSize = 640, 480

HOST = '192.168.203.224'
PORT = 61038

server = Server(HOST, PORT)


def main():
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()
    screen = pygame.display.set_mode(windowSize)
    max_frame_rate = 60
    dashboard = Dashboard("./img/font.png", 8, screen)
    sound = Sound()
    level = Level(screen, sound, dashboard)

    '''
    Server
    '''
    
    menu = Menu(screen, dashboard, level, sound, server)

    menu.update()
    menu.update()
    menu.update()

    # if not server.connected:
    #     server._connect()
    
    while not menu.start:
        menu.update()

    

    # t = threading.Thread(target = server._start())
    # t.start()

    pos2mario = [0,0]

    mario = Mario(0, 0, level, screen, dashboard, sound, windowSize, menu, pos2mario)
    camera = mario.camera

    clock = pygame.time.Clock()
    
    if menu.playerNum == 2:
        mario1 = Mario1(0.01, 0, level, screen, dashboard, sound, windowSize, menu, pos2mario, camera)


    while not mario.restart:
        if menu.playerNum == 2:
            if mario1.restart:
                return 'restart'
        pygame.display.set_caption("Attack on GG")
        if mario.pause:
            mario.pauseObj.update()
        else:
            if menu.playerNum == 2:
                pos2mario[0] = mario.getPosIndexAsFloat().x
                pos2mario[1] = mario1.getPosIndexAsFloat().x
                # if pos2mario[0] > pos2mario[1]:
                #     cam = mario.camera
                #     menu.globalCamPosX = cam.pos.x
                    
                # else:
                #     cam = mario1.camera
                #     menu.globalCamPosX = cam.pos.x
                    
            else:
                cam = mario.camera
            level.drawLevel(camera)
            #print(pos2mario)

            dashboard.update()
            mario.update()
            if menu.playerNum == 2:
                mario1.update()
        pygame.display.update()
        clock.tick(max_frame_rate)
    return 'restart'

    


if __name__ == "__main__":
    exitmessage = 'restart'
    while exitmessage == 'restart':
        exitmessage = main()