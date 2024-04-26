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
		self.prior_imu_angle = 0 # the direction where the robot is pointed initially is 0 degrees
		self.lr_imu_angle = 0 # used to store last recorded imu_angle from thread
		self.imu_angle = 0 # used to get imu_angle from thread
		self.imu_angle_lock = threading.Lock()
		self.imu_thread = threading.Thread(target=self.get_imu_angle)
		self.imu_thread.daemon=True
		self.imu_thread.start()
		self.d_angle = 0
		self.target_angle = 0

		#self.ser = serial.Serial('/dev/ttyUSB0', 9600) # identify serial connection

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

		return self.counterFL, self.counterBR

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

	def get_imu_angle(self):
		#global imu_angle
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
						self.imu_angle = x - 360
					else:
						self.imu_angle = x


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



