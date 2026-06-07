# extract_points_in_critical_area.py

def extract_points_in_critical_area(x,y):

    threshold_max_side = 3
    threshold_min_side = 0.2
    
    threshold_max_back_x = 1.5
    threshold_min_back_x = -0.5
    threshold_max_back_y = 4
    threshold_min_back_y = 0.2
    
    x_critical = []
    y_critical = []

    
    for i in range(len(x)):
        if x[i] > threshold_min_side and x[i] < threshold_max_side:
            if y[i] > threshold_min_side and y[i] < threshold_max_side: 
                x_critical.append(x[i])
                y_critical.append(y[i]) 
        elif x[i] > threshold_min_back_x and x[i] < threshold_max_back_x:
            if y[i] > threshold_min_back_y and y[i] < threshold_max_back_y:
                x_critical.append(x[i])
                y_critical.append(y[i]) 
    return x_critical, y_critical
