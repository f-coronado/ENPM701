import matplotlib.pyplot as plt

# Read data from file
filename = "encodercontrol04.txt"  # Update with your file path
with open(filename, 'r') as file:
    lines = file.readlines()

# Parse data
data = [line.strip().split('\t') for line in lines[1:]]  # Skip header line
data = [[int(value) for value in line] for line in data]  # Convert strings to integers

# Extract columns
BRcnt = [row[0] for row in data]
FLcnt = [row[2] for row in data]
GPIO = list(range(len(data)))  # Generate x-axis values based on row index

# Plot data
plt.plot(GPIO, BRcnt, label='BRcnt')
plt.plot(GPIO, FLcnt, label='FLcnt')

# Customize plot
plt.xlabel('GPIO')
plt.ylabel('Count')
plt.title('BRcnt and FLcnt vs. GPIO')
plt.legend()
plt.grid(True)

# Show plot
plt.show()

