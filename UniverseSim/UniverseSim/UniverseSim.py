import pygame
import numpy as np
from random import randint
import math
clock = pygame.time.Clock()

pygame.init()
gameExit = False
FPS = 200

w = pygame.display.Info().current_w
h = pygame.display.Info().current_h

x_offset = w/2
y_offset = h/2

N_fragment = 10
max_ratio = 31536000

#1920x1080
#screen = pygame.display.set_mode((100,100))
screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
font = pygame.font.SysFont('Calibri Body', 50)

bg = pygame.image.load("bg.jpg").convert()

playButton = pygame.image.load("playButton.jpg").convert()
pauseButton = pygame.image.load("pauseButton.jpg").convert()
resetButton = pygame.image.load("resetButton.jpg").convert()
deleteButton = pygame.image.load("deleteButton.jpg").convert()

border1 = pygame.image.load("border1.jpg").convert()
banner = pygame.image.load("banner.png").convert_alpha()
banner_x = math.ceil((1920-w)/2)

au = 1.49598 * (10 ** 11)
ly = 9.5 * (10 ** 15)
pc = 3.1 * (10 ** 16)
G = 6.67 * (10 ** -11)

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)

distanceRatio = 10**8
dR = 10**5
timeRatio = 1

drag = False
pause = False

class Button:
    def __init__(self,x,y,w,h,image,onScreen):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.hitbox = pygame.Rect(x,y,w,h)
        self.image = image
        self.onScreen = onScreen

    def clicked(self,pos):
        if self.hitbox.collidepoint(pos):
            return True
        return False       

    def draw(self):
        if self.onScreen:
            screen.blit(self.image,[self.x,self.y])

class startStop(Button):
    def function(self):
        if self.image == playButton:
            pause = False
            self.image = pauseButton
        else:
            pause = True
            self.image = playButton
        return Masses, Fragments, pause
startStopButton = startStop(45,43,84,84,pauseButton,True)

class delete(Button):
    def function(self):
        return [], [], pause
deleteButton = delete(245,43,84,84,deleteButton,True)

class reset(Button):
    def function(self):
        Masses, Fragments = init()
        return Masses, Fragments, pause
resetButton = reset(145,43,84,84,resetButton,True)

class speed(Button):
    def __init__(self,x,y,r):      
        self.y = y
        self.r = r
        self.onScreen = True
        self.clickedOn = False
        self.update(x)

    def draw(self):
        pygame.draw.circle(screen,BLACK,(self.x,self.y),self.r)

    def update(self,x):
        self.x = x
        self.hitbox = pygame.Rect(self.x - self.r,self.y - self.r, self.r * 2, self.r * 2)

    def getTime(self,secs):
        if secs < 60:
            div = 1
            unit = ' second'
        elif secs < 3600:
            div = 60
            unit = ' minute'
        elif secs < 86400:
            div = 3600
            unit = ' hour'
        elif secs < 604800:
            div = 86400
            unit = ' day'
        elif secs < 2628000:
            div = 604800
            unit = ' week'
        else:
            div = 2628000
            unit = ' month'
        val = int(round(secs/div,0))
        if val != 1:
            unit += 's'
        return val, unit

    def changeValue(self,x):
        if 350 <= x <= 375:
            return 0, 0, ' seconds'
        if 375 < x <= 675:
            self.update(x)
            newRatio = math.ceil(max_ratio * (x - 375)/300)
            val, unit = self.getTime(newRatio)
            return newRatio, val, unit   
        val, unit = self.getTime(timeRatio)
        return timeRatio, val, unit

    def function(self):
        self.clickedOn = True
        return Masses, Fragments, pause
speedButton = speed(375,85,10)

Buttons = [startStopButton,deleteButton,resetButton,speedButton]

