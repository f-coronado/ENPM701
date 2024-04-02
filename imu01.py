import serial

ser = serial.Serial('/dev/ttyUSB0', 9600) # identify serial connection
cnt = 0

while True:

	if (ser.in_waiting > 0):
		cnt += 1
		line = ser.readline()
		print(line)

		if cnt > 10: # avoid first 10 lines of serial connection

			# strip serial stream of extra characters
			line = line.rstrip().lstrip()
			print(line)

			line = str(line)
			line = line.strip("'")
			line = line.strip("b'")
			print(line)

			line = float(line)
			print(line, "\n")
