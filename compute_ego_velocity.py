# compute_ego_velocity.py

import numpy as np
from get_velocities import get_x_y_velocities

def compute_ego_velocity(previous_median, previous_x_values, current_x, previous_y_values, current_y, dt, timestamp, alpha, beta):
	
	# calculate the velocities
	vx, vy, v = get_x_y_velocities(previous_x_values, current_x, previous_y_values, current_y, dt, timestamp)        
	
	# use only the values for the right side of sensor for median 
	v_right = v[0:212]
	valid_v_right = v_right[np.isfinite(v_right)]

	# get the median value for velocity at the right side of the sensor where cars overtake
	if valid_v_right.size > 0:
		current_median_right_area = np.nanmedian(valid_v_right)
	else: 
		current_median_right_area = np.nan
	
	if np.isnan(current_median_right_area):
	   current_median_right_area = previous_median
	
	# filter the velocity median values and store the estimated velocites in a csv file
	ego_velocity_estimation = alpha * current_median_right_area + beta * previous_median  
	
	return ego_velocity_estimation
