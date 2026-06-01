# save_measuremet.py

import csv

def save_values_x_y(filename, t, x, y):
    
    # open file in append mode
    with open(filename, "a", newline="") as f:
        
        # use csv writer
        writer = csv.writer(f)
        
        # iterate over two lists and write the values in the file
        for value_x, value_y in zip(x, y):
            writer.writerow([t, value_x, value_y])

def save_vx_vy(filename, t, vx, vy, v):
    
    # open file in append mode
    with open(filename, "a", newline="") as f:
        
        # use csv writer
        writer = csv.writer(f)
        
        # iterate over four lists: vx, vy, v and theta and write into file 
        for value_vx, value_vy, value_v in zip(vx, vy, v):
            writer.writerow([t, value_vx, value_vy, value_v])
            
def save_scan(filename, t, distances):

    # open file in append mode
    with open(filename, "a", newline="") as f:
        
        # use csv writer
        writer = csv.writer(f)
        
        # save all distances with an index (numebr of points for each scan!)
        for i, d in enumerate(distances):
            writer.writerow([t, i, d])


def save_ego_velocity(filename, t, ego_velocity):
    
    # open file in append mode
    with open(filename, "a", newline="") as f:
        
        # use csv writer
        writer = csv.writer(f)
        writer.writerow([t, ego_velocity])
         

