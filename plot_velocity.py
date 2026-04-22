import matplotlib.pyplot as plt
import csv
import os 


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
measurement_dir = os.path.join(BASE_DIR, "measurements")
os.makedirs(measurement_dir, exist_ok=True)

filepath_radial = os.path.join(measurement_dir, "radial_velocities.csv")
filepath_xy = os.path.join(measurement_dir, "22042026_velocities_x_y.csv_perf_counter_static_environment_home.csv")

def plot_radial_velocities():
    timestamps = []
    values = []

    with open(filepath_radial, "r") as f:
        reader = csv.reader(f)

        for row in reader:
            timestamps.append(float(row[0]))
            values.append(float(row[1]))

    plt.figure()
    plt.plot(values)
    plt.title("Radial Velocity")
    plt.xlabel("Sample")
    plt.ylabel("Velocity")
    plt.show()


def plot_x_y_velocities():
    timestamps = []
    values_x = []
    values_y = []

    with open(filepath_xy, "r") as f:
        reader = csv.reader(f)

        for row in reader:
            timestamps.append(float(row[0]))
            values_x.append(float(row[1]))
            values_y.append(float(row[2]))

    plt.figure()
    plt.plot(values_x, label="Velocity X")
    plt.plot(values_y, label="Velocity Y")
    plt.title("Velocity X and Y")
    plt.xlabel("Sample")
    plt.ylabel("Velocity")
    plt.legend()
    plt.show()
    
    
plot_x_y_velocities()    
# plot_radial_velocities()
