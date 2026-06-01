# extract_points_in_critical_area.py

def extract_points_in_critical_area(x,y):

    threshold_max = 3
    threshold_min = 0.2
    x_critical = []
    y_critical = []
    for i in range(len(x)):
        if x[i] > threshold_min and x[i] < threshold_max:
            if y[i] > threshold_min and y[i] < threshold_max: 
                x_critical.append(x[i])
                y_critical.append(y[i])
    return x_critical, y_critical
