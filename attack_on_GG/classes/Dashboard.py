import pygame

from classes.Font import Font


class Dashboard(Font):
    def __init__(self, filePath, size, screen):
        Font.__init__(self, filePath, size)
        self.state = "menu"
        self.screen = screen
        self.levelName = ""
        self.points = 0
        self.coins = 0
        self.ticks = 0
        self.time = 0
        self.life = 3

        self.lifeImg = pygame.image.load("./img/life.png")
        self.lifeImg.convert()
        self.lifeImg = pygame.transform.scale(self.lifeImg, (15, 15))

    def update(self):
        self.drawText("GG!!", 50, 20, 15)
        self.drawText(self.pointString(), 50, 37, 15)

        self.drawText("@x{}".format(self.coinString()), 180, 37, 15)

        self.screen.blit(self.lifeImg, (260, 37))
        self.drawText("x{}".format(self.lifeString()), 280, 37, 15)

        self.drawText("WORLD", 380, 20, 15)
        self.drawText(str(self.levelName), 395, 37, 15)

        self.drawText("TIME", 520, 20, 15)
        if self.state != "menu":
            self.drawText(self.timeString(), 535, 37, 15)

        # update Time
        self.ticks += 1
        if self.ticks == 60:
            self.ticks = 0
            self.time += 1

    def drawText(self, text, x, y, size):
        for char in text:
            charSprite = pygame.transform.scale(self.charSprites[char], (size, size))
            self.screen.blit(charSprite, (x, y))
            if char == " ":
                x += size//2
            else:
                x += size

    def coinString(self):
        return "{:02d}".format(self.coins)

    def pointString(self):
        return "{:06d}".format(self.points)

    def timeString(self):
        return "{:03d}".format(self.time)

    def lifeString(self):
        return "{:01d}".format(self.life)
