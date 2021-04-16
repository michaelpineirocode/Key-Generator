from PIL import Image
import numpy as np
from stl import stl, mesh
import sys
import time
import math

COMM_ARGUMENTS = { # global dict of com. line arguments for easier reference
    "input" : sys.argv[1], # input file name
    "output": sys.argv[2], # output file name
    "sensitivity": float(sys.argv[3]) # sensitivity value
                }

def open_image(input_):
    img = Image.open("Pics/Inputs/" + input_)
    return img

def mean(pixel):
    sum_ = sum(pixel)
    average = int(sum_ / 3)
    return average

def bw(pixel):
    gray = mean(pixel)
    if gray < 127 * COMM_ARGUMENTS["sensitivity"]:
        return (0, 0, 0)
    else:
        return (255, 255, 255)

def convert_to_bw(pix, x, y):
    for i in range(y):
        for j in range(x):
            pixel = pix[j, i]
            pix[j, i] = bw(pixel)
    return pix

def save_image(img):
    img.save("Pics/Outputs/" + COMM_ARGUMENTS["output"] + ".png")

def main(): # calls other functions and tracks time
    img = open_image(COMM_ARGUMENTS["input"])
    x = img.size[0]
    y = img.size[1]
    pix = img.load()

    pix = convert_to_bw(pix, x, y)
    save_image(img)

if __name__ == "__main__":
    main()