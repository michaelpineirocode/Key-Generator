from PIL import Image
import numpy as np
from stl import stl, mesh
import settings
import sys
import time
import math

COMM_ARGUMENTS = { # global dict of com. line arguments for easier reference
    "k_input" : sys.argv[1], # input file name of key
    "kw_input": sys.argv[2], # input file of keyway
    "output": sys.argv[3], # output file name
    "k_sensitivity": float(sys.argv[4]), # sensitivity value of key
    "kw_sensitivity": float(sys.argv[5]), # sensitivity value of keyway (how much darkness in photo)
    "k_hole_sensitivity": float(sys.argv[6]),
    "kw_hole_sensitivity": float(sys.argv[7]),
    "gap_from_top": int(sys.argv[8]), # how many pixels down from the top   
    "gap_size": int(sys.argv[9]), # the size that the gap should be   
    "thickness": float(sys.argv[10])  
                }

def open_image(input_):
    img = Image.open("Pics/Inputs/" + input_)
    return img

def mean(pixel):
    sum_ = sum(pixel)
    average = int(sum_ / 3)
    return average

def bw(pixel, sens):
    gray = mean(pixel)
    if gray < 127 * COMM_ARGUMENTS[sens]: # the sense is whether to pass key or keyway sensitivity
        return (0, 0, 0)
    else:
        return (255, 255, 255)

def convert_to_bw(pix, x, y):
    for i in range(y):
        for j in range(x):
            pixel = pix[j, i]
            pix[j, i] = bw(pixel, "k_sensitivity")
    return pix

def save_image(img, tag):
    # tag to differentiate key from keyway
    img.save("Pics/Outputs/" + COMM_ARGUMENTS["output"] + "(" + tag + ")" + ".png")

def remove_holes(pix, x, y, sens):
    streak_size = COMM_ARGUMENTS[sens] # the minimum value of pixels in a row to be considered the new pattern
    current_streak = 0 # keeps track of the current streak size
    current_streak_black = True # keeps track of whether the current streak size is black
    black = True # keeps track of whether the last pixel was black
    
    for i in range(y): # loops through each pixel
        for j in range(x):
            pixel = pix[j, i][0]
            if pixel == 255: # if the current pixel is white
                if black: # if the last pixel was black
                    black = False # is now white
                    current_streak = 0 # since it changed, the new streak is 0
                else: # if last pixel was black
                    current_streak += 1
                    if current_streak >= streak_size: # test if a new streak exists
                        current_streak_black = False
            else: # if current pixel is black
                if not black: # if last pixel was white
                    black = True # change black to True
                    current_streak = 0 # reset the current streak
                else: # if last pixel was black
                    current_streak += 1
                    if current_streak >= streak_size:
                        current_streak_black = True
            if current_streak_black: #if the current streak is "black"
                pix[j, i] = settings.Colors().BLACK
            else:
                pix[j, i] = settings.Colors().WHITE
                
    return pix

def remove_gradient(pix, x, y, sens): #goes vertically to remove excess gradients
    streak_size = COMM_ARGUMENTS[sens] # the minimum value of pixels in a row to be considered the new pattern
    current_streak = 0 # keeps track of the current streak size
    current_streak_black = True # keeps track of whether the current streak size is black
    black = True # keeps track of whether the last pixel was black
    
    for i in range(x): # loops through each pixel
        for j in range(y):
            pixel = pix[i, j][0]
            if pixel == 255: # if the current pixel is white
                if black: # if the last pixel was black
                    black = False # is now white
                    current_streak = 0 # since it changed, the new streak is 0
                else: # if last pixel was black
                    current_streak += 1
                    if current_streak >= streak_size: # test if a new streak exists
                        current_streak_black = False
            else: # if current pixel is black
                if not black: # if last pixel was white
                    black = True # change black to True
                    current_streak = 0 # reset the current streak
                else: # if last pixel was black
                    current_streak += 1
                    if current_streak >= streak_size:
                        current_streak_black = True
            if current_streak_black: #if the current streak is "black"
                pix[i, j] = settings.Colors().BLACK
            else:
                pix[i, j] = settings.Colors().WHITE
                
    return pix
         
