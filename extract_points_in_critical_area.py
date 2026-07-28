# extract_points_in_critical_area.py

def extract_points_in_critical_area(x,y):

    threshold_distance_right = 3
    threshold_distance_sensor = 0.2
    threshold_distance_view = 8
    threshold_distance_left = -0.5

    x_critical = []
    y_critical = []

    for i in range(len(x)):
        if (x[i] > threshold_distance_left and x[i] < threshold_distance_right 
        and y[i] > threshold_distance_sensor and y[i] < threshold_distance_view): 
                x_critical.append(x[i])
                y_critical.append(y[i])
    
    return x_critical, y_critical
