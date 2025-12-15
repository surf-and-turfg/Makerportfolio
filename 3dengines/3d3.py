import pygame
import numpy
import math
import time
import copy
from numba import njit, prange

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


#loads the textuyre
texture = pygame.image.load("texture.png").convert()
texw, texh = texture.get_size()

size = max(texw, texh)
texture = pygame.transform.scale(texture, (size, size))

texw, texh = texture.get_size()
texarray = pygame.surfarray.pixels3d(texture)
def barycentric(px, py, a, b, c):
    den = (b[1]-c[1])*(a[0]-c[0]) + (c[0]-b[0])*(a[1]-c[1])
    if den == 0:
        return -1, -1, -1
    w0 = ((b[1]-c[1])*(px-c[0]) + (c[0]-b[0])*(py-c[1])) / den
    w1 = ((c[1]-a[1])*(px-c[0]) + (a[0]-c[0])*(py-c[1])) / den
    w2 = 1 - w0 - w1
    return w0, w1, w2

#literally the only way to make it run at a playable framrate
@njit(parallel=True)
def draw_texture(screenarray, texarray, pts, uvs):
    x0, y0 = pts[0]
    x1, y1 = pts[1]
    x2, y2 = pts[2]

    u0, v0 = uvs[0]
    u1, v1 = uvs[1]
    u2, v2 = uvs[2]

    height, width, _ = screenarray.shape
    texh, texw, _ = texarray.shape
    
    #only checking for bounding in the specified area
    minx = max(int(min(x0, x1, x2)), 0)
    maxx = min(int(max(x0, x1, x2)), width - 1)
    miny = max(int(min(y0, y1, y2)), 0)
    maxy = min(int(max(y0, y1, y2)), height - 1)

    den = (y1 - y2)*(x0 - x2) + (x2 - x1)*(y0 - y2)
    if den == 0:
        return

    for y in prange(miny, maxy + 1):
        for x in range(minx, maxx + 1):
            w0 = ((y1 - y2)*(x - x2) + (x2 - x1)*(y - y2)) / den
            w1 = ((y2 - y0)*(x - x2) + (x0 - x2)*(y - y2)) / den
            w2 = 1 - w0 - w1

            if w0 >= 0 and w1 >= 0 and w2 >= 0:
                u = u0*w0 + u1*w1 + u2*w2
                v = v0*w0 + v1*w1 + v2*w2

                tx = int(u * (texw - 1))
                ty = int((1 - v) * (texh - 1))

                screenarray[y, x, 0] = texarray[tx, ty, 0]
                screenarray[y, x, 1] = texarray[tx, ty, 1]
                screenarray[y, x, 2] = texarray[tx, ty, 2]

class vertex:
  def __init__(self, position, uv):
    self.modelpos = position
    self.uv = uv
    self.processedpos = numpy.array((0,0,0,1))


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
        x = 320 * newpos[1] + 320
        y = 320 * -newpos[0] + 320
        self.pointstorender.append((x,y,w))
        #pygame.draw.circle(background,(255,0,0),(x,y),10)
    #this is faster then individually mapping the texture pixels
    screenarray = pygame.surfarray.pixels3d(background)
    for i in range(0, len(self.pointstorender), 3):
        w0 = self.pointstorender[i][2]
        w1 = self.pointstorender[i+1][2]
        w2 = self.pointstorender[i+2][2]

        # only draw if all three vertices are infonrt
        if w0 <= 0 and w1 <= 0 and w2 <= 0:
            pts = [
                self.pointstorender[i][0:2],
                self.pointstorender[i+1][0:2],
                self.pointstorender[i+2][0:2]
            ]

            uvs = [
                self.verticies[i].uv,
                self.verticies[i+1].uv,
                self.verticies[i+2].uv
            ]

            draw_texture(screenarray, texarray, pts, uvs)
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
# OR EVERYTHING BRAEKSKSK
mpole = polygon()
mpole.verticies.append(vertex(numpy.array((0,0,0,1)), (0,0)))
mpole.verticies.append(vertex(numpy.array((2,9,0,1)), (1,1)))
mpole.verticies.append(vertex(numpy.array((2,0,0,1)), (1,0)))

mpole.verticies.append(vertex(numpy.array((0,0,0,1)), (0,0)))
mpole.verticies.append(vertex(numpy.array((2,9,0,1)), (1,1)))
mpole.verticies.append(vertex(numpy.array((0,9,0,1)), (0,1)))

mpole2 = polygon()
mpole2.verticies.append(vertex(numpy.array((-13,0,0,1)), (0,0)))
mpole2.verticies.append(vertex(numpy.array((-11,9,0,1)), (1,1)))
mpole2.verticies.append(vertex(numpy.array((-11,0,0,1)), (1,0)))

mpole2.verticies.append(vertex(numpy.array((-13,0,0,1)), (0,0)))
mpole2.verticies.append(vertex(numpy.array((-11,9,0,1)), (1,1)))
mpole2.verticies.append(vertex(numpy.array((-13,9,0,1)), (0,1)))


