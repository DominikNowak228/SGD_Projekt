import pygame
import sys
import random
from pygame.locals import *

DISPLAYWIDTH = 640
DISPLAYHEIGHT = 480
FPS = 60

BACKGROUND_MUSIC = "Background.mp3"
PADDLE_SFX = "Paddle.ogg"
BRICK_1 = "brick_1.ogg"
BRICK_2 = "brick_2.ogg"
BRICK_3 = "brick_3.ogg"

BRICKS_SFX = [BRICK_1,BRICK_2,BRICK_3]


## COLORS ##
#            R    G    B
GRAY     = (100, 100, 100)
NAVYBLUE = ( 60,  60, 100)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 255, 255)
BLACK    = (  0,   0,   0)
COMBLUE  = (233, 232, 255)

BLOCK_COLORS = [RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN]

BGCOLOR = BLACK
BLOCKGAP = 2
BLOCKWIDTH = 62
BLOCKHEIGHT = 25
ARRAYWIDTH = 10
ARRAYHEIGHT = 5
PADDLEWIDTH = 100
PADDLEHEIGHT = 10
BALLRADIUS = 20
BALLCOLOR = WHITE
BLOCK = 'block'
BALL = 'ball'
PADDLE = 'paddle'
BALLSPEED = 10


class Block(pygame.sprite.Sprite):

    def __init__(self):
        self.blockWidth = BLOCKWIDTH
        self.blockHeight = BLOCKHEIGHT
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((self.blockWidth, self.blockHeight))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.name = BLOCK



class Ball(pygame.sprite.Sprite):
    def __init__(self, displaySurf):
        pygame.sprite.Sprite.__init__(self)
        self.name = BALL
        self.moving = False
        self.image = pygame.Surface((15, 15))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.vectorx = BALLSPEED
        self.vectory = BALLSPEED * -1
        self.score = 0


    def update(self, mousex, blocks, paddle, *args):
        if self.moving == False:
            self.rect.centerx = mousex

        else:
            self.rect.y += self.vectory

            hitGroup = pygame.sprite.Group(paddle, blocks)

            spriteHitList = pygame.sprite.spritecollide(self, hitGroup, False)
            if len(spriteHitList) > 0:
                for sprite in spriteHitList:
                    if sprite.name == BLOCK:
                        sprite.kill()
                        self.score += 1
                        if hasattr(args[0], 'brick_sfx'):
                            random.choice(args[0].brick_sfx).play()

                    elif sprite.name == PADDLE:
                        if hasattr(args[0], 'paddle_sfx'):
                            args[0].paddle_sfx.play()
                self.vectory *= -1
                self.rect.y += self.vectory

            self.rect.x += self.vectorx

            blockHitList = pygame.sprite.spritecollide(self, blocks, True)

            if len(blockHitList) > 0:
                self.vectorx *= -1
                self.score += 1



            if self.rect.right > DISPLAYWIDTH:
                self.vectorx *= -1
                self.rect.right = DISPLAYWIDTH

            elif self.rect.left < 0:
                self.vectorx *= -1
                self.rect.left = 0

            if self.rect.top < 0:
                self.vectory *= -1
                self.rect.top = 0

            if self.rect.top > DISPLAYHEIGHT:
                self.moving = False
                args[0].gameOver = True

            if len(blocks) == 0:
                self.moving = False
                args[0].levelComplete = True


