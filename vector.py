import math

def cross_prod(a,b):
    return [a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0]]

def dot_prod(a,b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def vect_minus(a,b):
    return [a[0]-b[0], a[1]-b[1], a[2]-b[2]]

def scalar_prod(k,a):
    return [k*a[0], k*a[1], k*a[2]]

def magnitude(v):
    return math.sqrt(sum(i**2 for i in v))

def normalize(v):
    return [i/magnitude(v) for i in v]