m = model()
m.polygons.append(mpole)
m.polygons.append(mpole2)
m.set_pos(numpy.array((-5,0,5,1)))


frontfc= polygon()
#front face
frontfc.verticies.append(vertex(numpy.array((0,0,0,1)), (0,0)))
frontfc.verticies.append(vertex(numpy.array((3,3,0,1)), (1,1)))
frontfc.verticies.append(vertex(numpy.array((3,0,0,1)), (1,0)))

frontfc.verticies.append(vertex(numpy.array((0,0,0,1)), (0,0)))
frontfc.verticies.append(vertex(numpy.array((3,3,0,1)), (1,1)))
frontfc.verticies.append(vertex(numpy.array((0,3,0,1)), (0,1)))
# left face
leftfc = polygon()
leftfc.verticies.append(vertex(numpy.array((3,0,0,1)), (0,0)))  
leftfc.verticies.append(vertex(numpy.array((3,3,0,1)), (0,1))) 
leftfc.verticies.append(vertex(numpy.array((3,0,3,1)), (1,0)))  

leftfc.verticies.append(vertex(numpy.array((3,3,3,1)), (1,1)))  
leftfc.verticies.append(vertex(numpy.array((3,3,0,1)), (0,1))) 
leftfc.verticies.append(vertex(numpy.array((3,0,3,1)), (1,0))) 

#right face
rightfc = polygon()
rightfc.verticies.append(vertex(numpy.array((0,0,0,1)), (1,0)))
rightfc.verticies.append(vertex(numpy.array((0,0,3,1)), (0,0)))
rightfc.verticies.append(vertex(numpy.array((0,3,0,1)), (1,1)))

rightfc.verticies.append(vertex(numpy.array((0,3,3,1)), (0,1)))
rightfc.verticies.append(vertex(numpy.array((0,0,3,1)), (0,0)))
rightfc.verticies.append(vertex(numpy.array((0,3,0,1)), (1,1)))

#back face
backfc = polygon()
backfc.verticies.append(vertex(numpy.array((0,0,3,1)), (0,0)))
backfc.verticies.append(vertex(numpy.array((3,0,3,1)), (1,0)))
backfc.verticies.append(vertex(numpy.array((3,3,3,1)), (1,1)))

backfc.verticies.append(vertex(numpy.array((0,0,3,1)), (0,0)))
backfc.verticies.append(vertex(numpy.array((3,3,3,1)), (1,1)))
backfc.verticies.append(vertex(numpy.array((0,3,3,1)), (0,1)))

#bottom face
botfc = polygon()
botfc.verticies.append(vertex(numpy.array((0,0,0,1)), (0,1)))  
botfc.verticies.append(vertex(numpy.array((3,0,0,1)), (1,1))) 
botfc.verticies.append(vertex(numpy.array((3,0,3,1)), (1,0)))

botfc.verticies.append(vertex(numpy.array((0,0,0,1)), (0,1))) 
botfc.verticies.append(vertex(numpy.array((3,0,3,1)), (1,0)))
botfc.verticies.append(vertex(numpy.array((0,0,3,1)), (0,0)))
#top face
topfc = polygon()
topfc.verticies.append(vertex(numpy.array((0,3,0,1)), (0,0))) 
topfc.verticies.append(vertex(numpy.array((0,3,3,1)), (0,1)))
topfc.verticies.append(vertex(numpy.array((3,3,3,1)), (1,1))) 

topfc.verticies.append(vertex(numpy.array((0,3,0,1)), (0,0))) 
topfc.verticies.append(vertex(numpy.array((3,3,3,1)), (1,1)))  
topfc.verticies.append(vertex(numpy.array((3,3,0,1)), (1,0)))  


triangle = model()
triangle.polygons.append(frontfc)
triangle.polygons.append(leftfc)
triangle.polygons.append(rightfc)
triangle.polygons.append(backfc)
triangle.polygons.append(botfc)
triangle.polygons.append(topfc)
triangle.set_pos(numpy.array((5,0,5,1)))

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
    newz = p.pos[2] - (playerSin)
    newx = p.pos[0] - (playerCos)
    p.pos = numpy.array((newx,p.pos[1],newz,1))
  elif (flagd):
    playerCos = math.cos(math.radians(p.viewdiry))*0.1
    playerSin = math.sin(math.radians(p.viewdiry))*0.1
    newz = p.pos[2] + (playerSin)
    newx = p.pos[0] + (playerCos)
    p.pos = numpy.array((newx,p.pos[1],newz,1))
   
  if (rotleft):
    p.viewdiry+=1
  elif (rotright):
    p.viewdiry-=1
   
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
  #starmodel.render()
  m.render()
  triangle.render()
  #planetest.render()
  p.update_planes()
  time.sleep(0.01)
  pygame.display.update()
