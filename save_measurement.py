import csv
import time

def save_velocities_radial(filename, velocity_samples):
    timestamp = time.time()
    
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        
        for v in velocity_samples:
            writer.writerow([timestamp, v])
            

def save_values_x_y(filename, x, y, t):
    timestamp = t
    
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        
        for value_x, value_y in zip(x, y):
            writer.writerow([timestamp, value_x, value_y])
    
            
def save_scan(filename, distances, t):
    timestamp = t
    
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        
        for i, d in enumerate(distances):
            writer.writerow([timestamp, i, d])

