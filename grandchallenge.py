import RPi.GPIO as GPIO
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import time
from libraries.perception import Perception
from libraries.localization import Localization
from libraries.locomotion import Locomotion

def control(direction, angle=None):

		if direction == "forward": # ie if we are not turning
			# first retrieve initial heading so we keep going that angle
			while True:
					with local.imu_angle_lock:
						start_angle = round(local.imu_angle, 2)
					print("starting angle: ", start_angle)
					start_angle = str(start_angle)
					if '.' in start_angle:
						decimal_index = start_angle.index('.')
						num_decimals = len(start_angle) - decimal_index - 1
						if num_decimals >= 1:
							break
		start_angle = float(start_angle)
		while True:
			with local.imu_angle_lock:
				local.lr_imu_angle = local.imu_angle
			print("start_angle: ", start_angle, "current angle: ", \
			round(local.lr_imu_angle), "distance: ", round(distance, 2), \
			 "counterFL: ", local.counterFL.value, "counterBR: ",local.counterBR.value)
			if local.lr_imu_angle - start_angle >= max_diff: # this mean heading is $
				print("leaning right")
				pin31 = loco.duty - left_adjustment
				pin37 = loco.duty + right_adjustment
				loco.drive([pin31, 0, 0, pin37]) # speed up right wheels
			elif local.lr_imu_angle - start_angle <= -max_diff: # if robot is leanin$
				print("leaning left")
				pin31 = loco.duty  + left_adjustment
				pin37 = loco.duty - right_adjustment
				loco.drive([pin31, 0, 0, pin37]) # speed up right wheels
				distance = local.tick_2_distance(local.counterFL) # check h$
			if distance >= 2: # if traveled 2m break
				print("traveled: ", distance, "meters")
			break

def main():

	### intialization ###

	# classes
	percep = Perception()
	print('loaded perception')
	local = Localization()
	print('loaded localization')
	loco = Locomotion()
	print('loaded locomotion')

	# video parameters
	#cap = cv.VideoCapture(0)
	fourcc = cv.VideoWriter_fourcc(*'mp4v')
	fps = 10
	out_video = cv.VideoWriter("grand_challenge.mp4", fourcc, fps, (640, 480), isColor=True)

	### loop1: look for QR code ###
#	while True:
#		print("looking for qr code..")
#		data = percep.detect_qr_code()
#		if data == "ENPM701":
#			print("starting grand challenge!")
#			break

	### loop2: start ###

	print("starting at: ", local.x, local.y)

	targ_x = float(input("enter x target: "))
	targ_y = float(input("enter y target: "))
	turn_angle , distance = local.get_angle_dist(targ_x, targ_y)
	print("turn angle is: ", turn_angle)
	# turn in this while loop
	while True:
		if turn_angle >= 0: # if we want to turn right
			loco.drive([loco.duty_turn, 0, loco.duty_turn, 0])
			with local.imu_angle_lock:
				local.lr_imu_angle = local.imu_angle
			if local.imu_angle >= turn_angle:
				loco.drive([0, 0, 0, 0]) # stop turning
				break
		elif turn_angle <= 0: # if we want to turn right
			loco.drive([0, loco.duty_turn, 0, loco.duty_turn])
			with local.imu_angle_lock:
				local.lr_imu_angle = local.imu_angle
			if local.imu_angle <= turn_angle:
				loco.drive([0, 0, 0, 0]) # stop turning
				break

	loco.drive([loco.duty, 0, 0, loco.duty])
	i = 0
	# drive forward in this while loop
	while True:
		with local.imu_angle_lock:
			local.lr_imu_angle = local.imu_angle
		print("start_angle: ", start_angle, "current angle: ", \
		round(local.lr_imu_angle), "distance: ", round(distance, 2), \
		"counterFL: ", local.counterFL.value, "counterBR: ", \
		local.counterBR.value)
		if local.lr_imu_angle - start_angle >= max_diff: # if robot leans right
			print("leaning right")
			pin31 = loco.duty - local.left_adjust
			pin37 = loco.duty + local.right_adjust
			loco.drive([pin31, 0, 0, pin37]) # speed up right wheels
		elif local.lr_imu_angle - start_angle <= -max_diff: # if robot leans left
			print("leaning left")
			pin31 = loco.duty  + local.left_adjust
			pin37 = loco.duty - local.right_adjust
			loco.drive([pin31, 0, 0, pin37]) # speed up left wheels
		distance = local.tick_2_distance(local.counterFL.value) # check dist traveled
		if i % 5 == 0:
			current_distance = local.tick_2_distance(\
				local.counterFL.value)
		if current_distance >= distance:
			loco.drive([0, 0, 0, 0])
			break
		i += 1


	### loop3: retrieve and deliver ###










	order = ['r', 'g', 'b', 'r', 'g', 'b', 'r', 'g', 'b']
	for color in order:

		green_edged = perception.detect_color(hsv_frame, green_lower, green_upper)
		cv.imshow('green_edged', green_edged)
		cv.imshow('frame', frame)
		green_contours, cx, cy = perception.detect_contours(green_edged, frame)
		cv.imshow('green_contours', green_contours)
		cv.waitKey(0)
		cv.destroyAllWindows()


if __name__ == "__main__":
	start = time.time()
	main()
	end = time.time()
	print("time taken: ", abs(end - start), "seconds")
