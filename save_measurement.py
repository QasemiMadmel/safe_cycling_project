# save_measuremet.py

import csv
import time

def save_values_x_y(filename, x, y, t):
    
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        
        for value_x, value_y in zip(x, y):
            writer.writerow([t, value_x, value_y])

def save_vx_vy_theta(filename, x, y, t, theta):
    
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        
        for value_x, value_y, angle in zip(x, y, theta):
            writer.writerow([t, value_x, value_y, angle])
    
            
def save_scan(filename, distances, t):
    timestamp = t
    
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        
        for i, d in enumerate(distances):
            writer.writerow([timestamp, i, d])