class PointMass: 
    def __init__(self,r,mass,x,y,Vx,Vy):
        self.r = r
        self.mass = mass
        self.x = x
        self.y = y
        self.Vx = Vx
        self.Vy = Vy
        self.hitbox = pygame.Rect((self.x - (0.85 * self.r)) / dR,(self.y - (0.85 * self.r)) / dR,(1.7 * self.r) / dR,(1.7 * self.r) / dR)
        self.xpositions = []
        self.ypositions = []

    def V(self):
        return np.sqrt(self.Vx**2 + self.Vy**2)
        
    def checkCollide(self):
        for x in Masses:
            if x != self:
                if pygame.Rect.colliderect(self.hitbox,x.hitbox):
                    other = self
                    self.collide(x)                   
                    x.collide(other)
                    break

    def collide(self,x):
        dx = x.x - self.x
        dy = x.y - self.y
        collisionFactor = abs(((self.Vx * dx) + (self.Vy * dy))/(self.V() * getDist(self,x)))
        momentumFactor = collisionFactor * (x.mass/self.mass) * (x.V()/self.V())
        N = math.ceil(N_fragment * momentumFactor)
        if N <= 4:
            N = 4
        elif N >= 20:
            N = 20
        r = self.r / N
        m = self.mass / N
        print('\nCOLLISION FACTOR:',collisionFactor)
        print('MOMENTUM FACTOR:',momentumFactor,'\n\n')
        if momentumFactor >= 0.5:
            Masses.remove(self)
        for i in range(N):
            angle = randint(-30,30) * (np.pi/180)
            Vx_f = math.ceil(self.Vx * np.cos(angle) - self.Vy * np.sin(angle))
            Vy_f = math.ceil(self.Vy * np.cos(angle) + self.Vx * np.sin(angle))
            var_x = math.ceil(0.1 * abs(Vx_f))
            var_y = math.ceil(0.1 * abs(Vy_f))
            Fragments.append(Fragment(self.x + Vx_f,self.y + Vy_f,randint(Vx_f - var_x,Vx_f + var_x),randint(Vy_f - var_y,Vy_f + var_y),m,r * 2))

    def draw(self):      
        if (self.r/distanceRatio < 1):
            pygame.draw.circle(screen,WHITE,getLocalPos(self.x,self.y),1)
        else:
            pygame.draw.circle(screen,WHITE,getLocalPos(self.x,self.y),self.r/distanceRatio)
        #pygame.draw.rect(screen,RED,self.hitbox)

    def draw_trail(self):       
        power = 2 - self.V()/25000
        colour_val = 1/(1+3**(power))
        colour = (255 * colour_val,0,255 * (1-colour_val))
        if len(self.xpositions) > 1:
            pygame.draw.lines(screen,colour, False, list(map(getLocalPos,self.xpositions,self.ypositions)),2)             

    def updateTrail(self):
        self.xpositions.append(self.x)
        self.ypositions.append(self.y)

        lim = math.floor((3153600/timeRatio)*FPS)
        length = len(self.xpositions)
        if length > lim:
            del self.xpositions[0:length - lim + 1]
            del self.ypositions[0:length - lim + 1]
        return lim

    def move(self,angle,a,dirx,diry):
        self.Vx += (a / FPS) * abs(np.cos(angle)) * dirx * timeRatio
        self.Vy += (a / FPS) * abs(np.sin(angle)) * diry * timeRatio
        self.x += (self.Vx / FPS) * timeRatio
        self.y += (self.Vy / FPS) * timeRatio        
        #self.hitbox = pygame.Rect(self.x - (0.85 * self.r),self.y - (0.85 * self.r),1.7 * self.r,1.7 * self.r)
        self.hitbox = pygame.Rect((self.x - (0.85 * self.r)) / dR,(self.y - (0.85 * self.r)) / dR,(1.7 * self.r) / dR,(1.7 * self.r) / dR)

    def getForce(self):
        rFx = 0
        rFy = 0
        for m in Masses:
            if m != self:
                dx = (self.x - m.x)
                dy = (self.y - m.y)
                if (dx + dy) != 0:
                    F = (G * self.mass * m.mass) / (dx**2 + dy**2)
                if dx == 0:
                    angle = 2 * np.pi
                else:
                    angle = np.arctan(dy/dx)
                dirx,diry = self.getDirection(self.x,m.x,self.y,m.y)
                rFx += F * abs(np.cos(angle)) * dirx
                rFy += F * abs(np.sin(angle)) * diry
        rF = np.sqrt(rFx**2 + rFy**2)
        dirx,diry = self.getDirection(0,rFx,0,rFy)
        if rFx == 0:
            angle = 2 * np.pi
        else:
            angle = np.arctan(rFy/rFx)
        a = rF / self.mass
        self.move(angle,a,dirx,diry)

    def getDirection(self,Ax,Bx,Ay,By):
        if Ax > Bx:
            dirx = -1
        else:
            dirx = 1
        if Ay > By:
            diry = -1
        else:
            diry = 1
        return dirx,diry

