import math
import time

import pygame

from graphics_functions import (
    clip_points,
    project_points,
    rotate_points,
    scale_points,
    transform_points,
)

pygame.init()


#system setup
screen_size = (750, 500)
target_fps = 60

print(pygame.display.get_desktop_sizes())

screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("super cool graphics testing")
clock = pygame.time.Clock()

running = True

system_font = pygame.font.SysFont("Times New Roman", 12)

#rendering variables
move_speed = 10
turn_speed = 1

frame = 0
start_time = time.time()
depth_buffer = []
draw_order = []
move_direction = [0, 0, 0]
velocity = [0, 0, 0]

class GameObject:
    def __init__(self, points, position, rotation, scale, color):
        self.points = points
        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.color = color

    def get_transformed_points(self, target_transform):
        points = scale_points(self.points, self.scale)
        points = rotate_points(points, self.rotation)
        points = transform_points(points, [
        target_transform[0] + self.position[0],
        target_transform[1] + self.position[1],
        target_transform[2] + self.position[2]
        ])

        return points

class Camera:
    def __init__(self, position, rotation, clipping_distance, focal_length):
        self.position = position
        self.rotation = rotation
        self.clipping_distance = clipping_distance
        self.focal_length = focal_length

    def get_camera_points(self, points):
        camera_points = rotate_points(points, self.rotation)
        camera_points = clip_points(camera_points, self.clipping_distance)

        return camera_points

    def handle_input(self, keys):
        ry = self.rotation[1] * (math.pi / 180)

        if keys[pygame.key.key_code('r')] == True:
            move_direction[1] = move_speed
        elif keys[pygame.key.key_code('f')] == True:
            move_direction[1] = -move_speed
        else:
            move_direction[1] = 0

        if keys[pygame.key.key_code('q')] == True:
            self.rotation[1] += turn_speed
        elif keys[pygame.key.key_code('e')] == True:
            self.rotation[1] -= turn_speed
    
        if keys[pygame.key.key_code('a')] == True:
            move_direction[0] = math.cos(ry) * move_speed
            move_direction[2] = math.sin(ry) * move_speed
        elif keys[pygame.key.key_code('d')] == True:
            move_direction[0] = -math.cos(ry) * move_speed
            move_direction[2] = -math.sin(ry) * move_speed
        elif keys[pygame.key.key_code('s')] == True:
            move_direction[0] = -math.sin(ry) * move_speed
            move_direction[2] = math.cos(ry) * move_speed
        elif keys[pygame.key.key_code('w')] == True:
            move_direction[0] = math.sin(ry) * move_speed
            move_direction[2] = -math.cos(ry) * move_speed
        else:
            move_direction[0] = 0
            move_direction[2] = 0


cube_points = [
    [-50,-50,50],
    [50,-50,50],
    [50,50,50],
    [-50,50,50],
    [-50,-50,150],
    [50,-50,150],
    [50,50,150],
    [-50,50,150]
    ]
    
plane_points = [
    [-50,-50,0],
    [50,-50,0],
    [50,50,0],
    [-50,50,0]
]

triangle_points = [
    [-50,50,0],
    [0,-50,0],
    [50,50,0]
]

#point data, position, rotation, scale, color
objects = [
    GameObject(triangle_points, (0,0,1000), (45,0,0), (1,1,1), (155,155,155)),
    GameObject(triangle_points, (100,0,1000), (0,45,0), (1,1,1), (155,155,155)),
    GameObject(triangle_points, (200,0,1000), (0,0,45), (1,1,1), (155,155,155)),

    GameObject(plane_points, (0,0,250), (0,0,0), (1,1,1), (155,0,0)),

    GameObject(plane_points, (100,0,250), (0,0,0), (1,1,1), (0,155,0)),
    GameObject(plane_points, (200,0,250), (0,0,0), (1,1,1), (0,0,155)),
    GameObject(plane_points, (0,0,500), (0,0,0), (1,1,1), (65,50,0)),
    GameObject(plane_points, (100,0,500), (0,0,0), (1,1,1), (50,175,80)),
    GameObject(plane_points, (200,0,500), (0,0,0), (1,1,1), (0,100,200)),
    GameObject(plane_points, (0,0,750), (0,0,0), (1,1,1), (155,155,155)),
    GameObject(plane_points, (100,0,750), (0,0,0), (1,1,1), (155,155,155)),
    GameObject(plane_points, (200,0,750), (0,0,0), (1,1,1), (155,155,155)),

    GameObject(plane_points, [0,-50,0], (45,0,0), (5,5,1), (155,155,155))
]

player_camera = Camera([0,0,0], [0,0,0], 1, 300)

def get_FPS():
    fps = int(frame / (time.time() - start_time))
    return fps

def render_object(objectID):
    color = objects[objectID].color
    transformed_points = objects[objectID].get_transformed_points(player_camera.position)

    camera_points = player_camera.get_camera_points(transformed_points)

    if not camera_points:
        return

    #project onto 2D screen
    flat_points = project_points(camera_points, player_camera.focal_length, screen_size)

    if not flat_points:
        return
        
    x_values = []
    y_values = []
    for point in flat_points:
        x_values.append(point[0])
        y_values.append(point[1])
            
    if not len(x_values) > 0:
        return

    z_values = []

    for point in camera_points:
        z_values.append(point[2])
    
    
    #populate debth buffer with current object's id and max z value
    depth_buffer[objectID] = ([objectID, sum(z_values)/len(z_values)])
    
    if not max(x_values) <= 0 and not min(x_values) >= screen_size[0]:
        pygame.draw.polygon(
            screen,
            color,
            tuple(flat_points),
            width=0
        )

def on_step():
    global frame
    global draw_order

    #clear screen
    screen.fill((30, 30, 30)) 

    if frame == 0:
        initialize()

    #debug information
    screen.blit(system_font.render(f"FPS: {get_FPS()}", True, (255, 255, 255)), (20, 20))
    screen.blit(system_font.render(f"Frame: {frame}", True, (255, 255, 255)), (20, 40))
    screen.blit(system_font.render(f"Objects: {len(depth_buffer)}", True, (255, 255, 255)), (20, 60))
    screen.blit(system_font.render(f"Position: {int(player_camera.position[0]), int(player_camera.position[1]), int(player_camera.position[2])}",
                                    True, (255, 255, 255)), (20, 80))
    
    frame += 1
    
    draw_order = list(depth_buffer)
    
    draw_order.sort(key = lambda obj: obj[1], reverse=True)

    for obj in draw_order:
        render_object(obj[0])
    
def initialize():
    for i in range(len(objects)):
        depth_buffer.append([i, 100])
        render_object(i)

def physicstest():
    camY = player_camera.position[1]
    
    velocity[0] += move_direction[0]
    velocity[1] += move_direction[1]
    velocity[2] += move_direction[2]

    player_camera.position[0] += velocity[0]
    player_camera.position[1] += velocity[1]
    player_camera.position[2] += velocity[2]

while running:
    on_step() #main loop

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player_camera.handle_input(pygame.key.get_pressed()) #give input to camera

    physicstest()

    pygame.display.flip() #render everything
    clock.tick(target_fps) #60 fps