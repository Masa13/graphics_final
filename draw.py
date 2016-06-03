from display import *
from matrix import *
from vector import *
from gmath import calculate_dot
from math import cos, sin, pi
from sys import maxint
import random
#import math

MAX_STEPS = 100

zbuffer = [[-5000 for x in range(500)] for x in range(500)] 
def clear_zbuffer():
    global zbuffer
    zbuffer = [[-5000 for x in range(500)] for x in range(500)] 

def add_polygon( points, x0, y0, z0, x1, y1, z1, x2, y2, z2):
    add_point( points, x0, y0, z0 )
    add_point( points, x1, y1, z1 )
    add_point( points, x2, y2, z2 )
   
def add_polygon_p(points, p0, p1, p2):
    add_polygon(points, 
                p0[0], p0[1], p0[2],
                p1[0], p1[1], p1[2],
                p2[0], p2[1], p2[2])

def draw_polygons(points, screen, env):
    color = [100,100,100] 
    def sortaequal(a,b,tol):
        return abs(a-b)<tol
    def light(x,y,z,ka,kd,ks): 
        colortmp = [0,0,0]
        ia = env["ambient"]
        for i in range(3):
            ambient = ka[i] * ia[i]
            colortmp[i] += ambient
            for light in env["lights"]:
                vector_l = vect_minus(light[3:],p0)
                n_surf_norm = normalize(surf_norm)
                n_vector_l = normalize(vector_l)
                
                diffuse = kd[i] * light[i] * \
                          max(0, dot_prod(n_surf_norm, 
                                          n_vector_l))

                n_x_vect = cross_prod(n_surf_norm, n_vector_l)
                specular_r_vec = normalize(vect_minus(scalar_prod(2,n_x_vect),n_vector_l))
                view_vec = normalize(vect_minus(p0,[0,0,-1]))
                
                specular = ks[i] * light[i] * \
                           max(0, dot_prod(specular_r_vec,
                                           view_vec)) ** 15

                colortmp[i] += diffuse+specular
                colortmp[i] = int(min(colortmp[i],255))
        return colortmp
            
    def scanlines(p0,p1,p2):
        if env["shading_mode"] == "flat":
            colortmp = light(p0[0],p0[1],p0[2],
                             (0.8,0.8,0.8), 
                             (0.8,0.8,0.8), 
                             (0.8,0.8,0.8)  
                            )
        else:
            colortmp = random.sample(xrange(255),3)
    
        for i in range(3):
            p0[i] = math.floor(p0[i])
            p1[i] = math.floor(p1[i])
            p2[i] = math.floor(p2[i])
        
        pts = sorted( (p0,p1,p2), key=lambda pt: pt[1])
        top = pts[0]; mid = pts[1]; bot = pts[2]

        yi = top[1]
        x0 = top[0]
        x1 = top[0]
        z0 = top[2]
        z1 = top[2]

        if bot[1] == top[1]:
            dx0 = 0
            dz0 = 0
        else:
            dx0 = (bot[0]-top[0])/(bot[1]-top[1])
            dz0 = (bot[2]-top[2])/(bot[1]-top[1])

        if mid[1] == top[1]:
            dx1m = 0
            dz1m = 0
        else:
            dx1m = (mid[0]-top[0])/(mid[1]-top[1])
            dz1m = (mid[2]-top[2])/(mid[1]-top[1])

        if bot[1] == mid[1]:
            dx1b = 0
            dz1b = 0
        else:
            dx1b = (bot[0]-mid[0])/(bot[1]-mid[1])
            dz1b = (bot[2]-mid[2])/(bot[1]-mid[1])

        while yi < mid[1]:
            x1 += dx1m
            z1 += dz1m
            yi += 1
            x0 += dx0
            z0 += dz0
            draw_line(screen, x0,yi,z0, x1,yi,z1, colortmp)
        x1 = mid[0]
        yi = mid[1]
        z1 = mid[2]
        draw_line(screen, x0,yi,z0, x1,yi,z1, colortmp)
        while yi < bot[1]:
            x0 += dx0
            z0 += dz0
            x1 += dx1b
            z1 += dz1b
            yi += 1
            draw_line(screen, x0,yi,z0, x1,yi,z1, colortmp)
            
            

    def draw_polygon(p0,p1,p2, c):
        if env["shading_mode"]=="wireframe":
            draw_line(screen, p0[0],p0[1],p0[2], p1[0],p1[1],p1[1], c)
            draw_line(screen, p1[0],p1[1],p1[2], p2[0],p2[1],p2[2], c)
            draw_line(screen, p2[0],p2[1],p2[2], p0[0],p0[1],p0[2], c)
        else:
            scanlines(p0,p1,p2)

    view_vect = [0, 0, -1]

    if len( points ) % 3 !=  0:
        print "Choose different number of points to draw polygon" 

    p = 0
    while p < len(points)-1:
        p0 = points[p]
        p1 = points[p+1]
        p2 = points[p+2]
        surf_norm = cross_prod(vect_minus(p1,p0),vect_minus(p2,p0))

        if dot_prod(surf_norm, view_vect) < 0:
            draw_polygon(points[p], points[p+1], points[p+2], color)

        p+=3

