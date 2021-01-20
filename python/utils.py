from collections import deque       #BFS iterator
import argparse                     #command line argument
import csv                          #read color data
import os.path                      #open files to convert
import os                           #find cwd
import re                           #find regex
import sys                          #command line argument
import time                         #record performance

def gap(a,b) :
    """return abs(b-a)"""
    return abs(a-b)

def is_float(token) :
    """check if the token can be convert in float"""
    try :
        f = float(token)
        return True
    except :
        return False

def get_color_name(data_colors,red,green,blue) :
    """return a color name corresponding to the r,g,b"""
    minn = float("inf")
    minn_name = "no name"
    for name, (r,g,b) in data_colors.items() :
        score = (
            gap(red,r)**2 + 
            gap(green,g)**2 + 
            gap(blue,b)**2
        )

        if score < minn :
            minn = score
            minn_name = name

    return minn_name
