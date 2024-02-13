import random
import pygame
#from pygame.gfxdraw import bezier




def ptOnCurve(b, t):
    q = b.copy()
    for k in range(1, len(b)):
        for i in range(len(b) - k):
            q[i] = (1-t) * q[i][0] + t * q[i+1][0], (1-t) * q[i][1] + t * q[i+1][1]
    return round(q[0][0]), round(q[0][1])

def bezier(surf, b, samples, color, thickness):
    pts = [ptOnCurve(b, i/samples) for i in range(samples+1)]
    pygame.draw.lines(surf, color, False, pts, thickness)

def hand_sketch_line(surf,start_pos,end_pos,color=(0,0,0),width=1,random_scale=5,random_seed=None):
    n_controls=8
    points=[]
    points.append(start_pos)
    if random_seed is not None:
        random.seed(random_seed)
    for i in range(n_controls):
        t=i/n_controls
        x=(1-t)*start_pos[0]+t*end_pos[0]
        y=(1-t)*start_pos[1]+t*end_pos[1]
        x+=random.randint(-random_scale,random_scale)
        y+=random.randint(-random_scale,random_scale)
        if i==0:
            points=[(x,y)]
        else:
            points.append((x,y))
    points.append(end_pos)
    bezier(surf,points,10,color,width)