import RPi.GPIO as GPIO
import math

class Localization:

	def __init__(self):
		self.FL_encoder_cnt = []
		self.BR_encoder_cnt = []
		self.counterBR = 0
		self.counterFL = 0
		self.priorFL = 5
		self.priorBR = 5
:
		R = .018 # track width, double check this
		C = .204204 # wheel circumference in meters
		gear_ratio = 1/120
		tick_per_mtr_rev = 8

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

	def tick_2_distance(self, ticks):
		distance = ticks / 4687 # distance in meters, there are 4687 ticks/m
		return distance

	def angle_2_ticks(self, angle)

		ticks = angle * self.R * (1/self.C) * self.gear_ratio * self.tick_per_mtr_rev
		return ticks

	def ticks_2_angle(self, ticks):
		
		angle = ticks * (1/self.ticks_per_mtr_rev) * (1/self.gear_ratio) * self.C * (1/self.R)
		return angle

	def update_enc_pos(self, x, y, distance, angle):
		x += distance * math.cos(math.radians(angle))
		y += distance * math.sin(math.radians(angle))

		return x, y

	def update_enc_angle(self, ticks, angle):
		angle = 0
		


	def get_angle_imu(self, cnt, serial):

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
				angle = float(line)
				print(line, "\n")

			return cnt, angle
