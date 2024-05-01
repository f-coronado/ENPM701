import RPi.GPIO as GPIO
import math
import serial
import time
import os
from datetime import datetime
import smtplib
from smtplib import SMTP
from smtplib import SMTPException
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import threading
import multiprocessing

class Localization:

	def __init__(self):
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(12, GPIO.IN, pull_up_down = GPIO.PUD_UP) # setup BR encoder
		GPIO.setup(7, GPIO.IN, pull_up_down = GPIO.PUD_UP) # setup FL encoder

		self.FL_encoder_cnt = []
		self.BR_encoder_cnt = []
		self.counterBR = multiprocessing.Value('i', 0)
		self.counterFL = multiprocessing.Value('i', 0)
		self.priorFL = multiprocessing.Value('i', 5) # why is this 5?
		self.priorBR = multiprocessing.Value('i', 5) # this one too
		self.positions = []

		self.tick_process = multiprocessing.Process(target=self.update_tick_count)
		self.tick_process.daemon=True
		self.tick_process.start()
		print("tick_process started")
		#time.sleep(5)

		# intialize encoder pose
		# initialize x and y to be at center of landing zone
		self.x = 1 # .3028 is a conversion factor to meters
		self.y = 1
		self.angle = 0
		self.x_pos = [self.x]
		self.y_pos = [self.y]

		self.right_x_wall = 10 # update this
		self.left_x_wall = 0
		self.top_y_wall = 10
		self.bottom_y_wall = 0

		# intialize imu angles
		self.x_imu = []
		self.y_imu = []
		self.z_imu = []
		self.prior_imu_angle = 0 # the direction where the robot is pointed initially is 0 degrees
		self.lr_imu_angle = 0 # used to store last recorded imu_angle from thread
		self.ser = serial.Serial('/dev/ttyUSB0', 9600)
		self.imu_angle = 0 # used to get imu_angle from thread
		self.imu_angle_lock = threading.Lock()
		self.imu_thread = threading.Thread(target=self.get_imu_angle)
		self.imu_thread.daemon=True
		self.imu_thread.start()
		self.d_angle = 0
		self.target_angle = 0
		self.start_angle = self.imu_angle

		# variables used for controlling steering
		self.left_adjust = 8
		self.right_adjust = 18
		self.max_diff = .25

		# robot characteristics
		self.R = .018 # track width, double check this
		self.C = .204204 # wheel circumference in meters
		self.gear_ratio = 1/120
		self.ticks_per_mtr_rev = 8

		print("active thread count: ", threading.activeCount())

#		GPIO.setmode(GPIO.BOARD)
#		GPIO.setup(12, GPIO.IN, pull_up_down = GPIO.PUD_UP)
#		GPIO.setup(7, GPIO.IN, pull_up_down = GPIO.PUD_UP)

	def __del__(self):
		self.ser.close()


	def update_tick_count(self):
		print("called update_tick_count")
		while True:
			try:
				input12 = GPIO.input(12)
				input7 = GPIO.input(7)

				with self.counterBR.get_lock():
					#if int(GPIO.input(12)) != int(self.priorBR):
					if input12 != self.priorBR.value:
						self.priorBR.value = input12
						#self.BR_encoder_cnt.append(PIO.input(12))
						self.BR_encoder_cnt.append(input12)
						self.counterBR.value += 1
						#print("BR tick cnt: ", self.counterBR)
				with self.counterFL.get_lock():
					if input7 != self.priorFL.value:
					#if int(GPIO.input(7)) != int(self.priorFL):
						self.priorFL.value = input7
						self.FL_encoder_cnt.append(input7)
						self.counterFL.value += 1
			except Exception as e:
				print("an error occurred in update_tick_count: ", e)
			#time.sleep(.01)

	def get_tick_count(self):
		print("inside get_tick_count")
		print("returning get_tick_count")
		return self.counterFL.value, self.counterBR.value

	def reset_tick_count(self):
		self.counterBR.value = 0
		self.counterFL.value = 0
		self.priorFL = 0
		self.priorBR = 0
		return self.counterBR.value, self.counterFL.value

	def tick_2_distance(self, ticks):
		distance = (ticks / 4687) * 3.28084 # distance in meters, there are 4687 ticks/m
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

	def get_imu_angle(self):
		#global imu_angle
		#ser = serial.Serial('/dev/ttyUSB0', 9600)
		cnt = 0
		while True:
			#time.sleep(.05)
			with self.imu_angle_lock:
				if (self.ser.in_waiting > 0):
					cnt += 1
					line = self.ser.readline()
					#print("get_imu_angle line: ", line)
					if cnt >= 10:
						values = line.split()
						if len(values) >= 3:
							line = self.ser.readline()
							line = line.rstrip().lstrip()
							line = str(line)
							line = line.strip("'")
							line.strip("b'")
							values = line.split()
							values = values[1:]
							values[0] = values[0][:-5]
							values[1] = values[1][:-5]
							x = -float(values[0])
							y = float(values[1])
							z = float(values[2])
							if (x >= 180):
								self.imu_angle = x - 360
							elif x < -180:
								self.imu_angle = x + 360
							else:
								self.imu_angle = x

	def get_angle_dist(self, x, y):
		print("\ncurrent location is x:", self.x, "y:",  self.y, "feet")
		print("currenty pointed at: ", self.lr_imu_angle, "degrees")

		dx = x - self.x
		dy = y - self.y
		target_angle = math.degrees(math.atan2(dy,dx))
		print("target_angle: ", target_angle)
		#turn_angle = target_angle - self.lr_imu_angle
		#print("turn_angle: ", turn_angle)

		#if target_angle <= -180:
		#	turn_angle += 360
		#	print("target_angle < -180, normalizing to: ", turn_angle)
		#elif target_angle > 180:
			#turn_angle -= 180
			#print("target_angle > 180, normalizing to: ", turn_angle)

		distance = math.sqrt(dx**2 + dy **2)
		print("distance to travel is ", distance, "feet")
		print("need to turn to: ", target_angle)
		target_angle = round(target_angle, 3)
		return target_angle, distance



	def email(self):
		# define timestamp and record a image
		pic_time = datetime.now().strftime('%Y%m%d%H%M%S')
		command = 'raspistill -w 1280 -h 720 -vf -hf -o ' + pic_time + '.jpg'
		os.system(command)

		# email info
		smtpUser = 'fabrizzio.enpm701@gmail.com'
		#smtpPass = 'jaw7-bold-imply'
		smtpPass = 'xshy vmsi btcw swvo'

		# destination email info
		toAdd = ['ENPM809TS19@gmail.com', 'jsuriya@umd.edu']
		fromAdd = smtpUser
		subject = 'image recorded at ' + pic_time
		msg = MIMEMultipart()
		msg['Subject'] = subject
		msg['From'] = fromAdd
		#msg['To'] = toAdd
		msg['To'] = ",".join(toAdd)
		msg.preamble = 'Image recorded at ' + pic_time

		# email text
		body = MIMEText("image recorded at " + pic_time)
		msg.attach(body)

		# attach image
		fp = open(pic_time + '.jpg', 'rb')
		img = MIMEImage(fp.read())
		fp.close()
		msg.attach(img)

		# send email
		s = smtplib.SMTP('smtp.gmail.com', 587)
		s.ehlo()
		s.starttls()
		s.ehlo()

		s.login(smtpUser, smtpPass)
		s.sendmail(fromAdd, toAdd, msg.as_string())
		s.quit()

		print("email delivered")



