import RPi.GPIO as GPIO

class Localization:

	def __init__(self):
		self.FL_encoder_cnt = []
		self.BR_encoder_cnt = []
		self.counterBR = 0
		self.counterFL = 0
		self.priorFL = 5
		self.priorBR = 5
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
