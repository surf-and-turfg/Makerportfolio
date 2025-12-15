import pygame
import numpy
import math
import time
import copy
pygame.init()

class player:
  def __init__(self):
    self.pos = numpy.array((0,4,0,1))
    self.fovx = 120
    self.fovy = 90
    self.viewdirx = 0
    self.viewdiry = 0
   

f = 2000
width = 640
height = 640
n = 0.1
pygame.display.set_caption('Quick Start')
window_surface = pygame.display.set_mode((width, height))

background = pygame.Surface((width, height))
background.fill(pygame.Color('#000000'))
p = player()

class vertex:
  def __init__(self,position):
    self.modelpos = position
    self.processedpos = numpy.array((0,0,0,1))
    processed = 1



class polygon:
  def __init__(self):
    self.verticies = []
    self.pointstorender = []
  def set_pos(self,newpos):
    for i in range(0,len(self.verticies)):
      self.verticies[i].processedpos = self.verticies[i].modelpos + newpos
     
  def render_poly(self):
    self.pointstorender = []
    for i in range(0,len(self.verticies)):
     
        #ttranslate the vertex position based on the player pos
        newpos = self.verticies[i].processedpos- p.pos
       
        negatez = numpy.array([[1,0,0,0],
                              [0,1,0,0],
                              [0,0,-1,0],
                              [0,0,0,1],])
                             
        newpos= numpy.array((newpos[0],newpos[1],newpos[2], 1))
        newpos = newpos.dot(negatez)
        #create rotation matrices
        rx = numpy.array([[1, 0, 0, 0],
                          [0, math.cos(math.radians(p.viewdirx)), math.sin(math.radians(p.viewdirx)), 0],
                          [0, -math.sin(math.radians(p.viewdirx)), math.cos(math.radians(p.viewdirx)), 0],
                          [0, 0, 0, 1]])
       
        ry = numpy.array([[math.cos(math.radians(p.viewdiry)), 0, math.sin(math.radians(p.viewdiry)), 0],
                          [0, 1, 0, 0],
                          [-math.sin(math.radians(p.viewdiry)), 0, math.cos(math.radians(p.viewdiry)), 0],
                          [0, 0, 0, 1]])
       
        #combine the rot matrix
        r = numpy.dot(ry, rx)
       
        #apply rot
        newpos = newpos.dot(r)
        #project
        s = 1 / (math.tan(math.radians(p.fovx / 2)))
        per = numpy.array([[s, 0, 0, 0],
                           [0, s, 0, 0],
                           [0, 0, -f / (f - n), -1],
                           [0, 0, (-f * n) / (f - n), 0]])
        newpos = numpy.dot(newpos,per)
        w = -newpos[3]
        newpos = newpos/w
        x = 320*newpos[0] + 320
        y = 320*newpos[1] + 320
        self.pointstorender.append((x,y,w))
        #pygame.draw.circle(background,(255,0,0),(x,y),10)
    #find if the vertices are behind the camerea
    if (self.pointstorender[0][2] <= 0 and self.pointstorender[len(self.pointstorender)-1][2] <= 0):
      pygame.draw.line(background,(0,255,0),self.pointstorender[0][:2],self.pointstorender[len(self.pointstorender)-1][:2])
    for i in range(0, len(self.pointstorender)-1):
      if (self.pointstorender[i][2] <= 0 and self.pointstorender[i+1][2] <= 0):
        pygame.draw.line(background,(0,255,0),self.pointstorender[i][:2],self.pointstorender[i+1][:2])
class model:
  def __init__(self):
    self.polygons = []
    self.modelpos = numpy.array((0,0,0))
  def set_pos(self,newpos):
    for i in self.polygons:
      i.set_pos(newpos)
  def render(self):
    for i in self.polygons:
      i.render_poly()
 

is_running = True

#stupid manual insertion
cubefaceFront = polygon()
cubefaceFront.verticies.append(vertex(numpy.array((0,3,0,1))))
cubefaceFront.verticies.append(vertex(numpy.array((3,3,0,1))))
cubefaceFront.verticies.append(vertex(numpy.array((3,6,0,1))))
cubefaceFront.verticies.append(vertex(numpy.array((0,6,0,1))))

cubefaceBack = polygon()
cubefaceBack.verticies.append(vertex(numpy.array((0,3,3,1))))
cubefaceBack.verticies.append(vertex(numpy.array((3,3,3,1))))
cubefaceBack.verticies.append(vertex(numpy.array((3,6,3,1))))
cubefaceBack.verticies.append(vertex(numpy.array((0,6,3,1))))

cubefaceRight = polygon()
cubefaceRight.verticies.append(vertex(numpy.array((0,3,0,1))))
cubefaceRight.verticies.append(vertex(numpy.array((0,6,0,1))))
cubefaceRight.verticies.append(vertex(numpy.array((0,6,3,1))))
cubefaceRight.verticies.append(vertex(numpy.array((0,3,3,1))))

