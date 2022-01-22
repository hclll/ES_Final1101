import pygame
from pygame.locals import *
import sys


class Input:
    def __init__(self, entity, server):
        self.mouseX = 0
        self.mouseY = 0
        self.entity = entity
        self.server = server

    def checkForInput(self):
        events = pygame.event.get()
        self.checkForKeyboardInput()
        self.checkForMouseInput(events)
        self.checkForQuitAndRestartInputEvents(events)

    def checkForKeyboardInput(self):
        pressedKeys = pygame.key.get_pressed()
        if self.server.connected:
            self.server.get_data()
            self.server._setmode(2)

        if (pressedKeys[K_LEFT] or pressedKeys[K_h] and not pressedKeys[K_RIGHT]) or self.server.keyDirection == "Left":
            self.entity.traits["goTrait"].direction = -1
        elif (pressedKeys[K_RIGHT] or pressedKeys[K_l] and not pressedKeys[K_LEFT]) or self.server.keyDirection == "Right":
            self.entity.traits["goTrait"].direction = 1
        else:
            self.entity.traits['goTrait'].direction = 0

        isJumping = pressedKeys[K_SPACE] or pressedKeys[K_UP] or pressedKeys[K_k] or (self.server.loudness > 85)
        
        isFencing = pressedKeys[K_c] or (self.server.attack)
        isShooting = pressedKeys[K_v] or (self.server.pressed)

        self.entity.traits['jumpTrait'].jump(isJumping)
        self.entity.isFencing = isFencing
        self.entity.isShooting = isShooting

        self.entity.traits['goTrait'].boost = pressedKeys[K_LSHIFT]

    def checkForMouseInput(self, events):
        mouseX, mouseY = pygame.mouse.get_pos()
        if self.isRightMouseButtonPressed(events):
            self.entity.levelObj.addKoopa(
                mouseY / 32, mouseX / 32 - self.entity.camera.pos.x
            )
            self.entity.levelObj.addGoomba(
                mouseY / 32, mouseX / 32 - self.entity.camera.pos.x
            )
            self.entity.levelObj.addRedMushroom(
                mouseY / 32, mouseX / 32 - self.entity.camera.pos.x
            )
        if self.isLeftMouseButtonPressed(events):
            self.entity.levelObj.addCoin(
                mouseX / 32 - self.entity.camera.pos.x, mouseY / 32
            )

    def checkForQuitAndRestartInputEvents(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and \
                (event.key == pygame.K_ESCAPE or event.key == pygame.K_F5):
                self.entity.pause = True
                self.entity.pauseObj.createBackgroundBlur()

    def isLeftMouseButtonPressed(self, events):
        return self.checkMouse(events, 1)

    def isRightMouseButtonPressed(self, events):
        return self.checkMouse(events, 3)

    def checkMouse(self, events, button):
        for e in events:
            if e.type == pygame.MOUSEBUTTONUP and e.button == button:
                return True
        return False
