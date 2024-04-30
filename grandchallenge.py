import RPi.GPIO as GPIO
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import time
from libraries.perception import Perception
from libraries.localization import Localization
from libraries.locomotion import Locomotion

def get_object(color, frame):
		print("\ngetting obj")
		start = time.time()
		edged_frame = percep.detect_color(frame, color)
		frame, cx, cy, edged_frame, w, h = percep.detect_contours(edged_frame, frame)
		end = time.time()
		print("time taken to capture edge and contour within get_object", end-start)

		while True:
			frame = percep.get_pic()
			loco.drive([loco.duty, 0, 0, loco.duty]) # drive straight to obj
			edged_frame = percep.detect_color(frame, color)
			frame, cx, cy, edged_frame, w, h = percep.detect_contours(edged_frame, frame)
			print("cx: ", cx, "angle2center: ", percep.get_angle2center(cx))
			if percep.get_angle2center(cx) >= 7: # if obj to right more than 7 degrees
				print("obj is to right ", cx, "degrees")
				# turn right 
				loco.drive([loco.duty_turn - 10, 0, loco.duty_turn - 10, 0])
				while True:
					frame = percep.get_pic()
					edged = percep.detect_color(color)
					frame, cx, cy, edged, w, h = perception.detect_contours(edged, frame)
					if cx <= 7:
						break
			elif percep.get_angle2center(cx) <= -7: # if obj to left more than 7 degrees
				print("obj is to left ", cx, "degrees")
				# turn left
				loco.drive([0, loco.duty_turn - 10, 0,  loco.duty_turn - 10])
				while True:
					frame = percep.get_pic()
					edged = percep.detect_color(color)
					frame, cx, cy, edged, w, h = perception.detect_contours(edged, frame)
					if percep.get_angle2center(cx) >= -7:
						break
			cv.imshow("frame: ", frame)
			cv.waitKey(30)
			if percep.object_check(w, h) is "open": # obj is near
				print("object is near, opening gripper")
				loco.drive([0, 0, 0, 0]) # stop
				loco.grip("open") # open gripper
				break

		print("obj should be close and centered enough by now")
		# obj should be close and center enough by now
		loco.drive([loco.duty, 0, 0, loco.duty])
		while True:
			frame = percep.get_pic()
			edged = percep.detect_color(frame, color)
			frame, cx, cy, _, w, h = percep.detect_contours(edged, frame)
			cv.imshow("frame", frame)
			cv.waitKey(30)
			print("w: ", w, "h: ", h)
			# if w > 100 and h > 145
			#object is close enough so...
			if percep.object_check(w, h) is "grip":
				#print("object is within grasp")
				#loco.drive([0, 0, 0, 0]) # stop
				#loco.grip("open") # open before we drive object into gripper opening
				#time.sleep(2)
				#start = time.time()

				while True:
					loco.drive([40, 0, 0, 40]) # drive to grab object
					_, _ = local.get_tick_count() # update tick count
					#print("driving into object to grasp")
					# 3 inches = .0732m, and 4687 ticks/m
					if local.counterFL >= .0762 * 4687:
						break
				end = time.time()
				print("time taken through while loop in get_object: ", end-start)
				loco.grip("close")
				loco.drive([0, 0, 0, 0])
				time.sleep(3)
				return True



def look4color(color):

		if color == "green":
			lower = percep.green_lower
			upper = percep.green_upper
		elif color == "red":
			lower = percep.red_lower
			upper = percep.red_upper
		elif color == "blue":
			lower = percep.blue_lower
			upper = percep.blue_upper

		with local.imu_angle_lock:
			local.prior_imu_angle = local.imu_angle
		#print("initial angle: ", local.prior_imu_angle)
		#time.sleep(3)
		right_turn = 90
		left_turn = 180

		while True:
			frame = percep.get_pic()
			# turn right 90 degrees and look for the color obj
			loco.drive([loco.duty_turn - loco,reduce, 0, loco.duty_turn - loco,reduce, 0])
			# get edged frame
			edged = percep.detect_color(frame, color)
			# if we found the object
			#if percep.detect_contours(edged, frame) is not None:
			frame, cx, cy, edged, w, h = percep.detect_contours(edged, frame)
			#print("contours is not none")
			text = "obj is" + str(percep.get_angle2center(cx)) + "degrees from center"
			frame = percep.write_on_frame(frame, text)
			cv.imshow("contours: ", frame)
			cv.waitKey(30)
			# and the obj is close to the center
			#print("angle2center: ", percep.get_angle2center(cx))
			if abs(percep.get_angle2center(cx)) <= 2:
				loco.drive([0, 0, 0, 0]) # stop
				print("cx: ", cx, "cy: ", cy)
				#cv.imshow("centerd obj", frame)
				time.sleep(10)
				print("waiting before get_object")
				get_object(color, frame)
				time.sleep(10000)

			# get current angle
			with local.imu_angle_lock:
				local.lr_imu_angle = local.imu_angle
			print("current angle: ", local.lr_imu_angle)
			# else if the bot has turned right > 90 degrees
			if abs(local.prior_imu_angle - local.lr_imu_angle) >= right_turn:
				print("turned right by 90 degrees")
				frame = percep.get_pic()
				#out.write(frame)
				break

		# update prior imu_angle
		with local.imu_angle_lock:
			local.prior_imu_angle = local.imu_angle
		print("updated angle is: ", local.prior_imu_angle)

		while True:
			frame = percep.get_pic() # look for obj
			loco.drive([0, loco.duty_turn - loco,reduce, 0, loco.duty_turn - loco,reduce]) # turn left
			# check for object
			edged = percep.detect_color(frame, color)
			if percep.detect_contours(edged, frame) is not None:
				frame, cx, cy, edged, w, h = percep.detect_contours(edged, frame)
				print("contours is not none")
				cv.imshow("contours: ", frame)
				cv.waitKey(30)
				# and the obj is close to the center
				print("angle2center: ", percep.get_angle2center(cx))
				if abs(percep.get_angle2center(cx)) <= 2:
					loco.drive([0, 0, 0, 0]) # stop
					print("cx: ", cx, "cy: ", cy)
					cv.imshow("centerd obj", frame)
					print("waiting before get_object")
					get_object(color, frame)
					time.sleep(10000)

			# get current angle
			with local.imu_angle_lock:
				local.lr_imu_angle = local.imu_angle
			print("current angle: ", local.lr_imu_angle)

			# if the bot has turned left > 180 degrees
			if abs(local.prior_imu_angle - local.lr_imu_angle) >= left_turn:
				print("turned left by 180 degrees")
				frame = percep.get_pic()
				#out.write(frame)
				break



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