cubefaceLeft = polygon()
cubefaceLeft.verticies.append(vertex(numpy.array((3,3,0,1))))
cubefaceLeft.verticies.append(vertex(numpy.array((3,6,0,1))))
cubefaceLeft.verticies.append(vertex(numpy.array((3,6,3,1))))
cubefaceLeft.verticies.append(vertex(numpy.array((3,3,3,1))))

star = polygon()
star.verticies.append(vertex(numpy.array((2,0,0,1))))
star.verticies.append(vertex(numpy.array((1,2.5,0,1))))
star.verticies.append(vertex(numpy.array((2,5,0,1))))
star.verticies.append(vertex(numpy.array((0.5,4,0,1))))
star.verticies.append(vertex(numpy.array((0,6,0,1))))
star.verticies.append(vertex(numpy.array((-0.5,4,0,1))))
star.verticies.append(vertex(numpy.array((-2,5,0,1))))
star.verticies.append(vertex(numpy.array((-1,2.5,0,1))))
star.verticies.append(vertex(numpy.array((-2,0,0,1))))
star.verticies.append(vertex(numpy.array((0,2,0,1))))
starmodel = model()
starmodel.polygons.append(star)
starmodel.set_pos(numpy.array((0,2,10,1)))


cube = model()
cube.polygons.append(cubefaceFront)
cube.polygons.append(cubefaceBack)
cube.polygons.append(cubefaceRight)
cube.polygons.append(cubefaceLeft)
cube2 = copy.deepcopy(cube)
cube.set_pos(numpy.array((0,0,5,1)))
cube2.set_pos(numpy.array((5,5,5,1)))
print(starmodel.polygons[0].verticies[0].processedpos)

cube.render()


print(cube.polygons[0].verticies[0].processedpos)

flagw = False
flaga = False
flags = False
flagd = False
rotleft = False
rotright = False
rotdown = False
rotup = False

flydown = False
flyup = False
def move():
  if (flagw):
    playerCos = math.cos(math.radians(p.viewdiry-90))*0.1
    playerSin = math.sin(math.radians(p.viewdiry-90))*0.1
    newz = p.pos[2] - (playerSin)
    newx = p.pos[0] - (playerCos)
    p.pos = numpy.array((newx,p.pos[1],newz,1))
  if (flags):
    playerCos = math.cos(math.radians(p.viewdiry-90))*0.1
    playerSin = math.sin(math.radians(p.viewdiry-90))*0.1
    newz = p.pos[2] + (playerSin)
    newx = p.pos[0] + (playerCos)
    p.pos = numpy.array((newx,p.pos[1],newz,1))
  if (flaga):
    playerCos = math.cos(math.radians(p.viewdiry))*0.1
    playerSin = math.sin(math.radians(p.viewdiry))*0.1
    newz = p.pos[2] + (playerSin)
    newx = p.pos[0] + (playerCos)
    p.pos = numpy.array((newx,p.pos[1],newz,1))
  elif (flagd):
    playerCos = math.cos(math.radians(p.viewdiry))*0.1
    playerSin = math.sin(math.radians(p.viewdiry))*0.1
    newz = p.pos[2] - (playerSin)
    newx = p.pos[0] - (playerCos)
    p.pos = numpy.array((newx,p.pos[1],newz,1))
   
  if (rotleft):
    p.viewdiry-=1
  elif (rotright):
    p.viewdiry+=1
   
  if (rotdown):
    p.viewdirx+=1
  elif (rotup):
    p.viewdirx-=1
   
  if (flydown):
    p.pos = numpy.array((p.pos[0],p.pos[1]-0.1,p.pos[2],1))
  elif (flyup):
    p.pos = numpy.array((p.pos[0],p.pos[1]+0.1,p.pos[2],1)) 

while is_running:
  posold = p.pos
    
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      is_running = False
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE:
        is_running=False
      if event.key == pygame.K_w:
        flagw=True
      if event.key == pygame.K_s:
        flags=True
      if event.key == pygame.K_a:
        flaga=True
      if event.key == pygame.K_d:
        flagd=True
      if event.key == pygame.K_j:
        rotleft=True
      if event.key == pygame.K_l:
        rotright=True
      if event.key == pygame.K_i:
        rotup=True
      if event.key == pygame.K_k:
        rotdown=True
      if event.key == pygame.K_e:
        flyup=True
      if event.key == pygame.K_q:
        flydown=True
    if event.type == pygame.KEYUP:
      if event.key == pygame.K_w:
        flagw=False
      if event.key == pygame.K_s:
        flags=False
      if event.key == pygame.K_a:
        flaga=False
      if event.key == pygame.K_d:
        flagd=False
      if event.key == pygame.K_j:
        rotleft=False
      if event.key == pygame.K_l:
        rotright=False
      if event.key == pygame.K_i:
        rotup=False
      if event.key == pygame.K_k:
        rotdown=False
      if event.key == pygame.K_e:
        flyup=False
      if event.key == pygame.K_q:
        flydown=False 


  window_surface.blit(background, (0, 0))
  background.fill((0,0,0))
  move()
  cube.render()
  cube2.render()
  starmodel.render()
  time.sleep(0.01)
  pygame.display.update()


