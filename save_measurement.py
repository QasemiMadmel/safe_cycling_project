# save_measuremet.py

import csv

def save_values_x_y(filename, x, y, t):
    
    # open file in append mode
    with open(filename, "a", newline="") as f:
        
        # use csv writer
        writer = csv.writer(f)
        
        # iterate over two lists and write the values iin the file
        for value_x, value_y in zip(x, y):
            writer.writerow([t, value_x, value_y])

def save_vx_vy_theta(filename, vx, vy, v, t, theta):
    
    # open file in append mode
    with open(filename, "a", newline="") as f:
        
        # use csv writer
        writer = csv.writer(f)
        
        # iterate over four lists: vx, vy, v and theta and write into file 
        for value_vx, value_vy, value_v, angle in zip(vx, vy, v, theta):
            writer.writerow([t, value_vx, value_vy, value_v, angle])
            
def save_scan(filename, distances, t):

    # open file in append mode
    with open(filename, "a", newline="") as f:
        
        # use csv writer
        writer = csv.writer(f)
        
        # save all distances with an index (numebr of points for each scan!)
        for i, d in enumerate(distances):
            writer.writerow([t, i, d])

import csv

def save_median(filename, r, rt, lt, l):
    
    # open file in append mode
    with open(filename, "a", newline="") as f:
        
        # use csv writer
        writer = csv.writer(f)

        values = [r, rt, lt, l]

        for i, value in enumerate(values, start=1):
            writer.writerow([i, value])

def save_rssi(filepath, rssi, t_log):
    
    # open file in append mode
    with open(filepath, "a") as f:

        for val in rssi:

            f.write(f"{t_log},{val}\n") # time, intensity
