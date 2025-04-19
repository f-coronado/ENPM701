from libraries.localization import Localization
from libraries.locomotion import Locomotion
import threading
import time
import serial

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



def main():

	global imu_angle
	imu_thread = threading.Thread(target=get_imu_angle)
	imu_thread.daemon = True
	imu_thread.start()

	local = Localization()
	loco = Locomotion()

	print("starting..")
	time.sleep(2)
	dec = 0.05
	target_angle = 90

	for i in range(4):
		print("i: ", i)
		with imu_angle_lock:
			current_angle = imu_angle
		local.prior_imu_angle = current_angle
#		print("difference in angle: ", abs(local.prior_imu_angle - current_angle))
		print("current angle before turning: ", current_angle)
		duty = 70
		time.sleep(3)

		while True:
			loco.drive([duty, 0, duty, 0])
			with imu_angle_lock:
				current_angle = imu_angle
			if abs(local.prior_imu_angle - current_angle) >= target_angle - 10:
				duty = 40
				#print("updated duty: ", duty)
				#print("abs(local.prior_imu_angle - current_angle: ", abs(local.prior_imu_angle - current_angle))
			if abs(local.prior_imu_angle - current_angle) >= target_angle:
				print("		turned 90 degrees")
				print("		updated current angle: ", current_angle)
				loco.drive([0, 0, 0, 0])
				time.sleep(2)
				break


if __name__ == "__main__":
	main()
