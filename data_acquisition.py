# data_acquisition.py

import time
import socket
import numpy as np 
import configurations as config
from save_measurement import save_scan
from save_measurement import save_values_x_y
import os
from filename_handler import create_filename, get_common_suffix

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

config.suffix = get_common_suffix()

filepath_scan_r = create_filename(BASE_DIR, "scan", config.suffix)
filepath_scan_xy = create_filename(BASE_DIR, "scan_xy", config.suffix)

#filepath_scan_r = create_filename(BASE_DIR, "scan")
#filepath_scan_xy = create_filename(BASE_DIR, "scan_xy")

class LidarReader: 
        def __init__(self):
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print((config.HOST, config.PORT))
                self.sock.connect((config.HOST, config.PORT))

                self.sock.send(b"\x02sEN LMDscandata 1\x03") 

                self.buffer = "" 

                self.angleDeg = config.START_ANGLE + np.arange(config.DISTANCE_POINTS_COUNT) * config.STEP_ANGLE
                self.angleRad = np.deg2rad(self.angleDeg) 
        
        def getScan(self): 
                gotScan = False
                while not gotScan:

                    data = self.sock.recv(4096)
                    
                    text = data.decode("ascii", errors="ignore")
                    self.buffer += text
                    
                    while "\x03" in self.buffer:
                        end = self.buffer.index("\x03")
                        telegram = self.buffer[:end+1]
                        self.buffer = self.buffer[end+1:]
                        
                        telegram = telegram.strip()
                        telegram = telegram.replace("\x03","").replace("\x02","")
                        tokens = telegram.split()
                        
                        if "DIST1" not in tokens:
                            continue
                        
                        i = tokens.index("DIST1")
                        
                        distanceRawValues = tokens[i+6: i+6+config.DISTANCE_POINTS_COUNT]
                        if len(distanceRawValues) != config.DISTANCE_POINTS_COUNT:
                            print("incomplete scan")
                            continue
                        
                        distances_list = []
                        for x in distanceRawValues:
                            value = int(x, 16)
                            distances_list.append(value)
                        
                        distances = np.array(distances_list, dtype=np.float32) 
                        
                        r = distances / 1000
                        x = r * np.cos(self.angleRad)
                        y = r * np.sin(self.angleRad)
                        t = time.time()
                        
                        save_scan(filepath_scan_r, r, t)
                        save_values_x_y(filepath_scan_xy, x, y, t)

                        gotScan = True
                        return r, x, y, t


