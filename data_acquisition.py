# data_acquisition.py

import os
import time
import socket
import numpy as np 
import configurations as config
from save_measurement import save_scan
from save_measurement import save_values_x_y
from filename_handler import create_filename, get_common_suffix

# data storage in measurement directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config.suffix = get_common_suffix()
filepath_scan_r = create_filename(BASE_DIR, "scan", config.suffix)
filepath_scan_xy = create_filename(BASE_DIR, "scan_xy", config.suffix)

# default file names (data will be overwritten with each new measurement): 
#filepath_scan_r = create_filename(BASE_DIR, "scan") 
#filepath_scan_xy = create_filename(BASE_DIR, "scan_xy")

class LidarReader: 
        def __init__(self):
                
                # initializing connection to socket 
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
                # connecting port to sensor
                self.sock.connect((config.HOST, config.PORT))
                
                # sending command for data acquisition to sensor 
                self.sock.send(b"\x02sEN LMDscandata 1\x03") 
                
                # buffer for storing the data
                self.buffer = "" 
                
                # calculating the number of angles that the sensor transmits based on steps and number of points
                self.angleDeg_full = config.START_ANGLE + np.arange(config.DISTANCE_POINTS_COUNT) * config.STEP_ANGLE
                
                # limiting the field of view for rapid processing and avoiding redundancies
                self.angleDeg = self.angleDeg_full[config.valid_start:config.valid_stop]
                
                # degrees into radian
                self.angleRad = np.deg2rad(self.angleDeg)
                 
                # defining areas for convenient processing and visualization  
                self.right = (self.angleDeg >= 20)&(self.angleDeg < 60)
                self.front = (self.angleDeg >= 60)&(self.angleDeg < 120)
                self.left = (self.angleDeg >= 120)&(self.angleDeg <=160)

        def getScan(self): 
                
                # variable that controls the amount of iterations
                gotScan = False
                
                while not gotScan:
                    
                    # read up to 4096 bytes
                    data = self.sock.recv(4096)
                    
                    # decode the bytes into ascii 
                    text = data.decode("ascii", errors="ignore")
                    
                    # add the decoded version to the buffer
                    self.buffer += text
                    
                    # search for the end token in the buffer
                    while "\x03" in self.buffer:
                            
                        # mark the ending
                        end = self.buffer.index("\x03")
                        
                        # store all tokens till the end token 
                        telegram = self.buffer[:end+1]
                        
                        # save the remaining tokens
                        self.buffer = self.buffer[end+1:]
                        
                        # remove space from the end and beginning 
                        telegram = telegram.strip()
                        
                        # remove the start and end command from the scan
                        telegram = telegram.replace("\x03","").replace("\x02","")
                        
                        # split all tokens to distinguish between values
                        tokens = telegram.split()
                        
                        # search for keyword to get the distances from the telegram (if not found: continue)
                        if "DIST1" not in tokens:
                            continue
                        
                        # keyword found so take the index
                        i = tokens.index("DIST1")
                        
                        # ignore metadata and store all points
                        #distanceRawValues = tokens[i+6: i+6+config.DISTANCE_POINTS_COUNT]           # for the full field of view
                        distanceRawValues = tokens[i+6+config.valid_start: i+6+config.valid_stop]    # store only specific area 
                        
                        # check if scan has (full fov: 811 points/ limited fov: 421 points)
                        if len(distanceRawValues) != config.valid_length:
                            print("incomplete scan")
                            continue
                        
                        # make a list to store distances
                        distances_list = []
                        for x in distanceRawValues:
                            # convert into integer to store    
                            value = int(x, 16)
                            # add to list
                            distances_list.append(value)
                        
                        # convert list into array of float
                        distances = np.array(distances_list, dtype=np.float32) 
                        
                        r = distances / 1000                            # millimeter to meter
                        x = r * np.cos(self.angleRad)                   # x coordinates
                        y = r * np.sin(self.angleRad)                   # y coordinates
                        # t = time.perf_counter_ns()                     # high resolution counter  
                        t = int(tokens[i-10],16)                        # time from sensor telegram
                        t_log = time.time()                             # time (for logging only)
                        
                        save_scan(filepath_scan_r, r, t_log)            # save scan (time, angle, distance)
                        save_values_x_y(filepath_scan_xy, x, y, t_log)  # save scan (time, x, y)

                        gotScan = True                                  # scan is complete, to stop the iterations set the variable to true
                        return r, x, y, t_log, t                        # return all data 