def create_gap(pix, x, y):
    # finds the upper left most white pixel
    for i in range(y):
        for j in range(x):
            if pix[j, i] == settings.Colors().WHITE:
                top = (j, i)
                break
        if "top" in locals():
            break

    for i in range(top[1]+COMM_ARGUMENTS["gap_from_top"], top[1]+COMM_ARGUMENTS["gap_from_top"]+COMM_ARGUMENTS["gap_size"]):
        for j in range(x): # range(top[0] + COMM_ARGUMENTS["gap_from_top"] ,x)
            pix[j, i] = settings.Colors().BLACK
    return pix
    
def create_heightmap(pix, x, y):
    heightmap = [[0 for i in range(y + 1)] for j in range(x + 1)] # this creates an empty 2D array of size x by y
    for i in range(y):
        for j in range(x):
            pixel = pix[j, i][0]
            if pixel == 0:
                heightmap[j][i] = 0
            else:
                heightmap[j][i] = (COMM_ARGUMENTS["thickness"])
    return heightmap

def change_vectors(surfaces, vert_index, array_content):
    surfaces["vectors"][vert_index] = np.array(array_content)
    vert_index += 1
    return surfaces, vert_index

def check_sides(heightmap, x, y):
    if heightmap[y][x-1] == 0 or heightmap[y][x+1] == 0 or heightmap[y-1][x] == 0 or heightmap[y+1][x] == 0:
        return True
    else:
        return False

def find_surfaces(heightmap):
    # need the number of white pixels to determine the size of the array
    num_white = 0
    for i in range(len(heightmap)):
        for j in range(len(heightmap[0])):
            if heightmap[i][j] > 0: # if the height is not 0, add to the running count
                num_white += 1
    
    num_vertices = 4 * num_white # size of the surfaces array
    surfaces = np.zeros(num_vertices, dtype=mesh.Mesh.dtype) # surfaces numpy array
    thickness = COMM_ARGUMENTS["thickness"]

    vert_index = 0
    for y in range(len(heightmap)):
        for x in range(len(heightmap[0])):
            if heightmap[y][x] > 0:
                # top section
                surfaces, vert_index = change_vectors(surfaces, vert_index, [[x, y, thickness], [x, y+1, thickness], [x+1, y, thickness]]) #creates "first" triangle
                surfaces, vert_index = change_vectors(surfaces, vert_index, [[x, y+1, thickness], [x+1, y+1, thickness], [x+1, y, thickness]]) # creates the second
            
                # bottom
                surfaces, vert_index = change_vectors(surfaces, vert_index, [[x, y, 0], [x, y+1, 0], [x+1, y, 0]]) #creates "first" triangle
                surfaces, vert_index = change_vectors(surfaces, vert_index, [[x, y+1, 0], [x+1, y+1, 0], [x+1, y, 0]]) # creates the second
                
                # sides (this is the hard part)
                if check_sides(heightmap, x, y): # if the pixel is on an outside edge
                    #surfaces, vert_index = change_vectors(surfaces, vert_index, [[x+1, y, thickness], [x, y, thickness], [x, y, 0]]) #creates "first" triangle
                    #surfaces, vert_index = change_vectors(surfaces, vert_index, [[x+1, y, 0], [x+1, y, thickness], [x, y, thickness]]) # creates the second
                    pass

    return surfaces


def main(): # calls other functions and tracks time
    img = open_image(COMM_ARGUMENTS["k_input"])
    x = img.size[0]
    y = img.size[1]
    pix = img.load()

    pix = convert_to_bw(pix, x, y)
    pix = remove_holes(pix, x, y, "k_hole_sensitivity")
    pix = remove_gradient(pix, x, y, "kw_hole_sensitivity")
    pix = create_gap(pix, x, y)
    save_image(img, "KEY")
    heightmap = create_heightmap(pix, x, y)
    print(heightmap[int(len(heightmap) / 2)])
    surfaces = find_surfaces(heightmap)
    
    stl_mesh = mesh.Mesh(surfaces, remove_empty_areas = False)
    stl_mesh.normals
    stl_mesh.save("STLS/" + COMM_ARGUMENTS["output"] + ".stl", mode=stl.Mode.ASCII)


if __name__ == "__main__":
    main()