def add_box( points, x, y, z, width, height, depth ):
    x1 = x + width
    y1 = y - height
    z1 = z - depth

    #front
    add_polygon( points, 
                 x, y, z, 
                 x, y1, z,
                 x1, y1, z)
    add_polygon( points, 
                 x1, y1, z, 
                 x1, y, z,
                 x, y, z)
    #back
    add_polygon( points, 
                 x1, y, z1, 
                 x1, y1, z1,
                 x, y1, z1)
    add_polygon( points, 
                 x, y1, z1, 
                 x, y, z1,
                 x1, y, z1)
    #top
    add_polygon( points, 
                 x, y, z1, 
                 x, y, z,
                 x1, y, z)
    add_polygon( points, 
                 x1, y, z, 
                 x1, y, z1,
                 x, y, z1)
    #bottom
    add_polygon( points, 
                 x1, y1, z1, 
                 x1, y1, z,
                 x, y1, z)
    add_polygon( points, 
                 x, y1, z, 
                 x, y1, z1,
	         x1, y1, z1)
    #right side
    add_polygon( points, 
                 x1, y, z, 
                 x1, y1, z,
                 x1, y1, z1)
    add_polygon( points, 
                 x1, y1, z1, 
                 x1, y, z1,
                 x1, y, z)
    #left side
    add_polygon( points, 
                 x, y, z1, 
                 x, y1, z1,
                 x, y1, z)
    add_polygon( points, 
                 x, y1, z, 
                 x, y, z,
                 x, y, z1) 


def add_sphere( points, cx, cy, cz, r, step ):
    
    num_steps = MAX_STEPS / step
    temp = []

    generate_sphere( temp, cx, cy, cz, r, step )
    num_points = len( temp )

    lat = 0
    lat_stop = num_steps
    longt = 0
    longt_stop = num_steps

    num_steps += 1

    while lat < lat_stop:
        longt = 0
        while longt < longt_stop:
            
            index = lat * num_steps + longt

            px0 = temp[ index ][0]
            py0 = temp[ index ][1]
            pz0 = temp[ index ][2]

            px1 = temp[ (index + num_steps) % num_points ][0]
            py1 = temp[ (index + num_steps) % num_points ][1]
            pz1 = temp[ (index + num_steps) % num_points ][2]
            
            if longt != longt_stop - 1:
                px2 = temp[ (index + num_steps + 1) % num_points ][0]
                py2 = temp[ (index + num_steps + 1) % num_points ][1]
                pz2 = temp[ (index + num_steps + 1) % num_points ][2]
            else:
                px2 = temp[ (index + 1) % num_points ][0]
                py2 = temp[ (index + 1) % num_points ][1]
                pz2 = temp[ (index + 1) % num_points ][2]
                
            px3 = temp[ index + 1 ][0]
            py3 = temp[ index + 1 ][1]
            pz3 = temp[ index + 1 ][2]
      
            if longt != 0:
                add_polygon( points, px0, py0, pz0, px1, py1, pz1, px2, py2, pz2 )

            if longt != longt_stop - 1:
                add_polygon( points, px2, py2, pz2, px3, py3, pz3, px0, py0, pz0 )
            
            longt+= 1
        lat+= 1

def generate_sphere( points, cx, cy, cz, r, step ):

    rotation = 0
    rot_stop = MAX_STEPS
    circle = 0
    circ_stop = MAX_STEPS

    while rotation < rot_stop:
        circle = 0
        rot = float(rotation) / MAX_STEPS
        while circle <= circ_stop:
            
            circ = float(circle) / MAX_STEPS
            x = r * cos( pi * circ ) + cx
            y = r * sin( pi * circ ) * cos( 2 * pi * rot ) + cy
            z = r * sin( pi * circ ) * sin( 2 * pi * rot ) + cz
            
            add_point( points, x, y, z )

            circle+= step
        rotation+= step

