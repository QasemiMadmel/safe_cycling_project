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

def save_vx_vy(filename, vx, vy, v, t):
    
    # open file in append mode
    with open(filename, "a", newline="") as f:
        
        # use csv writer
        writer = csv.writer(f)
        
        # iterate over four lists: vx, vy, v and theta and write into file 
        for value_vx, value_vy, value_v in zip(vx, vy, v):
            writer.writerow([t, value_vx, value_vy, value_v])
            
def save_scan(filename, distances, t):

    # open file in append mode
    with open(filename, "a", newline="") as f:
        
        # use csv writer
        writer = csv.writer(f)
        
        # save all distances with an index (numebr of points for each scan!)
        for i, d in enumerate(distances):
            writer.writerow([t, i, d])


def save_median_and_ego_velocity_estimation(filename, t, median_right, ego_velocity):
    
    # open file in append mode
    with open(filename, "a", newline="") as f:
        
        # use csv writer
        writer = csv.writer(f)
        writer.writerow([t, median_right, ego_velocity])
         
            
def save_rssi(filepath, rssi, t_log):
    
    # open file in append mode
    with open(filepath, "a") as f:

        for val in rssi:

            f.write(f"{t_log},{val}\n") # time, intensity