class Fragment(PointMass):
    def __init__(self,x,y,Vx,Vy,mass,r):
        self.r = r
        self.mass = mass
        self.lifetime = randint(5 * FPS,10 * FPS)
        self.x = x
        self.y = y
        self.Vx = Vx
        self.Vy = Vy

    def updateLife(self):
        if self.lifetime == 1:
            Fragments.remove(self)
        self.lifetime -= 1

def displayText(text,pos):
        textsurface = font.render(text, True, WHITE)
        screen.blit(textsurface, pos)

def getDist(m1,m2):
    return np.sqrt((m2.x-m1.x)**2 + (m2.y-m1.y)**2)

def getLocalPos(x,y):
    return x_offset + x/distanceRatio,y_offset + y/-distanceRatio

def getGlobalPos(x,y):
    return -distanceRatio * (x_offset - w/2 - x), distanceRatio * (y_offset - h/2 - y)

def init():
    Sun = PointMass(6.96*10**8,1.989*10**30,
               0,       #x
               0,       #y
               0,       #Vx
               0)       #Vy

    Mercury = PointMass(2.44*10**6,3.285*10**23,
                        0.387 * au,
                        0,
                        0,
                        47879)

    Venus = PointMass(6.05*10**6,4.867*10**24,
                   0.723 * au,
                   0,
                   0,
                   35025)

    Earth = PointMass(6.37*10**6,5.97*10**24,
                   au,
                   0,
                   0,
                   29800)

    Mars = PointMass(3.39*10**6,6.390*10**23,
                     1.523 * au,
                     0,
                     0,
                     24135)

    Jupiter = PointMass(6.99*10**7,1.898 * 10**27,
                        5.203 * au,
                        0,
                        0,
                        13060)

    Saturn = PointMass(6.03*10**7,5.683*10**26,
                       9.537 * au,
                       0,
                       0,
                       9646)

    Uranus = PointMass(2.54*10**7,8.681*10**25,
                       19.189 * au,
                       0,
                       0,
                       6800)

    Neptune = PointMass(2.41*10**7,1.024*10**26,
                        30.070 * au,
                        0,
                        0,
                        5432)
    return [Sun,Mercury,Venus,Earth,Mars,Jupiter,Saturn,Uranus,Neptune],[]

Masses,Fragments = init()

while not gameExit:
    screen.blit(bg,[0,0])

    for x in Masses:   
        x.draw_trail()
        x.draw()
        if not pause and timeRatio > 0:    
            x.updateTrail()            
            x.getForce()  
            x.checkCollide()
                         
    for x in Fragments:
        x.draw()     
        if not pause and timeRatio > 0:
            x.getForce()
            x.updateLife()

    if drag:
        newRef = pygame.mouse.get_pos()
        dx = (newRef[0] - oldRef[0])
        dy = (newRef[1] - oldRef[1])
        x_offset += dx
        y_offset += dy
        oldRef = newRef  
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                gameExit = True           
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            dx = mouse_pos[0] - w/2
            dy = mouse_pos[1] - h/2
            if event.button == 1: #Left click
                oldRef = mouse_pos
                drag = True
                for x in Buttons:
                    if x.onScreen:
                        if x.clicked(mouse_pos):
                            Masses,Fragments,pause = x.function()
                            drag = False
                
            elif event.button == 3:
                pos = getGlobalPos(dx,dy)
                Masses.append(PointMass(6.96*10**8,10**30,pos[0],pos[1],-15000,0))
            elif event.button == 4: #Zoom in
                distanceRatio /= 1.1
                x_offset = (x_offset * 1.1) - (0.1 * dx) - (0.05 * w)
                y_offset = (y_offset * 1.1) - (0.1 * dy) - (0.05 * h)
            elif event.button == 5: #Zoom out
                distanceRatio *= 1.1
                x_offset = (x_offset / 1.1) + (dx / 11) + (w / 22)
                y_offset = (y_offset / 1.1) + (dy / 11) + (h / 22)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: #Left click
                drag = False
                speedButton.clickedOn = False

    if speedButton.clickedOn:
        timeRatio, val, unit = speedButton.changeValue(pygame.mouse.get_pos()[0])
        text = str(val) + unit + ' /s'
        displayText(text,(750,75))
                
    screen.blit(border1,[25,25])
    screen.blit(banner,[banner_x,h-80])
    for x in Buttons:
        x.draw()


pygame.display.update()
clock.tick(FPS)

