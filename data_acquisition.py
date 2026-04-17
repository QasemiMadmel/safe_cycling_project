# data_acquisition.py

import time
import socket
import numpy as np 
import configurations as config


class LidarReader: 
        def __init__(self):
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((config.HOST, config.PORT))

                # SICK comand to start transmission
                self.sock.send(b"\x02sEN LMDscandata 1\x03") 

                self.buffer = "" #buffer to store telegrams

                # comupte the angles in rad 
                self.angleDeg = config.START_ANGLE + np.arange(config.DISTANCE_POINTS_COUNT) * config.STEP_ANGLE
                self.angleRad = np.deg2rad(self.angleDeg) 
        
        def getScan(self): 
                gotScan = False
                while not gotScan:
                    # get data from port
                    data = self.sock.recv(4096)
                    
                    # decode as ascii and store in buffer
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
                        
                        # convert all hex values into integer
                        distances_list = []
                        for x in distanceRawValues:
                            value = int(x, 16)
                            distances_list.append(value)
                        
                        # convert list into python array (float valeus) for better calculation
                        distances = np.array(distances_list, dtype=np.float32) 
                        
                        # compute the polar coordinates for visualization
                        r = distances / 1000
                        x = r * np.cos(self.angleRad)
                        y = r * np.sin(self.angleRad)
                        t = time.time()

                        gotScan
                        return r, x, y, t


