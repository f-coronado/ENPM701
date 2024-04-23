import serial
import time
import threading

imu_angle = 0.0
imu_angle_lock = threading.Lock()


def get_imu_angle():
	global imu_angle
	ser = serial.Serial('/dev/ttyUSB0', 9600)
	cnt = 0
	while True:
		if (ser.in_waiting > 0):
			cnt += 1
			line = ser.readline()

			if cnt > 10:

				line = ser.readline()
				line = line.rstrip().lstrip()
				line = str(line)
				line = line.strip("'")
				line.strip("b'")
				values = line.split()
				values = values[1:]
				values[0] = values[0][:-5]
				values[1] = values[1][:-5]
				x = float(values[0])
				y = float(values[1])
				z = float(values[2])
				if (x >= 180):
					imu_angle = x - 360
				else:
					imu_angle = x

#		shared_variable.acquire()
#		shared_variable.value = imu_angle
#		shared_variable.release()

def main():
	global imu_angle

#	shared_variable = threading.Value('f', 0.0)
#	imu_angle = 0

	# start imu thread
	imu_thread = threading.Thread(target=get_imu_angle)
	imu_thread.daemon = True
	imu_thread.start()

	print("starting..")
	time.sleep(2)

	# get current angle from imu
	with imu_angle_lock:
		current_angle = imu_angle
	print("starting angle is: ", current_angle)
	print("waiting 5s..")
	time.sleep(5)

	with imu_angle_lock:
		current_angle = imu_angle
	print("updated angle is: ", current_angle)
	print("waiting 5s..")
	time.sleep(5)

	with imu_angle_lock:
		current_angle = imu_angle
	print("updated angle is: ", current_angle)
	print("waiting 5s..")
	time.sleep(5)

	with imu_angle_lock:
		current_angle = imu_angle
	print("updated angle is: ", current_angle)
	print("waiting 5s..")
	time.sleep(5)

if __name__ == "__main__":
	main()
