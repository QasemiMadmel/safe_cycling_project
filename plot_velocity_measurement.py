import matplotlib.pyplot as plt
import csv

timestamps = []
values = []

with open("velocities.csv", "r") as f:
    reader = csv.reader(f)
    
    for row in reader:
        timestamps.append(float(row[0]))
        values.append(float(row[1]))

plt.plot(values)
plt.title("Velocity Plot")
plt.xlabel("Sample")
plt.ylabel("Velocity")
plt.show()