class Paddle(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((PADDLEWIDTH, PADDLEHEIGHT))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.name = PADDLE

    def update(self, mousex, *args):
        if self.rect.x >= 0 and self.rect.right <= DISPLAYWIDTH:
            self.rect.centerx = mousex

        if self.rect.x < 0:
            self.rect.x = 0

        elif self.rect.right > DISPLAYWIDTH:
            self.rect.right = DISPLAYWIDTH


class Score(object):
    def __init__(self):
        self.score = 0
        self.font = pygame.font.SysFont('Helvetica', 25)
        self.render = self.font.render('Score: ' + str(self.score), True, WHITE, BLACK)
        self.rect = self.render.get_rect()
        self.rect.topleft = (10, 10)





class App(object):
    def __init__(self):
        pygame.init()
        self.displaySurf, self.displayRect = self.makeScreen()
        self.mousex = 0
        self.blocks = self.createBlocks()
        self.paddle = self.createPaddle()
        self.ball = self.createBall()
        self.score = Score()
        self.clock = pygame.time.Clock()
        self.gameOver = False
        self.levelComplete = False
        self.paused = False
        self.music_on = True

        self.allSprites = pygame.sprite.Group(self.blocks, self.paddle, self.ball)

        pygame.mixer.music.load(BACKGROUND_MUSIC)
        pygame.mixer.music.set_volume(0.05)
        pygame.mixer.music.play(-1)

        self.paddle_sfx = pygame.mixer.Sound(PADDLE_SFX)
        self.paddle_sfx.set_volume(0.5)

        self.brick_sfx = [pygame.mixer.Sound(sfx) for sfx in BRICKS_SFX]
        for sound in self.brick_sfx:
            sound.set_volume(0.5)

    def updateScore(self):
        self.score.score = self.ball.score
        self.score.render = self.score.font.render('Score: ' + str(self.score.score), True, WHITE, BLACK)
        self.score.rect = self.score.render.get_rect()
        self.score.rect.topleft = (10, 10)



    def makeScreen(self):
        pygame.display.set_caption('Arkanoid')
        displaySurf = pygame.display.set_mode((DISPLAYWIDTH, DISPLAYHEIGHT))
        displayRect = displaySurf.get_rect()
        displaySurf.fill(BGCOLOR)
        displaySurf.convert()

        return displaySurf, displayRect


    def createBall(self):
        ball = Ball(self.displaySurf)
        ball.rect.centerx = self.paddle.rect.centerx
        ball.rect.bottom = self.paddle.rect.top

        return ball


    def createPaddle(self):
        paddle = Paddle()
        paddle.rect.centerx = self.displayRect.centerx
        paddle.rect.bottom = self.displayRect.bottom

        return paddle

    def createBlocks(self):
        blocks = pygame.sprite.Group()

        total_rows = 6
        for row in range(total_rows):
            blocks_in_row = ARRAYWIDTH - row

            total_width = blocks_in_row * (BLOCKWIDTH + BLOCKGAP)
            start_x = (DISPLAYWIDTH - total_width) // 2

            for i in range(blocks_in_row):
                block = Block()
                block.rect.x = start_x + i * (BLOCKWIDTH + BLOCKGAP)
                block.rect.y = 50 + row * (BLOCKHEIGHT + BLOCKGAP)
                block.color = self.setBlockColor(block, row, i)
                block.image.fill(block.color)
                blocks.add(block)

        return blocks



    def setBlockColor(self, block, row, column):
        return random.choice(BLOCK_COLORS)

    def restartGame(self):
        self.blocks = self.createBlocks()
        self.paddle = self.createPaddle()
        self.ball = self.createBall()
        self.score = Score()
        self.allSprites = pygame.sprite.Group(self.blocks, self.paddle, self.ball)
        self.mousex = self.displayRect.centerx
        self.gameOver = False
        self.levelComplete = False

    def checkInput(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.terminate()

            if event.type == MOUSEMOTION:
                self.mousex = event.pos[0]

            elif event.type == KEYUP:
                if event.key == K_SPACE and not (self.gameOver or self.levelComplete):
                    self.ball.moving = True
                elif event.key == K_r and (self.gameOver or self.levelComplete):
                    self.restartGame()
                elif event.key == K_p:
                    self.paused = not self.paused
                elif event.key == K_ESCAPE:
                    self.terminate()
                elif event.key == K_m:
                    self.toggleMusic()

    def terminate(self):
        pygame.quit()
        sys.exit()

    def toggleMusic(self):
        if self.music_on:
            pygame.mixer.music.pause()
            self.music_on = False
        else:
            pygame.mixer.music.unpause()
            self.music_on = True

    def drawGameOverScreen(self):
        font = pygame.font.SysFont('Helvetica', 36)
        gameOverText = font.render('Game Over! Press R to Restart', True, RED, BLACK)
        gameOverRect = gameOverText.get_rect(center=(DISPLAYWIDTH // 2, DISPLAYHEIGHT // 2))

        scoreText = font.render('Final Score: ' + str(self.score.score), True, WHITE, BLACK)
        scoreRect = scoreText.get_rect(center=(DISPLAYWIDTH // 2, DISPLAYHEIGHT // 2 + 50))

        self.displaySurf.blit(gameOverText, gameOverRect)
        self.displaySurf.blit(scoreText, scoreRect)

    def drawWinScreen(self):
        font = pygame.font.SysFont('Helvetica', 36)
        winText = font.render('You Win! Press R to Restart', True, GREEN, BLACK)
        winRect = winText.get_rect(center=(DISPLAYWIDTH // 2, DISPLAYHEIGHT // 2))

        scoreText = font.render('Final Score: ' + str(self.score.score), True, WHITE, BLACK)
        scoreRect = scoreText.get_rect(center=(DISPLAYWIDTH // 2, DISPLAYHEIGHT // 2 + 50))

        self.displaySurf.blit(winText, winRect)
        self.displaySurf.blit(scoreText, scoreRect)

    def drawPauseScreen(self):
        font = pygame.font.SysFont('Helvetica', 36)
        pauseText = font.render('Paused - Press P to Resume', True, WHITE, BLACK)
        pauseRect = pauseText.get_rect(center=(DISPLAYWIDTH // 2, DISPLAYHEIGHT // 2))
        self.displaySurf.blit(pauseText, pauseRect)

    def mainLoop(self):
        while True:
            self.displaySurf.fill(BGCOLOR)
            self.updateScore()
            self.displaySurf.blit(self.score.render, self.score.rect)

            if not (self.gameOver or self.levelComplete or self.paused):
                self.allSprites.update(self.mousex, self.blocks, self.paddle, self)

            self.allSprites.draw(self.displaySurf)

            if self.levelComplete:
                self.drawWinScreen()
            elif self.gameOver:
                self.drawGameOverScreen()
            elif self.paused:
                self.drawPauseScreen()

            pygame.display.update()
            self.checkInput()
            self.clock.tick(FPS)


if __name__ == '__main__':

    runGame = App()
    runGame.mainLoop()
