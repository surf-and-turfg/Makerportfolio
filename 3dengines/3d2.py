import pygame
import numpy
import math
import time
import copy
pygame.init()

f = 2000
width = 640
height = 640
n = 0.1

#plane class for checking culling
class plane:
    def __init__(self):
        #constructs a plane based on the three coordinates
        self.x = 0
        self.y = 0
        self.z = 0
        self.d = 0
    def face(self,other):
       return numpy.dot(self.v,other.v)
    def construct(self,point1,point2,point3):
        #fins the normal of the plane
        self.v1 = point2[:3] - point1[:3]  
        self.v2 = point3[:3] - point1[:3]  
        self.crossprod = numpy.cross(self.v1,self.v2)
        self.d = numpy.dot(self.crossprod,point1[:3])
        self.x = self.crossprod[0]
        self.y = self.crossprod[1]
        self.z = self.crossprod[2]

def normalize(v):
    return v/numpy.linalg.norm(v)


class player:
  def __init__(self):
    self.pos = numpy.array((0,4,0,1))
    self.fovx = 120
    self.fovy = 90
    self.viewdirx = 0
    self.viewdiry = 0
    self.nearplane = plane()
    self.nearplane.x = 0
    self.nearplane.y = 0
    self.nearplane.z = 1
    self.nearplane.d = n
    self.viewvector= numpy.array((0,0,2000))
    self.originvector = numpy.array((0,0,2000))
  def update_planes(self):
      self.rx = numpy.array([[1, 0, 0],
                          [0, math.cos(math.radians(self.viewdirx)),-math.sin(math.radians(self.viewdirx))],
                          [0, math.sin(math.radians(self.viewdirx)), math.cos(math.radians(self.viewdirx))]])
       
      self.ry = numpy.array([[math.cos(math.radians(self.viewdiry)), 0, math.sin(math.radians(self.viewdiry))],
                          [0, 1, 0],
                          [-math.sin(math.radians(self.viewdiry)), 0, math.cos(math.radians(self.viewdiry))]])
      self.rx = numpy.linalg.inv(self.rx)
      self.ry = numpy.linalg.inv(self.ry)
      self.r = numpy.dot(self.ry,self.rx)
      self.viewvector = numpy.dot(self.originvector,self.r)

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


class fulstrum:
    def __init__(self):
        pass

class polygon:
  def __init__(self):
    self.verticies = []
    self.pointstorender = []
    self.maxx = numpy.array((0,0,0,1))
    self.maxy = numpy.array((0,0,0,1))
    self.maxz = numpy.array((0,0,0,1))
    self.randomass = numpy.array((0,0,0,1))
  def rotate(self, rotx, roty,rotz):
    for i in range(0,len(self.verticies)):
        self.rx = numpy.array([[1, 0, 0, 0],
                          [0, math.cos(math.radians(rotx)), math.sin(math.radians(rotx)), 0],
                          [0, -math.sin(math.radians(rotx)), math.cos(math.radians(rotx)), 0],
                          [0, 0, 0, 1]])
       
        self.ry = numpy.array([[math.cos(math.radians(roty)), 0, math.sin(math.radians(roty)), 0],
                          [0, 1, 0, 0],
                          [-math.sin(math.radians(roty)), 0, math.cos(math.radians(roty)), 0],
                          [0, 0, 0, 1]])

        self.rz = numpy.array([[math.cos(math.radians(rotz)), -math.sin(math.radians(rotz)), 0,0],
                          [math.sin(math.radians(rotz)), math.cos(math.radians(rotz)), 0,0],
                          [0, 0, 1, 0],
                          [0,0,0,1]])
        self.r = numpy.dot(self.ry, self.rx)
        self.r = numpy.dot(self.rz,self.r)
        #rotate
        self.verticies[i].modelpos = self.verticies[i].modelpos.dot(self.r)
  def set_internal(self,newpos):
      for i in range(0,len(self.verticies)):
        self.verticies[i].modelpos = self.verticies[i].modelpos + newpos
  def set_pos(self,newpos):
    self.verticies[0].processedpos = self.verticies[0].modelpos + newpos
    self.maxx = self.verticies[0].processedpos
    self.maxy = self.verticies[0].processedpos
    self.maxz =self.verticies[0].processedpos
    self.randomass = numpy.array((0,0,0,1))
    for i in range(1,len(self.verticies)):
      self.verticies[i].processedpos = self.verticies[i].modelpos + newpos
      if (self.verticies[i].processedpos[2] > self.maxz[2]):
          self.maxz = self.verticies[i].processedpos
      elif (self.verticies[i].processedpos[1] > self.maxy[1]):
          self.maxy = self.verticies[i].processedpos
      elif (self.verticies[i].processedpos[0] > self.maxx[0]):
          self.maxx = self.verticies[i].processedpos
      elif (self.verticies[i].processedpos.all() != self.randomass.all()):
          self.randomass = self.verticies[i].processedpos    
    if(numpy.all(self.maxx == self.maxz) or numpy.all(self.maxx == self.maxy)):
        self.maxx = self.randomass
    if(numpy.all(self.maxy == self.maxz)):
        self.maxy = self.randomass
    self.polygonplane = plane()
    #self.polygonplane.construct(self.maxx,self.maxy,self.maxz)
    self.polygonplane.construct(self.verticies[0].processedpos,self.verticies[1].processedpos,self.verticies[2].processedpos)
  def render_poly(self):
    view_direction = p.pos[:3] - self.verticies[0].processedpos[:3]
    #check if we poly is in view
    #if normal points in same diirection of camera its visible
    if numpy.linalg.norm(self.polygonplane.crossprod) > 0:  
        normalized_normal = self.polygonplane.crossprod / numpy.linalg.norm(self.polygonplane.crossprod)
        if numpy.dot(normalized_normal, view_direction) < 0:
            return
    #render the polygon
    self.render_actual()
  def render_actual(self):
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

