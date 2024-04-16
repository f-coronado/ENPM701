import RPi.GPIO as GPIO
import math
import serial
import time

class Localization:

	def __init__(self):
		self.FL_encoder_cnt = []
		self.BR_encoder_cnt = []
		self.counterBR = 0
		self.counterFL = 0
		self.priorFL = 5
		self.priorBR = 5
		self.positions = []

		# intialize encoder pose
		# initialize x and y to be at center of landing zone
		self.x = 2 * .3028
		self.y = 2 * .3028
		self.angle = 0
		self.x_pos = [self.x]
		self.y_pos = [self.y]

		# intialize imu angles
		self.x_imu = []
		self.y_imu = []
		self.z_imu = []
		self.ser = serial.Serial('/dev/ttyUSB0', 9600) # identify serial connection

		# robot characteristics
		self.R = .018 # track width, double check this
		self.C = .204204 # wheel circumference in meters
		self.gear_ratio = 1/120
		self.ticks_per_mtr_rev = 8

#		GPIO.setmode(GPIO.BOARD)
#		GPIO.setup(12, GPIO.IN, pull_up_down = GPIO.PUD_UP)
#		GPIO.setup(7, GPIO.IN, pull_up_down = GPIO.PUD_UP)

	def get_tick_count(self):
		if int(GPIO.input(12)) != int(self.priorBR):
			self.priorBR = int(GPIO.input(12))
			self.BR_encoder_cnt.append(GPIO.input(12))
			self.counterBR += 1

		if int(GPIO.input(7)) != int(self.priorFL):
			self.priorFL = int(GPIO.input(7))
			self.FL_encoder_cnt.append(GPIO.input(7))
			self.counterFL += 1

		return self.counterBR, self.counterBR

	def reset_tick_count(self):
		self.counterBR = 0
		self.counterFL = 0
		self.priorFL = 0
		self.priorBR = 0
		return self.counterBR, self.counterFL

	def tick_2_distance(self, ticks):
		distance = ticks / 4687 # distance in meters, there are 4687 ticks/m
		return distance

	def angle_2_ticks(self, angle):

		ticks = angle * self.R * (1/self.C) * 1/self.gear_ratio * self.tick_per_mtr_rev
		return ticks

	def ticks_2_angle(self, ticks):

		angle = ticks * (1/self.ticks_per_mtr_rev) * self.gear_ratio * self.C * (1/self.R)
		return angle

	def update_enc_pos(self, distance): # update angles then append for plotting
		self.x += distance * math.cos(self.angle)
		self.x_pos.append(self.x)
		self.y += distance * math.sin(self.angle)
		self.y_pos.append(self.y)

		return self.x, self.y

	def update_enc_angle(self, theta, turn):
		print("self.angle = ", self.angle)
		if turn == 'l':
			self.angle += theta # in radians
		if turn == 'r':
			self.angle -= theta
		if turn == 'f' or turn == 'b':
			return

	def get_imu_angle(self, ser, cnt):

		while True:
			#print("ser: ", ser.in_waiting)
			if (ser.in_waiting > 0):
				cnt += 1
				line = self.ser.readline()
				print(line)

				if cnt > 10:
#					print("cnt > 10")
#					print("before stripping")
					line = line.rstrip().lstrip()
					print(line)

					line = str(line)
					line = line.strip("'")
					line.strip("b'")
#					print("after stripping")
					print(line)

					values = line.split()
					print("values before reassigning: ", values)
					values = values[1:]
					values[0] = values[0][:-5]
					values[1] = values[1][:-5]
					print("values after reassinging: ", values)
					x = float(values[0])
					y = float(values[1])
					z = float(values[2])

					print("X:", x, "Y:", y, "Z:", z)

					self.x_imu.append(x)
					self.y_imu.append(y)
					self.z_imu.append(z)
					break


		return x
