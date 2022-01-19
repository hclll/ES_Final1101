import pygame
from classes.Dashboard import Dashboard
from classes.Level import Level
from classes.Menu import Menu
from classes.Sound import Sound
from entities.Mario import Mario
from server.ws_server import Server

import threading

windowSize = 640, 480


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
    HOST = '172.20.10.4'
    PORT = 61038
    server = Server(HOST, PORT)

    menu = Menu(screen, dashboard, level, sound, server)

    menu.update()
    menu.update()
    menu.update()
    server._connect()
    
    while not menu.start:
        menu.update()

    

    # t = threading.Thread(target = server._start())
    # t.start()
    

    mario = Mario(0, 0, level, screen, dashboard, sound, windowSize, menu)
    clock = pygame.time.Clock()
    

    while not mario.restart:
        pygame.display.set_caption("Attack on GG")

        if mario.pause:
            mario.pauseObj.update()
        else:
            level.drawLevel(mario.camera)
            dashboard.update()
            mario.update()
        pygame.display.update()
        clock.tick(max_frame_rate)

    return 'restart'

    


if __name__ == "__main__":
    exitmessage = 'restart'
    while exitmessage == 'restart':
        exitmessage = main()