# MAKE SURE ITS COUNTER CLOCKWISE
#OTHERWISE THE ENTIRE THING WILL BREAK
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
starmodel.set_pos(numpy.array((0,0,10,1)))

frontfc= polygon()
#front face
frontfc.verticies.append(vertex(numpy.array((0,0,0,1))))
frontfc.verticies.append(vertex(numpy.array((3,3,0,1))))
frontfc.verticies.append(vertex(numpy.array((3,0,0,1))))

frontfc.verticies.append(vertex(numpy.array((0,0,0,1))))
frontfc.verticies.append(vertex(numpy.array((3,3,0,1))))
frontfc.verticies.append(vertex(numpy.array((0,3,0,1))))
# left face
leftfc = polygon()
leftfc.verticies.append(vertex(numpy.array((3,0,0,1))))  
leftfc.verticies.append(vertex(numpy.array((3,3,0,1)))) 
leftfc.verticies.append(vertex(numpy.array((3,0,3,1))))  

leftfc.verticies.append(vertex(numpy.array((3,3,3,1))))  
leftfc.verticies.append(vertex(numpy.array((3,3,0,1)))) 
leftfc.verticies.append(vertex(numpy.array((3,0,3,1)))) 

#right face
rightfc = polygon()
rightfc.verticies.append(vertex(numpy.array((0,0,0,1))))
rightfc.verticies.append(vertex(numpy.array((0,0,3,1))))
rightfc.verticies.append(vertex(numpy.array((0,3,0,1))))

rightfc.verticies.append(vertex(numpy.array((0,3,3,1))))
rightfc.verticies.append(vertex(numpy.array((0,0,3,1))))
rightfc.verticies.append(vertex(numpy.array((0,3,0,1))))

#back face
backfc = polygon()
backfc.verticies.append(vertex(numpy.array((0,0,3,1))))
backfc.verticies.append(vertex(numpy.array((3,0,3,1))))
backfc.verticies.append(vertex(numpy.array((3,3,3,1))))

backfc.verticies.append(vertex(numpy.array((0,0,3,1))))
backfc.verticies.append(vertex(numpy.array((3,3,3,1))))
backfc.verticies.append(vertex(numpy.array((0,3,3,1))))

#bottom face
botfc = polygon()
botfc.verticies.append(vertex(numpy.array((0,0,0,1))))  
botfc.verticies.append(vertex(numpy.array((3,0,0,1)))) 
botfc.verticies.append(vertex(numpy.array((3,0,3,1))))

botfc.verticies.append(vertex(numpy.array((0,0,0,1)))) 
botfc.verticies.append(vertex(numpy.array((3,0,3,1))))
botfc.verticies.append(vertex(numpy.array((0,0,3,1))))

#top face
topfc = polygon()
topfc.verticies.append(vertex(numpy.array((0,3,0,1)))) 
topfc.verticies.append(vertex(numpy.array((0,3,3,1))))
topfc.verticies.append(vertex(numpy.array((3,3,3,1)))) 

topfc.verticies.append(vertex(numpy.array((0,3,0,1)))) 
topfc.verticies.append(vertex(numpy.array((3,3,3,1))))  
topfc.verticies.append(vertex(numpy.array((3,3,0,1))))  


triangle = model()
triangle.polygons.append(frontfc)
triangle.polygons.append(leftfc)
triangle.polygons.append(rightfc)
triangle.polygons.append(backfc)
triangle.polygons.append(botfc)
triangle.polygons.append(topfc)
triangle.set_pos(numpy.array((5,0,5,1)))
rotplane = polygon()
rotplane.verticies.append(vertex(numpy.array((2,0,0,1))))
rotplane.verticies.append(vertex(numpy.array((0,6,10,1))))
rotplane.verticies.append(vertex(numpy.array((1,2.5,10,1))))
rotplane.verticies.append(vertex(numpy.array((-1,-2,50,1))))



planetest = model()
planetest.polygons.append(rotplane)
planetest.set_pos(numpy.array((10,10,10,1)))


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
  #cube.render()
  #cube2.render()
  starmodel.render()
  triangle.render()
  #planetest.render()
  p.update_planes()
  time.sleep(0.01)
  pygame.display.update()
