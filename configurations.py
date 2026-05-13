# configurations.py

# ipv4
HOST_1 = "192.168.0.2" # sensor 1 
HOST_2 = "192.168.0.3" # sensor 2
HOST = HOST_2 

# 2112:(Cola-Binary), 2111:(Cola-ASCII) 
# choose the port for communication
PORT = 2111  

# constant variables for processing 
DISTANCE_POINTS_COUNT = 811
STEP_ANGLE = 0.3333
START_ANGLE = -45

# limits for the plot (must be adapted based on scenario!)
PLOT_X_LIMIT = 20
PLOT_Y_LIMIT = 20

# filename suffix
suffix = ""

# start and stop indidies for limiting the fov
valid_start = 195
valid_stop = 616
valid_length = valid_stop - valid_start

# thresholds to distiguish direction of velocity (must be adapted through the process)
RIGHT_APPROACH_MIN = 270
RIGHT_APPROACH_MAX = 320

FRONT_APPROACH_MIN = 220
FRONT_APPROACH_MAX = 320

LEFT_APPROACH_MIN = 300
LEFT_APPROACH_MAX = 330