def add_torus( points, cx, cy, cz, r0, r1, step ):
    
    num_steps = MAX_STEPS / step
    temp = []

    generate_torus( temp, cx, cy, cz, r0, r1, step )
    num_points = len(temp)

    lat = 0
    lat_stop = num_steps
    longt_stop = num_steps
    
    while lat < lat_stop:
        longt = 0

        while longt < longt_stop:
            index = lat * num_steps + longt

            px0 = temp[ index ][0]
            py0 = temp[ index ][1]
            pz0 = temp[ index ][2]

            px1 = temp[ (index + num_steps) % num_points ][0]
            py1 = temp[ (index + num_steps) % num_points ][1]
            pz1 = temp[ (index + num_steps) % num_points ][2]

            if longt != num_steps - 1:            
                px2 = temp[ (index + num_steps + 1) % num_points ][0]
                py2 = temp[ (index + num_steps + 1) % num_points ][1]
                pz2 = temp[ (index + num_steps + 1) % num_points ][2]

                px3 = temp[ (index + 1) % num_points ][0]
                py3 = temp[ (index + 1) % num_points ][1]
                pz3 = temp[ (index + 1) % num_points ][2]
            else:
                px2 = temp[ ((lat + 1) * num_steps) % num_points ][0]
                py2 = temp[ ((lat + 1) * num_steps) % num_points ][1]
                pz2 = temp[ ((lat + 1) * num_steps) % num_points ][2]

                px3 = temp[ (lat * num_steps) % num_points ][0]
                py3 = temp[ (lat * num_steps) % num_points ][1]
                pz3 = temp[ (lat * num_steps) % num_points ][2]


            add_polygon( points, px0, py0, pz0, px1, py1, pz1, px2, py2, pz2 );
            add_polygon( points, px2, py2, pz2, px3, py3, pz3, px0, py0, pz0 );        
            
            longt+= 1
        lat+= 1


def generate_torus( points, cx, cy, cz, r0, r1, step ):

    rotation = 0
    rot_stop = MAX_STEPS
    circle = 0
    circ_stop = MAX_STEPS

    while rotation < rot_stop:
        circle = 0
        rot = float(rotation) / MAX_STEPS
        while circle < circ_stop:
            
            circ = float(circle) / MAX_STEPS
            x = (cos( 2 * pi * rot ) *
                 (r0 * cos( 2 * pi * circ) + r1 ) + cx)
            y = r0 * sin(2 * pi * circ) + cy
            z = (sin( 2 * pi * rot ) *
                 (r0 * cos(2 * pi * circ) + r1))
            
            add_point( points, x, y, z )

            circle+= step
        rotation+= step



def add_circle( points, cx, cy, cz, r, step ):
    x0 = r + cx
    y0 = cy

    t = step
    while t<= 1:
        
        x = r * cos( 2 * pi * t ) + cx
        y = r * sin( 2 * pi * t ) + cy

        add_edge( points, x0, y0, cz, x, y, cz )
        x0 = x
        y0 = y
        t+= step
    add_edge( points, x0, y0, cz, cx + r, cy, cz )

def add_curve( points, x0, y0, x1, y1, x2, y2, x3, y3, step, curve_type ):
    xcoefs = generate_curve_coefs( x0, x1, x2, x3, curve_type )
    ycoefs = generate_curve_coefs( y0, y1, y2, y3, curve_type )
        
    t =  step
    while t <= 1:
        
        x = xcoefs[0][0] * t * t * t + xcoefs[0][1] * t * t + xcoefs[0][2] * t + xcoefs[0][3]
        y = ycoefs[0][0] * t * t * t + ycoefs[0][1] * t * t + ycoefs[0][2] * t + ycoefs[0][3]

        add_edge( points, x0, y0, 0, x, y, 0 )
        x0 = x
        y0 = y
        t+= step

def draw_lines( matrix, screen, color ):
    if len( matrix ) < 2:
        print "Need at least 2 points to draw a line"
        
    p = 0
    while p < len( matrix ) - 1:
        draw_line( screen, matrix[p][0], matrix[p][1],
                   matrix[p+1][0], matrix[p+1][1], color )
        p+= 2

def add_edge( matrix, x0, y0, z0, x1, y1, z1 ):
    add_point( matrix, x0, y0, z0 )
    add_point( matrix, x1, y1, z1 )

def add_point( matrix, x, y, z=0 ):
    matrix.append( [x, y, z, 1] )


def draw_line( screen, x0, y0, x1, y1, color ):
    dx = x1 - x0
    dy = y1 - y0
    if dx + dy < 0:
        dx = 0 - dx
        dy = 0 - dy
        tmp = x0
        x0 = x1
        x1 = tmp
        tmp = y0
        y0 = y1
        y1 = tmp
    
    if dx == 0:
        y = y0
        while y <= y1:
            plot(screen, color,  x0, y)
            y = y + 1
    elif dy == 0:
        x = x0
        while x <= x1:
            plot(screen, color, x, y0)
            x = x + 1
    elif dy < 0:
        d = 0
        x = x0
        y = y0
        while x <= x1:
            plot(screen, color, x, y)
            if d > 0:
                y = y - 1
                d = d - dx
            x = x + 1
            d = d - dy
    elif dx < 0:
        d = 0
        x = x0
        y = y0
        while y <= y1:
            plot(screen, color, x, y)
            if d > 0:
                x = x - 1
                d = d - dy
            y = y + 1
            d = d - dx
    elif dx > dy:
        d = 0
        x = x0
        y = y0
        while x <= x1:
            plot(screen, color, x, y)
            if d > 0:
                y = y + 1
                d = d - dx
            x = x + 1
            d = d + dy
    else:
        d = 0
        x = x0
        y = y0
        while y <= y1:
            plot(screen, color, x, y)
            if d > 0:
                x = x + 1
                d = d - dy
            y = y + 1
            d = d + dx
