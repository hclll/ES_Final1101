import pygame

from classes.Animation import Animation
from classes.Camera import Camera
from classes.Collider import Collider
from classes.EntityCollider import EntityCollider
from classes.Input import Input
from classes.Sprites import Sprites
from entities.EntityBase import EntityBase
from entities.Mushroom import RedMushroom
from traits.bounce import bounceTrait
from traits.go import GoTrait
from traits.jump import JumpTrait
from classes.Pause import Pause
from classes.Maths import Vec2D
from entities.Bullet import Bullet
from entities.Sword import Sword
import os



class Mario(EntityBase):
    def __init__(self, x, y, level, screen, dashboard, sound, windowSize, menu, gravity=0.8):
        self.menu = menu
        if self.menu.choosenPlayer == "Mario":
            super(Mario, self).__init__(x, y, gravity)
        else:
            self.image = pygame.image.load('{}.jpg'.format(os.path.join('playerimg', self.menu.choosenPlayer))).convert_alpha()
            self.image = pygame.transform.scale(self.image, (int(self.image.get_size()[0]*32/self.image.get_size()[1]), 32))
            super(Mario, self).__init__(x, y, gravity, int(self.image.get_size()[0]*32/self.image.get_size()[1]), 32)

        spriteCollection = Sprites().spriteCollection
        if self.menu.choosenPlayer == "Mario":
            self.smallAnimation = Animation(
                [
                    spriteCollection["mario_run1"].image,
                    spriteCollection["mario_run2"].image,
                    spriteCollection["mario_run3"].image,
                ],
                spriteCollection["mario_idle"].image,
                spriteCollection["mario_jump"].image,
            )
            self.bigAnimation = Animation(
                [
                    spriteCollection["mario_big_run1"].image,
                    spriteCollection["mario_big_run2"].image,
                    spriteCollection["mario_big_run3"].image,
                ],
                spriteCollection["mario_big_idle"].image,
                spriteCollection["mario_big_jump"].image,
            )
        else:
            self.smallAnimation = Animation(
                [self.image],
                self.image,
                self.image
            )
            self.bigimage = pygame.transform.scale(self.image, (int(self.image.get_size()[0]*64/self.image.get_size()[1]), 64))
            self.bigAnimation = Animation(
                [self.bigimage],
                self.bigimage,
                self.bigimage
            )
        self.camera = Camera(self.rect, self)
        self.sound = sound
        self.windowSize = windowSize
        self.input = Input(self)
        self.inAir = False
        self.inJump = False
        self.powerUpState = 0
        self.invincibilityFrames = 0
        self.traits = {
            "jumpTrait": JumpTrait(self),
            "goTrait": GoTrait(self.smallAnimation, screen, self.camera, self),
            "bounceTrait": bounceTrait(self),
        }
        self.lr_direction = self.traits["goTrait"].heading
        self.isFencing = False
        self.isShooting = False

        self.levelObj = level
        self.collision = Collider(self, level)
        self.screen = screen
        self.EntityCollider = EntityCollider(self)
        self.dashboard = dashboard
        self.restart = False
        self.pause = False
        self.pauseObj = Pause(screen, self, dashboard)
        self.bullets = pygame.sprite.Group()
        self.swords = pygame.sprite.Group()

        self.time = 0
        self.t_wait = 50
        self.pre_shoot = -self.t_wait
        self.pre_fence = -self.t_wait
        self.pre_loseLife = -self.t_wait

        #self.life = 3

    def update(self):
        if self.invincibilityFrames > 0:
            self.invincibilityFrames -= 1
        self.updateTraits()
        self.moveMario()
        self.camera.move()
        self.applyGravity()
        self.checkEntityCollision()
        self.input.checkForInput()
        self.lr_direction = self.traits["goTrait"].heading

        if self.isShooting and (self.time - self.pre_shoot) > 10:
            self.shoot()
            self.pre_shoot = self.time
        self.bullets.update()

        if self.isFencing: 
            self.fence()
        self.swords.update()

        self.checkPos()

        self.time += 1
        

    def moveMario(self):
        self.rect.y += self.vel.y
        self.collision.checkY()
        self.rect.x += self.vel.x
        self.collision.checkX()

    def checkPos(self):
        if self.getPos()[0] >= self.windowSize[0] - 40:
            self.win()

    def checkEntityCollision(self):
        for ent in self.levelObj.entityList:
            collisionState = self.EntityCollider.check(ent)
            if collisionState.isColliding:
                if ent.type == "Item":
                    self._onCollisionWithItem(ent)
                elif ent.type == "Block":
                    self._onCollisionWithBlock(ent)
                elif ent.type == "Mob":
                    self._onCollisionWithMob(ent, collisionState)

    def _onCollisionWithItem(self, item):
        self.levelObj.entityList.remove(item)
        self.dashboard.points += 100
        self.dashboard.coins += 1
        self.sound.play_sfx(self.sound.coin)

    def _onCollisionWithBlock(self, block):
        if not block.triggered:
            self.dashboard.coins += 1
            self.sound.play_sfx(self.sound.bump)
        block.triggered = True

    def _onCollisionWithMob(self, mob, collisionState):
        if isinstance(mob, RedMushroom) and mob.alive:
            self.powerup(1)
            self.killEntity(mob)
            self.sound.play_sfx(self.sound.powerup)
        elif collisionState.isTop and (mob.alive or mob.bouncing):
            self.sound.play_sfx(self.sound.stomp)
            self.rect.bottom = mob.rect.top
            self.bounce()
            self.killEntity(mob)
        elif collisionState.isTop and mob.alive and not mob.active:
            self.sound.play_sfx(self.sound.stomp)
            self.rect.bottom = mob.rect.top
            mob.timer = 0
            self.bounce()
            mob.alive = False
        elif collisionState.isColliding and mob.alive and not mob.active and not mob.bouncing:
            mob.bouncing = True
            if mob.rect.x < self.rect.x:
                mob.leftrightTrait.direction = -1
                mob.rect.x += -5
                self.sound.play_sfx(self.sound.kick)
            else:
                mob.rect.x += 5
                mob.leftrightTrait.direction = 1
                self.sound.play_sfx(self.sound.kick)
        elif collisionState.isColliding and mob.alive and not self.invincibilityFrames:
            if self.powerUpState == 0:
                if self.time - self.pre_loseLife > self.t_wait:
                    self.loseLife()

                if self.dashboard.life <= 0:
                    self.gameOver()
                #self.gameOver()
            elif self.powerUpState == 1:
                self.powerUpState = 0
                self.traits['goTrait'].updateAnimation(self.smallAnimation)
                x, y = self.rect.x, self.rect.y
                self.rect = pygame.Rect(x, y + 32, int(self.image.get_size()[0]*32/self.image.get_size()[1]), 32)
                self.invincibilityFrames = 60
                self.sound.play_sfx(self.sound.pipe)

    def bounce(self):
        self.traits["bounceTrait"].jump = True

    def killEntity(self, ent):
        if ent.__class__.__name__ != "Koopa":
            ent.alive = False
        else:
            ent.timer = 0
            ent.leftrightTrait.speed = 1
            ent.alive = True
            ent.active = False
            ent.bouncing = False
        self.dashboard.points += 100

    def gameOver(self):
        srf = pygame.Surface((640, 480))
        srf.set_colorkey((255, 255, 255), pygame.RLEACCEL)
        srf.set_alpha(128)
        self.sound.music_channel.stop()
        self.sound.music_channel.play(self.sound.death)

        for i in range(500, 20, -2):
            srf.fill((0, 0, 0))
            pygame.draw.circle(
                srf,
                (255, 255, 255),
                (int(self.camera.x + self.rect.x) + 16, self.rect.y + 16),
                i,
            )
            self.screen.blit(srf, (0, 0))
            pygame.display.update()
            self.input.checkForInput()
        while self.sound.music_channel.get_busy():
            pygame.display.update()
            self.input.checkForInput()
        self.restart = True

    def win(self):
        srf = pygame.Surface((640, 480))
        srf.set_colorkey((255, 255, 255), pygame.RLEACCEL)
        srf.set_alpha(128)
        self.sound.music_channel.stop()
        self.sound.music_channel.play(self.sound.succeed)

        for i in range(500, 20, -2):
            srf.fill((255, 255, 0))
            pygame.draw.circle(
                srf,
                (255, 255, 255),
                (int(self.camera.x + self.rect.x) + 16, self.rect.y + 16),
                i,
            )
            self.screen.blit(srf, (0, 0))
            pygame.display.update()

            self.dashboard.drawText("Level Completed", self.windowSize[0]/3, self.windowSize[1]/2, 20)

            self.input.checkForInput()
        while self.sound.music_channel.get_busy():
            pygame.display.update()
            self.input.checkForInput()
        self.restart = True

    def loseLife(self):
        self.dashboard.life -= 1
        self.pre_loseLife = self.time
        self.sound.music_channel.stop()
        self.sound.music_channel.play(self.sound.lose_life)


    def getPos(self):
        return self.camera.x + self.rect.x, self.rect.y

    def setPos(self, x, y):
        self.rect.x = x
        self.rect.y = y
        
    def powerup(self, powerupID):
        if self.powerUpState == 0:
            if powerupID == 1:
                self.powerUpState = 1
                self.traits['goTrait'].updateAnimation(self.bigAnimation)
                if self.menu.choosenPlayer == "Mario":
                    self.rect = pygame.Rect(self.rect.x, self.rect.y-32, 32, 64)
                else:
                    self.rect = pygame.Rect(self.rect.x, self.rect.y-32, self.bigimage.get_size()[0], 64)
                self.invincibilityFrames = 20

    def shoot(self):
        bullet = Bullet(self.rect.right, self.rect.centery, self.rect.width, self.lr_direction, self.screen, self.camera, self.levelObj, self.dashboard)
        self.bullets.add(bullet)

    def fence(self):
        sword = Sword(self.rect.right, self.rect.centery, self.rect.width, self.lr_direction, self.screen, self.camera, self.levelObj, self.dashboard)
        self.swords.add(sword)
    