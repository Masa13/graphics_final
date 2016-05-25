"""========== script.py ==========
  This is the only file you need to modify in order
  to get a working mdl project (for now).
  my_main.c will serve as the interpreter for mdl.
  When an mdl script goes through a lexer and parser, 
  the resulting operations will be in the array op[].
  Your job is to go through each entry in op and perform
  the required action from the list below:
  frames: set num_frames for animation
  basename: set name for animation
  vary: manipluate knob values between two given frames
        over a specified interval
  set: set a knob to a given value
  
  setknobs: set all knobs to a given value
  push: push a new origin matrix onto the origin stack
  
  pop: remove the top matrix on the origin stack
  move/scale/rotate: create a transformation matrix 
                     based on the provided values, then 
		     multiply the current top of the
		     origins stack by it.
  box/sphere/torus: create a solid object based on the
                    provided values. Store that in a 
		    temporary matrix, multiply it by the
		    current top of the origins stack, then
		    call draw_polygons.
  line: create a line based on the provided values. Store 
        that in a temporary matrix, multiply it by the
	current top of the origins stack, then call draw_lines.
  save: call save_extension with the provided filename
  display: view the image live
  
  jdyrlandweaver
  ========================="""


import os,sys
import mdl
from display import *
from matrix import *
from draw import *



"""======== first_pass( commands, symbols ) ==========
  Checks the commands array for any animation commands
  (frames, basename, vary)
  
  Should set num_frames and basename if the frames 
  or basename commands are present
  If vary is found, but frames is not, the entire
  program should exit.
  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  jdyrlandweaver
  ==================== """
def first_pass( commands ):
    num_frames = 1
    basename = ""
    shading_mode = "flat"
    ambient = (20,20,20)
    hasvary = False
    
    for command in commands:
        if command[0] == "frames":
            num_frames = command[1]
        elif command[0] == "basename":
            basename = command[1]
        elif command[0] == "vary":
            hasvary = True
        elif command[0] == "shading":
            shading_mode = command[1]
        elif command[0] == "ambient":
            ambient = (command[1],command[2],command[3])

    if hasvary and num_frames == 1:
        print "MDL ERROR: Found 'vary' but not 'frames'"
        print "Exiting..."
        sys.exit()

    if num_frames != 1 and basename == "":
        print "INFO: Found 'num_frames' but not 'basename'"
        print "INFO: Settings basename to 'anim'"
        basename = "anim"
            
    return (num_frames,basename,shading_mode,ambient)

"""======== second_pass( commands ) ==========
  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).
  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.
  Go through the command array, and when you find vary, go 
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value. 
  ===================="""

def second_pass( commands, num_frames ):
    frames = []
    for i in range(num_frames):
        newframe = {}
        frames.append(newframe)
    for c in commands:
        if c[0] == "vary":
            for i in range(c[2],c[3]+1):
                length = float(c[3]-c[2])
                frames[i][c[1]] = i/length
    return frames
                
    
    
def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)
    
    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    num_frames,basename,shading_mode,ambient = first_pass(commands)
    frames = second_pass(commands,num_frames)

    lights = []
    for s in symbols:
        if s[0] == 'light': lights.append(s[1])

    env = {}
    env["shading_mode"] = shading_mode
    env["ambient"] = ambient
    env["lights"] = lights
    
    if num_frames > 1 and not os.path.exists("anim"):
        os.makedirs("anim")

    for frame,i in zip(frames,range(len(frames))):
        print i,frame
        screen = run_frame(commands,frame,env)
        if num_frames > 1:
            save_ppm(screen, "anim/"+basename+("%03d"%i)+".ppm")
        
def run_frame(commands,frame,env):
    clear_zbuffer()
    color = [255, 255, 255]
    tmp = new_matrix()
    tmp = ident( tmp )

    stack = [ tmp ]
    screen = new_screen()

    for command in commands:
        if command[0] == "push":
            copy = matrix_copy(stack[-1])
            stack.append(copy)

        elif command[0] == "pop":
            stack.pop()

        elif command[0] == "move":
            dx,dy,dz = command[1],command[2],command[3]
            knob = command[4]
            if knob and knob in frame:
                dx *= frame[knob]
                dy *= frame[knob]
                dz *= frame[knob]
            tmat = make_translate(dx,dy,dz)
            stack[-1] = matrix_mult(stack[-1],tmat)
            
        elif command[0] == "rotate":
            rmat = new_matrix(4,4)
            deg = command[2]
            knob = command[3]
            if knob and knob in frame:
                deg *= frame[knob]
            if command[1] == "x":
                rmat = make_rotX(deg)
            elif command[1] == "y":
                rmat = make_rotY(deg)
            elif command[1] == "z":
                rmat = make_rotZ(deg)
            else:
                print "invalid rotation axis"
            stack[-1] = matrix_mult(stack[-1],rmat)


        elif command[0] == "scale":
            sx,sy,sz = command[1],command[2],command[3]
            knob = command[4]
            if knob and knob in frame:
                sx *= frame[knob]
                sy *= frame[knob]
                sz *= frame[knob]
            smat = make_scale(sx,sy,sz)
            stack[-1] = matrix_mult(stack[-1],smat)
            
        elif command[0] == "box":
            polymat = []
            add_prism(polymat,
                      command[1],command[2],command[3],
                      command[4],command[5],command[6])
            #if command[7]:
            #    pass
            polymat = matrix_mult(stack[-1], polymat)
            draw_polygons(polymat, screen, env)

        elif command[0] == "sphere":
            polymat = []
            add_sphere(polymat,
                       command[1],command[2],command[3],
                       command[4],36)
            #if command[5]:
            #    pass
            polymat = matrix_mult(stack[-1], polymat)
            draw_polygons(polymat, screen, env)

        elif command[0] == "torus":
            polymat = []
            add_torus(polymat,
                      command[1],command[2],command[3],
                      command[4],command[5],50)
            #if command[6]:
            #    pass
            polymat = matrix_mult(stack[-1], polymat)
            draw_polygons(polymat, screen, env)

        elif command[0] == "line":
            linemat = []
            #if command[whatever]:
            #    pass
            add_edge(linemat,
                     command[1],command[2],command[3],
                     command[4],command[5],command[6])
            linemat = matrix_mult(stack[-1], linemat)
            draw_lines(linemat)
            

        elif command[0] == "save":
            save_ppm(screen, command[1])

        elif command[0] == "display":
            display(screen)

        elif command[0] in ["vary","basename","frames"]:
            pass

        elif command[0] in ["shading","ambient","light"]:
            pass

        else:
            print "unknown command somehow?"

    return screen
