import csv
import time

def save_velocities(filename, velocity_samples):
    timestamp = time.time()
    
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        
        for v in velocity_samples:
            writer.writerow([timestamp, v])
            
def save_scan(filename, distances):
    timestamp = time.time()
    
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        
        for i, d in enumerate(distances):
            writer.writerow([timestamp, i, d])
