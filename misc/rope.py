import pygame
import math
import time

pygame.init()

pygame.display.set_caption('Quick Start')
window_surface = pygame.display.set_mode((640, 640))
background = pygame.Surface((640, 640))
background.fill((0, 0, 0))

GRAVITY = 1200.0
SEGMENT_LENGTH = 12
NUM_SEGMENTS = 48
CONSTRAINT_ITERS = 6
DESIRED = SEGMENT_LENGTH

border_collision = False 

class ropesegment:
    def __init__(self, xm, ym):
        self.xm = float(xm)
        self.ym = float(ym)
        self.prev_xm = float(xm)
        self.prev_ym = float(ym)
        self.accel_xm = 0.0
        self.accel_ym = GRAVITY

    def verlet(self):
        temp_xm = self.xm
        temp_ym = self.ym
        dt = 0.01
        self.xm += (self.xm - self.prev_xm) + self.accel_xm * (dt * dt)
        self.ym += (self.ym - self.prev_ym) + self.accel_ym * (dt * dt)
        self.prev_xm = temp_xm
        self.prev_ym = temp_ym

    def draw(self):
        pygame.draw.circle(background, (156, 78, 200), (int(self.xm), int(self.ym)), 6)

rope = []
dragging = False

is_running = True
while is_running:
    mouse_xm, mouse_ym = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            rope = [ropesegment(mouse_xm, mouse_ym + i * SEGMENT_LENGTH) for i in range(NUM_SEGMENTS)]
            dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_k:
                border_collision = not border_collision 

    background.fill((0, 0, 0))

    for seg in rope:
        seg.verlet()

    for _ in range(CONSTRAINT_ITERS):
        for i, seg in enumerate(rope):
            if i == 0:
                if dragging:
                    dx = seg.xm - mouse_xm
                    dy = seg.ym - mouse_ym
                    seg.xm -= dx
                    seg.ym -= dy
                continue
            prev_seg = rope[i - 1]
            dx = prev_seg.xm - seg.xm
            dy = prev_seg.ym - seg.ym
            dist = math.hypot(dx, dy)
            if dist == 0:
                continue
            diff = DESIRED - dist
            correction_x = (dx / dist) * diff * 0.5
            correction_y = (dy / dist) * diff * 0.5
            seg.xm -= correction_x
            seg.ym -= correction_y
            prev_seg.xm += correction_x
            prev_seg.ym += correction_y

    if border_collision:
        for seg in rope:
            if seg.xm < 0:
                seg.xm = 0
                seg.prev_xm = seg.xm
            if seg.xm > 640:
                seg.xm = 640
                seg.prev_xm = seg.xm
            if seg.ym < 0:
                seg.ym = 0
                seg.prev_ym = seg.ym
            if seg.ym > 640:
                seg.ym = 640
                seg.prev_ym = seg.ym

    for i in range(len(rope) - 1):
        pygame.draw.line(background, (200, 200, 200),
                         (int(rope[i].xm), int(rope[i].ym)),
                         (int(rope[i + 1].xm), int(rope[i + 1].ym)), 2)
    for seg in rope:
        seg.draw()

    window_surface.blit(background, (0, 0))
    pygame.display.update()
    time.sleep(0.01)


