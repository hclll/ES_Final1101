import pygame
from classes.Maths import Vec2D

class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, marioWidth, lr_direction, screen, camera, level, dashboard):
		pygame.sprite.Sprite.__init__(self)
		self.img = pygame.Surface((20,10))
		self.img.fill((0,0,0))
		
		self.rect = self.img.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.lr_direction = lr_direction
		self.marioWidth = marioWidth

		self.screen = screen
		self.camera = camera

		self.vel = Vec2D()
		self.vel.x = 10
		self.vel.y = 0
		self.level = level.level
		self.levelObj = level
		self.dashboard = dashboard

		self.count = 0

	def update(self):

		self.checkEntityCollision()
		self.OnCollisionWithTile()

		if self.lr_direction == -1:
			self.rect.x -= self.vel.x
			self.screen.blit(self.img, (self.rect.x - self.marioWidth + self.camera.x , self.rect.y))
		else:
			self.rect.x += self.vel.x
			self.screen.blit(self.img, (self.rect.x + self.camera.x , self.rect.y))

		if self.count > 50:
			self.kill()
		self.count += 1

	def checkEntityCollision(self):
		for ent in self.levelObj.entityList:
			if self.rect.colliderect(ent.rect):
				if ent.type == "Item":
					self._onCollisionWithItem(ent)
				elif ent.type == "Block":
					self._onCollisionWithBlock(ent)
				elif ent.type == "Mob":
					self._onCollisionWithMob(ent)

	def _onCollisionWithItem(self, item):
		pass

	def _onCollisionWithBlock(self, block):
		self.kill()

	def _onCollisionWithMob(self, mob):
		self.killEntity(mob)
		self.kill()

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

	def OnCollisionWithTile(self):
		try:
			rows = [
				self.level[self.getPosIndex().y],
				self.level[self.getPosIndex().y + 1],
				self.level[self.getPosIndex().y + 2],
			]
		except Exception:
			return
		for row in rows:
			tiles = row[self.getPosIndex().x : self.getPosIndex().x + 2]
			for tile in tiles:
				if tile.rect is not None:
					if self.rect.colliderect(tile.rect):
						self.kill()

	def getPosIndex(self):
		return Vec2D(self.rect.x // 32, self.rect.y // 32)

	def getPosIndexAsFloat(self):
		return Vec2D(self.rect.x / 32.0, self.rect.y / 32.0)
