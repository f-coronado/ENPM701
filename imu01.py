import serial

ser = serial.Serial('/dev/ttyUSB0', 9600) # identify serial connection
cnt = 0

while True:

	if (ser.in_waiting > 0):
		cnt += 1
		line = ser.readline()
		print(line)

		if cnt > 10: # avoid first 10 lines of serial connection
			print("cnt is > 10")
			# strip serial stream of extra characters
			print("before stripping")
			line = line.rstrip().lstrip()
			print(line)

			line = str(line)
			line = line.strip("'") # remove ' from end of line
			line = line.strip("b'") # remove b' from beginning of line
			print("after stripping")
			print(line)

#			line = float(line)
#			print(line, "\n")

			values = line.split()
			print("values: ", values)
			values = values[1:]
			values[0] = values[1][:-5]
			values[1] = values[1][:-5]
			print("values: ", values)
			x = float(values[0])
			y = float(values[1])
			z = float(values[2])

			print("X:", x, "\tY:", y, "\tZ:", z, "\n")
