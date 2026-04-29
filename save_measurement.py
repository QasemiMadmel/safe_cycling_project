# save_measuremet.py

import csv
import time

def save_values_x_y(filename, x, y, t):
    
    # open file in append mode
    with open(filename, "a", newline="") as f:
        
        # use csv writer
        writer = csv.writer(f)
        
        # iterrate over two lists and write the values iin the file
        for value_x, value_y in zip(x, y):
            writer.writerow([t, value_x, value_y])

def save_vx_vy_theta(filename, x, y, t, theta):
    
    # open file in append mode
    with open(filename, "a", newline="") as f:
        
        # use csv writer
        writer = csv.writer(f)
        
        # iterate over three lists: vx, vy and theta and write into file 
        for value_x, value_y, angle in zip(x, y, theta):
            writer.writerow([t, value_x, value_y, angle])
            
def save_scan(filename, distances, t):

    # open file in append mode
    with open(filename, "a", newline="") as f:
        
        # use csv writer
        writer = csv.writer(f)
        
        # save all distances with an index (numebr of points for each scan!)
        for i, d in enumerate(distances):
            writer.writerow([t, i, d])

