from PIL import Image
import numpy as np
from stl import stl, mesh
import sys
import time
import math

COMM_ARGUMENTS = { # global dict of com. line arguments for easier reference
    "k_input" : sys.argv[1], # input file name of key
    "kw_input": sys.argv[2], # input file of keyway
    "output": sys.argv[3], # output file name
    "k_sensitivity": float(sys.argv[4]), # sensitivity value of key
    "kw_sensitivity": float(sys.argv[5]) # sensitivity value of keyway (how much darkness in photo)
                
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

def remove_holes(pix, x, y):
    streak_size = 10
    current_streak = 0
    current_streak_black = False
    black = False
    
    for i in range(y):
        for j in range(x):
            pixel = pix[j, i][0]
            if pixel == 255: # if the pixel is white
                if black: # if the last pixel was black
                    black = False # is now white
                    current_streak = 0
                else:
                    current_streak += 1
                    if current_streak >= streak_size:
                        current_streak_black = False
            else:
                if not black:
                    black = True
                    current_streak = 0
                else:
                    current_streak += 1
                    if current_streak >= streak_size:
                        current_streak_black = True
            if current_streak_black: #if the current streak is "black"
                pix[j, i] = (0, 0, 0)
            else:
                pix[j, i] = (255, 255, 255)

                
    return pix
                

def main(): # calls other functions and tracks time
    img = open_image(COMM_ARGUMENTS["k_input"])
    x = img.size[0]
    y = img.size[1]
    pix = img.load()

    pix = convert_to_bw(pix, x, y)
    pix = remove_holes(pix, x, y)
    save_image(img, "KEY")

if __name__ == "__main__":
    main()