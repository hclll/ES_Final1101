import json
import sys
import os
import pygame

from classes.Spritesheet import Spritesheet


class Menu:
    def __init__(self, screen, dashboard, level, sound, server, choosenPlayer="Strong Shiba.png", choosenPlayer2="Capoo.jpg"):
        self.screen = screen
        self.sound = sound
        self.start = False
        self.inSettings = False
        self.state = 0
        self.level = level
        self.music = True
        self.sfx = True
        self.currSelectedLevel = 2
        self.currSelectedPlayer = 1
        self.currSelectedPlayer2 = 2
        self.levelNames = []
        self.playerNames = []
        self.inChoosingLevel = False
        self.inChoosingPlayer = False
        self.inTakingPhoto = False
        self.dashboard = dashboard
        self.levelCount = 0
        self.playerCount = 0
        self.choosenPlayer = choosenPlayer
        self.choosenPlayer2 = choosenPlayer2
        self.spritesheet = Spritesheet("./img/title_screen.png")

        self.bannerImg = pygame.image.load("./img/banner.png")
        self.bannerImg.convert()
        self.menu_banner = pygame.transform.scale(self.bannerImg, (500,200))

        self.menu_dot = self.spritesheet.image_at(
            0, 150, 2, colorkey=[255, 0, 220], ignoreTileSize=True
        )
        self.menu_dot2 = self.spritesheet.image_at(
            20, 150, 2, colorkey=[255, 0, 220], ignoreTileSize=True
        )
        self.loadSettings("./settings.json")
        self.server = server
        self.serverDirDelay = 0
        self.serverDirDelay2 = 0

        self.stmImg = pygame.image.load("./img/controller2.png")
        self.stmImg.convert()
        self.stmImg = pygame.transform.scale(self.stmImg, (35,30))

        if self.server.connected2:
            self.playerNum = 2
        else:
            self.playerNum = 1

    def update(self):
        self.checkInput()
        if self.inChoosingLevel:
            return
        elif self.inChoosingPlayer:
            return

        self.drawMenuBackground()
        self.dashboard.update()

        if not self.inSettings:
            self.drawMenu()
        else:
            self.drawSettings()

        # print(self.server)
        if self.server.connected:
            self.screen.blit(self.stmImg, (325, 30))
        else:
            self.dashboard.drawText("Connecting to controller...", 180, 60, 13)
            # pygame.time.delay(500)
            # pygame.display.update()
            # self.server._connect()
            # self.server._setmode(3)



    def drawDot(self):
        if self.state == 0:
            self.screen.blit(self.menu_dot, (145, 273))
            self.screen.blit(self.menu_dot2, (145, 303))
            self.screen.blit(self.menu_dot2, (145, 332))
            self.screen.blit(self.menu_dot2, (145, 362))
        elif self.state == 1:
            self.screen.blit(self.menu_dot2, (145, 273))
            self.screen.blit(self.menu_dot, (145, 303))
            self.screen.blit(self.menu_dot2, (145, 332))
            self.screen.blit(self.menu_dot2, (145, 362))
        elif self.state == 2:
            self.screen.blit(self.menu_dot2, (145, 273))
            self.screen.blit(self.menu_dot2, (145, 303))
            self.screen.blit(self.menu_dot, (145, 332))
            self.screen.blit(self.menu_dot2, (145, 362))
        elif self.state == 3:
            self.screen.blit(self.menu_dot2, (145, 273))
            self.screen.blit(self.menu_dot2, (145, 303))
            self.screen.blit(self.menu_dot2, (145, 332))
            self.screen.blit(self.menu_dot, (145, 362))

    def drawSettingDot(self):
        if self.state == 0:
            self.screen.blit(self.menu_dot, (145, 263))
            self.screen.blit(self.menu_dot2, (145, 293))
            self.screen.blit(self.menu_dot2, (145, 322))
            self.screen.blit(self.menu_dot2, (145, 352))
            self.screen.blit(self.menu_dot2, (145, 382))
        elif self.state == 1:
            self.screen.blit(self.menu_dot2, (145, 263))
            self.screen.blit(self.menu_dot, (145, 293))
            self.screen.blit(self.menu_dot2, (145, 322))
            self.screen.blit(self.menu_dot2, (145, 352))
            self.screen.blit(self.menu_dot2, (145, 382))
        elif self.state == 2:
            self.screen.blit(self.menu_dot2, (145, 263))
            self.screen.blit(self.menu_dot2, (145, 293))
            self.screen.blit(self.menu_dot, (145, 322))
            self.screen.blit(self.menu_dot2, (145, 352))
            self.screen.blit(self.menu_dot2, (145, 382))
        elif self.state == 3:
            self.screen.blit(self.menu_dot2, (145, 263))
            self.screen.blit(self.menu_dot2, (145, 293))
            self.screen.blit(self.menu_dot2, (145, 322))
            self.screen.blit(self.menu_dot, (145, 352))
            self.screen.blit(self.menu_dot2, (145, 382))
        elif self.state == 4:
            self.screen.blit(self.menu_dot2, (145, 263))
            self.screen.blit(self.menu_dot2, (145, 293))
            self.screen.blit(self.menu_dot2, (145, 322))
            self.screen.blit(self.menu_dot2, (145, 352))
            self.screen.blit(self.menu_dot, (145, 382))

    def loadSettings(self, url):
        try:
            with open(url) as jsonData:
                data = json.load(jsonData)
                if data["sound"]:
                    self.music = True
                    self.sound.music_channel.play(self.sound.soundtrack, loops=-1)
                else:
                    self.music = False
                if data["sfx"]:
                    self.sfx = True
                    self.sound.allowSFX = True
                else:
                    self.sound.allowSFX = False
                    self.sfx = False
        except (IOError, OSError):
            self.music = False
            self.sound.allowSFX = False
            self.sfx = False
            self.saveSettings("./settings.json")
    
    def saveSettings(self, url):
        data = {"sound": self.music, "sfx": self.sfx}
        with open(url, "w") as outfile:
            json.dump(data, outfile)

    def drawMenu(self):
        self.drawDot()
        self.dashboard.drawText("CHOOSE LEVEL", 180, 280, 24)
        self.dashboard.drawText("CHOOSE PLAYER", 180, 310, 24)
        self.dashboard.drawText("SETTINGS", 180, 340, 24)
        self.dashboard.drawText("EXIT", 180, 370, 24)

    def drawMenuBackground(self, withBanner=True):
        for y in range(0, 13):
            for x in range(0, 20):
                self.screen.blit(
                    self.level.sprites.spriteCollection.get("sky").image,
                    (x * 32, y * 32),
                )
        for y in range(13, 15):
            for x in range(0, 20):
                self.screen.blit(
                    self.level.sprites.spriteCollection.get("ground").image,
                    (x * 32, y * 32),
                )
        if withBanner:
            self.screen.blit(self.menu_banner, (80, 80))
        if self.choosenPlayer == "Mario.jpg":
            self.screen.blit(
                self.level.sprites.spriteCollection.get("mario_idle").image,
                (2 * 32, 12 * 32),
            )
        else:
            image = pygame.image.load('{}'.format(os.path.join('playerimg', self.choosenPlayer))).convert_alpha()
            image = pygame.transform.scale(image, (int(image.get_size()[0]*32/image.get_size()[1]), 32))
            self.screen.blit(
                image,
                (2 * 32, 12 * 32),
            )
        if self.playerNum == 2:
            if self.choosenPlayer2 == "Mario.jpg":
                self.screen.blit(
                    self.level.sprites.spriteCollection.get("mario_idle").image,
                    (1 * 32, 12 * 32),
                )
            else:
                image = pygame.image.load('{}'.format(os.path.join('playerimg', self.choosenPlayer2))).convert_alpha()
                image = pygame.transform.scale(image, (int(image.get_size()[0]*32/image.get_size()[1]), 32))
                self.screen.blit(
                    image,
                    (1 * 32, 12 * 32),
                )
        self.screen.blit(
            self.level.sprites.spriteCollection.get("bush_1").image, (14 * 32, 12 * 32)
        )
        self.screen.blit(
            self.level.sprites.spriteCollection.get("bush_2").image, (15 * 32, 12 * 32)
        )
        self.screen.blit(
            self.level.sprites.spriteCollection.get("bush_2").image, (16 * 32, 12 * 32)
        )
        self.screen.blit(
            self.level.sprites.spriteCollection.get("bush_2").image, (17 * 32, 12 * 32)
        )
        self.screen.blit(
            self.level.sprites.spriteCollection.get("bush_3").image, (18 * 32, 12 * 32)
        )
        self.screen.blit(self.level.sprites.spriteCollection.get("goomba-1").image, (18.5*32, 12*32))

    def drawSettings(self):
        self.drawSettingDot()
        self.dashboard.drawText("MUSIC", 180, 270, 24)
        if self.music:
            self.dashboard.drawText("ON", 340, 270, 24)
        else:
            self.dashboard.drawText("OFF", 340, 270, 24)
        
        self.dashboard.drawText("SFX", 180, 300, 24)
        if self.sfx:
            self.dashboard.drawText("ON", 340, 300, 24)
        else:
            self.dashboard.drawText("OFF", 340, 300, 24)
        self.dashboard.drawText("RESET", 180, 330, 24)
        self.dashboard.drawText("PLAYER", 180, 360, 24)
        if self.playerNum == 1:
            self.dashboard.drawText("1", 340, 360, 24)
        else:
            self.dashboard.drawText("2", 340, 360, 24)
        self.dashboard.drawText("BACK", 180, 390, 24)
    def chooseLevel(self):
        self.drawMenuBackground(False)
        self.inChoosingLevel = True
        self.levelNames = self.loadLevelNames()
        self.drawLevelChooser()
    
    def choosePlayer(self):
        self.drawMenuBackground(False)
        self.inChoosingPlayer = True
        self.playerNames = self.loadPlayerNames()
        self.drawPlayerChooser()

    def takePhoto(self):
        self.drawMenuBackground(False)
        self.drawTakingPlayerPic()

    def drawBorder(self, x, y, width, height, color, thickness):
        pygame.draw.rect(self.screen, color, (x, y, width, thickness))
        pygame.draw.rect(self.screen, color, (x, y+width, width, thickness))
        pygame.draw.rect(self.screen, color, (x, y, thickness, width))
        pygame.draw.rect(self.screen, color, (x+width, y, thickness, width+thickness))

    def drawLevelChooser(self):
        j = 0
        offset = 75
        textOffset = 90
        for i, levelName in enumerate(self.loadLevelNames()):
            if self.currSelectedLevel == i+1:
                color = (255, 0, 0)
            else:
                color = (150, 150, 150)
            if i < 4:
                self.dashboard.drawText(levelName, 175*i+textOffset, 100, 12)
                self.drawBorder(175*i+offset, 55, 125, 75, color, 5)
            else:
                self.dashboard.drawText(levelName, 175*j+textOffset, 250, 12)
                self.drawBorder(175*j+offset, 210, 125, 75, color, 5)
                j += 1

    def drawPlayerChooser(self):
        j = 0
        offset = 75
        textOffset = 90
        imageOffset = 77
        print(self.loadPlayerNames())
        for i, playerName in enumerate(self.loadPlayerNames()):
            image = pygame.image.load('{}'.format(os.path.join('playerimg', playerName))).convert_alpha()
            image = pygame.transform.scale(image, (125, 125))
            
            if self.currSelectedPlayer == i+1:
                color = (255, 0, 0)
            elif self.playerNum == 2 and self.currSelectedPlayer2 == i+1:
                color = (0, 0, 255)
            else:
                color = (150, 150, 150)

            if i < 3:
                self.screen.blit(image, (175*i+imageOffset, 60))
                self.dashboard.drawText(playerName.split(".")[0], 175*i+textOffset, 193, 12)
                self.drawBorder(175*i+offset, 55, 125, 75, color, 5)
            else:
                self.screen.blit(image, (175*j+imageOffset, 225))
                self.dashboard.drawText(playerName.split(".")[0], 175*j+textOffset, 358, 12)
                self.drawBorder(175*j+offset, 220, 125, 75, color, 5)
                j += 1
    def drawTakingPlayerPic(self):
        # TODO add player's face
        color = (255, 0, 0)
        self.drawBorder(165, 55, 300, 300, color, 5)

    def loadLevelNames(self):
        files = []
        res = []
        for r, d, f in os.walk("./levels"):
            for file in f:
                files.append(os.path.join(r, file))
        for f in files:
            res.append(os.path.split(f)[1].split(".")[0])
        self.levelCount = len(res)
        return res
    
    def loadPlayerNames(self):
        files = []
        res = []
        res1 = []
        for r, d, f in os.walk("./playerimg"):
            for file in f:
                files.append(os.path.join(r, file))
        for f in files:
            if os.path.split(f)[1].split(".")[1] == 'jpg' or os.path.split(f)[1].split(".")[1] == 'png':
                res.append(os.path.split(f)[1].split(".")[0])
                res1.append(os.path.split(f)[1])
        # res.append(res.pop(res.index("Add Player")))
        self.playerCount = len(res)
        # print("res1",res1)
        # print("res",res)
        # print("f",files)
        return res1

    def checkInput(self):
        if self.server.connected:
            self.server.get_data()
            self.server._setmode(1)
            if self.playerNum == 2:
                self.server.get_data2()
                self.server._setmode2(1)
            if self.server.pressed:
                if self.inChoosingLevel:
                    self.inChoosingLevel = False
                    self.dashboard.state = "start"
                    self.dashboard.time = 0
                    self.level.loadLevel(self.levelNames[self.currSelectedLevel-1])
                    self.dashboard.levelName = self.levelNames[self.currSelectedLevel-1].split("Level")[1]
                    self.start = True
                    return
                if self.inChoosingPlayer:
                    if self.playerNames[self.currSelectedPlayer-1] != "Add Player":
                        self.inChoosingPlayer = False
                        self.choosenPlayer = self.playerNames[self.currSelectedPlayer-1]
                        self.choosenPlayer2 = self.playerNames[self.currSelectedPlayer2-1]
                        self.__init__(self.screen, self.dashboard, self.level, self.sound, self.server, self.choosenPlayer, self.choosenPlayer2)
                        return
                    else:
                        self.takePhoto()
                        return
                if not self.inSettings:
                    if self.state == 0:
                        self.chooseLevel()
                    elif self.state == 1:
                        self.choosePlayer()
                    elif self.state == 2:
                        self.inSettings = True
                        self.state = 0
                    elif self.state == 3:
                        pygame.quit()
                        sys.exit()
                else:
                    if self.state == 0:
                        if self.music:
                            self.sound.music_channel.stop()
                            self.music = False
                        else:
                            self.sound.music_channel.play(self.sound.soundtrack, loops=-1)
                            self.music = True
                        self.saveSettings("./settings.json")
                    elif self.state == 1:
                        if self.sfx:
                            self.sound.allowSFX = False
                            self.sfx = False
                        else:
                            self.sound.allowSFX = True
                            self.sfx = True
                        self.saveSettings("./settings.json")
                    elif self.state == 2:
                        pass
                    elif self.state == 3:
                        if self.playerNum == 1:
                            self.server._connect2()
                            self.server._setmode2(3)
                            self.playerNum = 2
                        else:
                            self.playerNum = 1
                        self.saveSettings("./settings.json")
                    elif self.state == 4:
                        self.state = 2
                        self.inSettings = False

            if self.serverDirDelay2 > 0:
                self.serverDirDelay2 -= 1
            elif self.server.keyDirection2 == "Up":
                if self.inChoosingPlayer:
                    if self.currSelectedPlayer2 > 3:
                        self.currSelectedPlayer2 -= 3
                        self.drawPlayerChooser()
                self.serverDirDelay2 = 5
            elif  self.server.keyDirection2 == "Down":
                if self.inChoosingPlayer:
                    if self.currSelectedPlayer2+3 <= self.playerCount:
                        self.currSelectedPlayer2 += 3
                        self.drawPlayerChooser()
                self.serverDirDelay2 = 5
            elif self.server.keyDirection2 == "Left":
                if self.inChoosingPlayer:
                    if self.currSelectedPlayer2 > 1:
                        self.currSelectedPlayer2 -= 1
                        self.drawPlayerChooser()
                self.serverDirDelay2 = 5
            elif self.server.keyDirection2 == "Right":
                if self.inChoosingPlayer:
                    if self.currSelectedPlayer2 < self.playerCount:
                        self.currSelectedPlayer2 += 1
                        self.drawPlayerChooser()
                self.serverDirDelay2 = 5

            if self.serverDirDelay > 0:
                self.serverDirDelay -= 1
            elif self.server.keyDirection == "Up":
                if self.inChoosingLevel:
                    if self.currSelectedLevel > 3:
                        self.currSelectedLevel -= 3
                        self.drawLevelChooser()
                elif self.inChoosingPlayer:
                    if self.currSelectedPlayer > 3:
                        self.currSelectedPlayer -= 3
                        self.drawPlayerChooser()
                if self.state > 0:
                    self.state -= 1
                self.serverDirDelay = 5
            elif self.server.keyDirection == "Down":
                if self.inChoosingLevel:
                    if self.currSelectedLevel+3 <= self.levelCount:
                        self.currSelectedLevel += 3
                        self.drawLevelChooser()
                elif self.inChoosingPlayer:
                    if self.currSelectedPlayer+3 <= self.playerCount:
                        self.currSelectedPlayer += 3
                        self.drawPlayerChooser()
                if not self.inSettings and self.state < 3:
                    self.state += 1
                elif self.inSettings and self.state < 4:
                    self.state += 1
                self.serverDirDelay = 5
            elif self.server.keyDirection == "Left":
                if self.inChoosingLevel:
                    if self.currSelectedLevel > 1:
                        self.currSelectedLevel -= 1
                        self.drawLevelChooser()
                elif self.inChoosingPlayer:
                    if self.currSelectedPlayer > 1:
                        self.currSelectedPlayer -= 1
                        self.drawPlayerChooser()
                self.serverDirDelay = 5
            elif self.server.keyDirection == "Right":
                if self.inChoosingLevel:
                    if self.currSelectedLevel < self.levelCount:
                        self.currSelectedLevel += 1
                        self.drawLevelChooser()
                elif self.inChoosingPlayer:
                    if self.currSelectedPlayer < self.playerCount:
                        self.currSelectedPlayer += 1
                        self.drawPlayerChooser()
                self.serverDirDelay = 5


        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.inChoosingLevel or self.inSettings or self.inChoosingPlayer:
                        self.inChoosingLevel = False
                        self.inSettings = False
                        self.inChoosingPlayer = False
                        self.__init__(self.screen, self.dashboard, self.level, self.sound, self.server, self.choosenPlayer, self.choosenPlayer2)
                    else:
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    if self.inChoosingLevel:
                        if self.currSelectedLevel > 3:
                            self.currSelectedLevel -= 3
                            self.drawLevelChooser()
                    elif self.inChoosingPlayer:
                        if event.key == pygame.K_UP:
                            if self.currSelectedPlayer > 3:
                                self.currSelectedPlayer -= 3
                                self.drawPlayerChooser()
                        else:
                            if self.currSelectedPlayer2 > 3:
                                self.currSelectedPlayer2 -= 3
                                self.drawPlayerChooser()
                    if self.state > 0:
                        self.state -= 1
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    if self.inChoosingLevel:
                        if self.currSelectedLevel+3 <= self.levelCount:
                            self.currSelectedLevel += 3
                            self.drawLevelChooser()
                    elif self.inChoosingPlayer:
                        if event.key == pygame.K_DOWN:
                            if self.currSelectedPlayer+3 <= self.playerCount:
                                self.currSelectedPlayer += 3
                                self.drawPlayerChooser()
                        else:
                            if self.currSelectedPlayer2+3 <= self.playerCount:
                                self.currSelectedPlayer2 += 3
                                self.drawPlayerChooser()
                    if not self.inSettings and self.state < 3:
                        self.state += 1
                    elif self.inSettings and self.state < 4:
                        self.state += 1
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    if self.inChoosingLevel:
                        if self.currSelectedLevel > 1:
                            self.currSelectedLevel -= 1
                            self.drawLevelChooser()
                    elif self.inChoosingPlayer:
                        if event.key == pygame.K_LEFT:
                            if self.currSelectedPlayer > 1:
                                self.currSelectedPlayer -= 1
                                self.drawPlayerChooser()
                        else:
                            if self.currSelectedPlayer2 > 2:
                                self.currSelectedPlayer2 -= 1
                                self.drawPlayerChooser()
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if self.inChoosingLevel:
                        if self.currSelectedLevel < self.levelCount:
                            self.currSelectedLevel += 1
                            self.drawLevelChooser()
                    elif self.inChoosingPlayer:
                        if event.key == pygame.K_RIGHT:
                            if self.currSelectedPlayer < self.playerCount:
                                self.currSelectedPlayer += 1
                                self.drawPlayerChooser()
                        else:
                            if self.currSelectedPlayer2 < self.playerCount:
                                self.currSelectedPlayer2 += 1
                                self.drawPlayerChooser()
                elif event.key == pygame.K_RETURN:
                    if self.inChoosingLevel:
                        self.inChoosingLevel = False
                        self.dashboard.state = "start"
                        self.dashboard.time = 0
                        self.level.loadLevel(self.levelNames[self.currSelectedLevel-1])
                        self.dashboard.levelName = self.levelNames[self.currSelectedLevel-1].split("Level")[1]
                        self.start = True
                        return
                    if self.inTakingPhoto:
                        self.inTakingPhoto = False
                        return
                    if self.inChoosingPlayer:
                        if self.playerNames[self.currSelectedPlayer-1] != "Add Player":
                            self.inChoosingPlayer = False
                            self.choosenPlayer = self.playerNames[self.currSelectedPlayer-1]
                            self.choosenPlayer2 = self.playerNames[self.currSelectedPlayer2-1]
                            print(self.choosenPlayer)
                            self.__init__(self.screen, self.dashboard, self.level, self.sound, self.server, self.choosenPlayer, self.choosenPlayer2)
                            return
                        else:
                            self.inTakingPhoto = True
                            self.currSelectedPlayer = 1
                            self.currSelectedPlayer2 = 2
                            self.takePhoto()
                            return
                    if not self.inSettings:
                        if self.state == 0:
                            self.chooseLevel()
                        elif self.state == 1:
                            self.choosePlayer()
                        elif self.state == 2:
                            self.inSettings = True
                            self.state = 0
                        elif self.state == 3:
                            pygame.quit()
                            sys.exit()
                    else:
                        if self.state == 0:
                            if self.music:
                                self.sound.music_channel.stop()
                                self.music = False
                            else:
                                self.sound.music_channel.play(self.sound.soundtrack, loops=-1)
                                self.music = True
                            self.saveSettings("./settings.json")
                        elif self.state == 1:
                            if self.sfx:
                                self.sound.allowSFX = False
                                self.sfx = False
                            else:
                                self.sound.allowSFX = True
                                self.sfx = True
                            self.saveSettings("./settings.json")
                        elif self.state == 2:
                            pass
                        elif self.state == 3:
                            if self.playerNum == 1:
                                self.server._connect2()
                                self.server._setmode2(3)
                                self.playerNum = 2
                            else:
                                self.playerNum = 1
                            self.saveSettings("./settings.json")
                        else:
                            self.state = 2
                            self.inSettings = False

        pygame.display.update()
