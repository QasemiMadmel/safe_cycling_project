# data_acquisition.py

import os
import time
import socket
import numpy as np 
import configurations as config
from save_measurement import save_scan
from save_measurement import save_values_x_y
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
                
                self.sock.connect((config.HOST, config.PORT))

                self.sock.send(b"\x02sEN LMDscandata 1\x03") 

                self.buffer = "" 

                self.angleDeg_full = config.START_ANGLE + np.arange(config.DISTANCE_POINTS_COUNT) * config.STEP_ANGLE
                self.angleDeg = self.angleDeg_full[config.valid_start:config.valid_stop]
                self.angleRad = np.deg2rad(self.angleDeg)
                 
                self.right = (self.angleDeg >= 20)&(self.angleDeg < 60)
                self.front = (self.angleDeg >= 60)&(self.angleDeg < 120)
                self.left = (self.angleDeg >= 120)&(self.angleDeg <=160)

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
                        
                        #distanceRawValues = tokens[i+6: i+6+config.DISTANCE_POINTS_COUNT]
                        distanceRawValues = tokens[i+6+config.valid_start: i+6+config.valid_stop]
                        
                        if len(distanceRawValues) != config.valid_length:
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
                        t = time.perf_counter_ns()
                        t_log = time.time()
                        
                        save_scan(filepath_scan_r, r, t_log)
                        save_values_x_y(filepath_scan_xy, x, y, t_log)

                        gotScan = True
                        return r, x, y, t_log, t


