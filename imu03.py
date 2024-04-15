import serial
import RPi.GPIO as GPIO
from libraries.localization import Localization
from libraries.locomotion import Locomotion
import matplotlib.pyplot as plt
import time

def init():

        gpio.setmode(gpio.BOARD)
        gpio.setup(31, gpio.OUT) # IN1
        gpio.setup(33, gpio.OUT) # IN2
        gpio.setup(35, gpio.OUT) # IN3
        gpio.setup(37, gpio.OUT) # IN4

def main():

	locomotion = Locomotion()
	localization = Localization()
	ser = serial.Serial('/dev/ttyUSB0', 9600) # identify serial connection
	cnt = 0
	time.sleep(4)

	sequence = input("Enter a sequence of commands separated by spaces. \nAvailable commands are: f, b, r, l:\n").split()
	print("the sequence of commands entered was: \n", sequence)

	max_count = 2343 # ticks needed for half a meter
	turn_count = 975 # ticks needed for about 90 degrees
	duty = 40
	duty_turn = 100
	enc_distances = []
	total_distance = 0

	for command in sequence:
		print("\ncommand: ", command)
		cntrBR = 0
		cntrFL = 0
		localization.reset_tick_count()


		if command == 'r' or command == 'l':
			while cntrBR <= turn_count and cntrFL <= turn_count:
				if command == 'l':
					locomotion.drive([0, duty_turn, 0, duty_turn])
					print("cntrBR, cntrFL: ", cntrBR, cntrFL)


				elif command == 'r':
					locomotion.drive([duty_turn, 0, duty_turn, 0])
					print("cntrBR: ", cntrBR, "cntrFL: ", cntrFL)

				cntrBR, cntrFL = localization.get_tick_count()
				if cntrBR and cntrFL >= turn_count:
					theta = 1.5707 # 90 degrees in radians
					localization.update_enc_angle(theta, command)
					locomotion.gameover()
					print("cntrBR: ", cntrBR, "cntrFL: ", cntrFL)
					avg_tick = (cntrBR + cntrFL) / 2
					print("current encoder angle: ", localization.angle)
					print("imu coords: ", localization.get_imu_coords(ser, cnt))
					cntrBR, cntrFL = localization.reset_tick_count()
					break


		if command == 'f' or command == 'b':
			while cntrBR <= max_count and cntrFL <= max_count:

				if command == 'f':
					locomotion.drive([duty, 0, 0, duty])
					print("driving forward")
					print("cntrBR: ", cntrBR, "cntrFL: ", cntrFL)

				elif command == 'b':
					locomotion.drive([0, duty, duty, 0])
					print("driving forward")
					print("cntrBR: ", cntrBR, "cntrFL: ", cntrFL)

				cntrBR, cntrFL = localization.get_tick_count()
				if cntrBR and cntrFL >= max_count:
					locomotion.gameover()
					avg_tick = (cntrBR + cntrFL) / 2
					print("avg_tick: ", avg_tick)

					if command == 'f' or command == 'b':
						if command == 'f':
							distance = localization.tick_2_distance(avg_tick)
						if command == 'b':
							distance = -localization.tick_2_distance(avg_tick)
						print("current distance travelled: ", distance)
						enc_distances.append(distance)
						localization.update_enc_angle(0, command)
						print("current encoder angle is: ", localization.angle)
						print("imu coords: ", localization.get_imu_coords(ser, cnt))
						localization.update_enc_pos(distance)
						print("current position is at: ", localization.x, localization.y)
						counterBR, counterFL = localization.reset_tick_count()
						total_distance += distance
						print("total distance is at: ", total_distance)


					break

	print("\ncommand sequence: ", sequence)
	print("distances travelled: ", enc_distances)

	localization.gamover()

	enc_positions =list(zip(localization.x_pos, localization.y_pos))
	print("enc_positions: ", enc_positions)
	plt.plot(localization.x_pos, localization.y_pos)
	plt.title('plot of encoder positions')
	plt.xlabel('x [meters]')
	plt.ylabel('y [meters]')
	plt.grid(True)
	plt.show()

	imu_positions = list(zip(localization.x_imu, localization.y_imu))
	print("imu_positions: ", imu_positions)
	plt.plot(localization.x_imu, localization.y_imu)
	plt.title('plot of imu positions')
	plt.xlabel('x [meters]')
	plt.ylabel('y [meters]')
	plt.grid(True)
	plt.show()

if __name__ == "__main__":
	main()
