import pygame
import time 
import math

pygame.init()

width=640
height=480
pygame.display.set_caption('Quick Start')
window_surface = pygame.display.set_mode((640, 480))
background = pygame.Surface((640, 480))
background.fill(pygame.Color('#000000'))

is_running = True


#map here
map=[
 [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
 [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
 [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
 [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
 [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
 [1,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
 [1,1,1,0,1,1,0,1,1,1,0,0,1,1,1,0,0,0,0,0,0,1],
 [1,1,0,1,0,1,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,1],
 [1,1,0,0,0,1,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,1],
 [1,1,0,0,0,1,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,1],
 [1,1,0,0,0,1,0,1,1,1,0,0,0,1,0,0,0,0,0,0,0,1],
 [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]


#function to draw specific pixel with specified height
def drawpixel(x,y,height=1, color=(0,255,0)):
  startheight= int(math.floor(240-height/2))
  if startheight<0:
    startheight=0
  for i in range(height):
    pygame.draw.rect(background, color, pygame.Rect(x, startheight+i, 1, 1))
    if startheight+i>480:
      break
    
class player:
  def __init__(self):
    self.x=1
    self.y=1
    self.fov = 120
    self.viewdir = 90
    self.movespeed = 0.2
    self.rad=10

player1= player()

#clamping function
def clamp(val,min,max):
  if val<min:
    return min
  elif val>max:
    return max
  return val
  
class ray:
  def __init__(self,angle):
    self.angle = angle
    
    self.x = player1.x
    self.y = player1.y
    
    self.iterx = math.cos(math.radians(self.angle)) / 64
    self.itery = math.sin(math.radians(self.angle)) / 64
    
    self.val = map[math.floor(self.y)][math.floor(self.x)]
    
incre=player1.fov/width

def raycast():
  rays = ray((player1.viewdir - player1.fov/2))
  for i in range(width):
    #rays go until they hit a wall on the map
    while rays.val == 0:
      rays.x = rays.x + rays.iterx
      rays.y = rays.y + rays.itery
      rays.val = map[math.floor(rays.y)][math.floor(rays.x)]
    
    distance=math.sqrt(math.pow(player1.x - rays.x, 2) + math.pow(player1.y - rays.y, 2))
    wallheight=math.floor(240/distance)
    
    drawpixel(i,0,wallheight,(0,clamp(255/distance,1,255),0))
    
    rays = ray(rays.angle + incre)

moveforward=False
movebackward=False
strafeleft=False
straferight=False
rotright=False
rotleft=False

def movement():
    #just smmooth movement
  if moveforward==True:
    playerCos = math.cos(math.radians(player1.viewdir)) * player1.movespeed
    playerSin = math.sin(math.radians(player1.viewdir)) * player1.movespeed
    newX = player1.x + (playerCos*3)
    newY = player1.y + (playerSin*3)
    if map[math.floor(player1.y)][math.floor(newX)]==0:
      player1. x = newX - playerCos*2
    if map[math.floor(newY)][math.floor(player1.x)]==0:
      player1.y = newY - playerSin*2
  if movebackward==True:
    playerCos = math.cos(math.radians(player1.viewdir)) * player1.movespeed
    playerSin = math.sin(math.radians(player1.viewdir)) * player1.movespeed
    newX = player1.x - playerCos*3
    newY = player1.y - playerSin*3
    if map[math.floor(player1.y)][math.floor(newX)]==0:
      player1. x = newX + playerCos*2
    if map[math.floor(newY)][math.floor(player1.x)]==0:
      player1.y = newY + playerSin*2
    
  if strafeleft==True:
    playerCos = math.cos(math.radians(player1.viewdir-90)) * player1.movespeed
    playerSin = math.sin(math.radians(player1.viewdir-90)) * player1.movespeed
    newX = player1.x + (playerCos*3)
    newY = player1.y + (playerSin*3)
    if map[math.floor(player1.y)][math.floor(newX)]==0:
      player1. x = newX - playerCos*2
    if map[math.floor(newY)][math.floor(player1.x)]==0:
      player1.y = newY - playerSin*2
    
  if straferight==True:
    playerCos = math.cos(math.radians(player1.viewdir+90)) * player1.movespeed
    playerSin = math.sin(math.radians(player1.viewdir+90)) * player1.movespeed
    newX = player1.x + (playerCos*3)
    newY = player1.y + (playerSin*3)
    if map[math.floor(player1.y)][math.floor(newX)]==0:
      player1. x = newX - playerCos*2
    if map[math.floor(newY)][math.floor(player1.x)]==0:
      player1.y = newY - playerSin*2
      
  if rotright==True:
    player1.viewdir= player1.viewdir+5
    if player1.viewdir<0:
      player1.viewdir=355
  if rotleft==True:
    player1.viewdir= player1.viewdir-5
    if player1.viewdir>360:
      player1.viewdir=5

  
  
while is_running:
  window_surface.blit(background, (0, 0))
  background.fill(pygame.Color('#000000'))
  for event in pygame.event.get():
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_w:
        moveforward=True
      if event.key == pygame.K_s:
        movebackward=True
      if event.key == pygame.K_a:
        strafeleft=True
      if event.key == pygame.K_d:
        straferight=True
      if event.key == pygame.K_j:
        rotleft=True
      if event.key == pygame.K_l:
        rotright=True
          
    if event.type == pygame.KEYUP:
      if event.key==pygame.K_w:
        moveforward=False
      if event.key==pygame.K_s:
        movebackward=False
      if event.key == pygame.K_a:
        strafeleft=False
      if event.key == pygame.K_d:
        straferight=False
      if event.key == pygame.K_j:
        rotleft=False
      if event.key == pygame.K_l:
        rotright=False
        
  movement()
  raycast()
  pygame.display.update()
  time.sleep(0.03)

