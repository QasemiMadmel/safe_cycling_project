# verify_braking.py

import math

def verify_braking(acceleration_list, new_acceleration):

    acceleration_threshold = -0.1
    required_amount_of_values = 3

    # add to list until 3 values are available
    if len(acceleration_list) < required_amount_of_values:
        acceleration_list.append(new_acceleration)

    # after four scans and three values for acceleration get rid of the first value:
    else:
        acceleration_list[0] = acceleration_list[1]
        acceleration_list[1] = acceleration_list[2]
        acceleration_list[2] = new_acceleration

    braking_condition = (len(acceleration_list) == required_amount_of_values
        and all(math.isfinite(value) for value in acceleration_list)
        and all(value < acceleration_threshold for value in acceleration_list))

    return acceleration_list, braking_condition
