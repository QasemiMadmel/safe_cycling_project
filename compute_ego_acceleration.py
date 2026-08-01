# compute_ego_acceleration 

def compute_ego_acceleration(previous_velocity_value, current_velocity_value, dt): 
	
	if dt <= 0 or previous_velocity_value is None or current_velocity_value is None: 
		return None 
	
	acceleration = (current_velocity_value - previous_velocity_value) / dt
	return acceleration
