import RPi.GPIO as GPIO
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import time
from libraries.perception import Perception
from libraries.localization import Localization
from libraries.locomotion import Locomotion
import math


### intialization ###

# classes
percep = Perception()
print('loaded perception')
local = Localization()
print('loaded localization')
loco = Locomotion()
print('loaded locomotion')


def relocalize():
	print("\ncalled relocalize!")
	print("robot thinks it's at (x, y): ", local.x, local.y)
	#if local.x <= 4 and local.y >= 6: # if we're in construction zone..

	with local.imu_angle_lock:
		local.lr_imu_angle = local.imu_angle
	print("pointed at ", local.lr_imu_angle, "degrees")

	# turn left until..
	loco.drive([0, loco.duty_turn + 13, 0, loco.duty_turn + 13]) # check
	while True:
		with local.imu_angle_lock:
			local.lr_imu_angle = local.imu_angle
		#print("pointed at ", local.lr_imu_angle, "degrees")

		# if we're facing the left wall break out of while loop
		if local.lr_imu_angle >= 175 or local.lr_imu_angle <= -175:
			print("should be facing left wall now")
			print("angle is: ", local.lr_imu_angle)
			loco.drive([0, 0, 0, 0]) # stop
			break

	local.reset_tick_count()
	print("reset tick count to: ", local.counterFL.value, local.counterBR.value)

	dist2wall = percep.measure_distance()
	print("wall is approx: ", dist2wall, "far")
	if dist2wall >= 2:
		# drive straight to left wall
		loco.drive([loco.duty, 0, 0, loco.duty])
		print("driving to left wall")
		for i in range(10):
			while True:
				avg_tick = (local.counterFL.value + local.counterBR.value) / 2
				enc_dist = local.tick_2_distance(avg_tick)
				#dist2wall = percep.measure_distance()
				if enc_dist >= .35: # if we drove 1 foot towards the wall
					loco.drive([0, 0, 0, 0])
					break
			dist2wall = percep.measure_distance()
			print("dist2wall: ", dist2wall)
			if dist2wall <= 1.95:
				break

	time.sleep(0.5)
	dist_list = []
	for i in range(5):
		dist_list.append(percep.measure_distance())
	dist2wall = sum(dist_list)/len(dist_list) #get avg distance across 3 measurements
	print("left wall is at a distance of: ", dist2wall)
	# measure distance and relocalize x
	local.x = dist2wall
	print("relocalized x to: ", local.x)

	# turn right until..
	loco.drive([loco.duty + 20, 0, loco.duty + 20, 0])
	time.sleep(0.5)
	dist2wall = 1000 # reset so we break out of next loop appropriately
	while True:
		with local.imu_angle_lock:
			local.lr_imu_angle = local.imu_angle
		#print("pointed at ", local.lr_imu_angle, "degrees")
		# if we're facing the top wall break out of while loop
		if local.lr_imu_angle <= 91 :
			print("should be facing top wall now")
			print("angle is: ", local.lr_imu_angle)
			loco.drive([0, 0, 0, 0]) # stop
			break

	local.reset_tick_count()
	print("reset tick count to: ", local.counterFL.value, local.counterBR.value)

	dist2wall = percep.measure_distance()
	print("wall is approx: ", dist2wall , "feet far")

	if dist2wall >= 2:
		# drive straight to top wall
		loco.drive([loco.duty, 0, 0, loco.duty])
		print("driving to top wall")
		for i in range(10):
			while True:
				avg_tick = (local.counterFL.value + local.counterBR.value) / 2
				enc_dist = local.tick_2_distance(avg_tick)
				#dist2wall = percep.measure_distance()
				if enc_dist >= .35: # if we drove 1 foot towards the wall
					loco.drive([0, 0, 0, 0])
					break
			dist2wall = percep.measure_distance()
			print("dist2wall: ", dist2wall)
			if dist2wall <= 1.95:
				break


	time.sleep(1)
	dist_list = []
	for i in range(7):
		dist_list.append(percep.measure_distance())
	dist2wall = sum(dist_list)/len(dist_list)
	print("top wall is at a distance of: ", percep.dist2wall)
	# measure distance and relocalize x
	local.y = 10 - dist2wall
	print("relocalized y to: ", local.y)
	print("final relocalized values x:", local.x, "y: ", local.y)


def get_object(color, frame):
		print("\ncalled get_object()!")
		with local.imu_angle_lock:
			start_angle = local.imu_angle
		print("current position is x: ", local.x, "y:", local.y, "pointed at: ", \
			start_angle)
		edged_frame = percep.detect_color(frame, color)
		frame, cx, cy, edged_frame, w, h = percep.detect_contours(edged_frame, frame)
		cv.imshow("get_object", frame)
		cv.waitKey(30)

		current_distance = 0
		local.reset_tick_count()

		pin31 = loco.duty  # check update
		pin37 = loco.duty # check update
		pin31_opt = pin31
		pin37_opt = pin37
		loco.drive([pin31, 0, 0, pin37]) # drive straight to obj
		j = 0
		while True:
			print("current location is x:", local.x, "y: ", local.y)
			velocity = 0
			if j % 5 and j!= 0:

				velocity = abs(x2 - x1) / abs(t2 - t1)
				print("speed: ", round(velocity, 3))
			t1 = time.time()
			x1 = local.tick_2_distance(local.counterFL.value)

			avg_tick = (local.counterFL.value + local.counterBR.value) / 2
			current_distance = local.tick_2_distance(avg_tick)
			print("dist traveled: ", current_distance)

			frame = percep.get_pic()
			edged_frame = percep.detect_color(frame, color)
			frame, cx, cy, edged_frame, w, h = percep.detect_contours(edged_frame, frame)

			# if the object was lost
			if w == 0 and h == 0: # maybe make this a list check
				print("lost object..")
				loco.drive([0, 0, 0, 0])
				cv.destroyAllWindows()
				avg_tick = (local.counterFL.value + local.counterBR.value) / 2
				distance = local.tick_2_distance(avg_tick)
				print("distance traveled inside of get_object(): ", \
				distance)

				# update position before returning
				local.x = local.x + distance * math.cos(math.radians(\
					start_angle))
				local.y = local.y + distance * math.sin(math.radians(\
					start_angle))
				print("current location is x: ", local.x, "y: ", local.y)
				print("updating coordinates x:", local.x, "y: ", local.y)
				while True:
					ans = input("check coords")
					if ans == 'y':
						break

				if cx <= 320:
					return "left"
				else:
					return "right"

### begin perception steering ###
			if w >= 35 and h >= 50: # start perception to steer
				print("using camera to steer")
				print("pin31: ", pin31, "pin37: ", pin37)
				with local.imu_angle_lock:
					local.lr_imu_angle = local.imu_angle
				if percep.get_angle2center(cx) >= 2: # if obj to right more than 7 degrees
					print("obj is to the right ", cx, "degrees")
					# stop recenter then drive to it again
					loco.drive([0, 0, 0, 0]) # stop
					look4color(color, None, 135) # recenter object
					loco.drive([0, 0, 0, 0]) # stop turning
				elif percep.get_angle2center(cx) <= -2: # if obj to left more than 7 degrees
					print("pin31: ", pin31, "pin37: ", pin37)
					print("obj is to left ", cx, "degrees")
					loco.drive([0, 0, 0, 0]) # stop
					look4color(color, 135, None) # recenter object
					loco.drive([0, 0, 0, 0]) # stop turning

				loco.drive([loco.duty, 0, 0, loco.duty]) # drive straight

				if percep.object_check(w, h) is "open": # obj is near
					print("object is near, opening gripper")
					loco.drive([0, 0, 0, 0]) # stop
					loco.grip("open") # open gripper
					break
### imu steering ###
			else: # use imu to steer until close to obj then we'll switch to percep
				print("using imu to steer")
				with local.imu_angle_lock:
					local.lr_imu_angle = local.imu_angle
				# update position as we go?
				print("curr angle: ", round(local.lr_imu_angle, 4), "curr_dist: ",\
					round(current_distance, 2), "counterFL: ", \
					local.counterFL.value, "counterBR: ", \
					local.counterBR.value, "x:", round(local.x, 3), "y: ", \
					round(local.y, 3))

				#current_distance = local.tick_2_distance(local.counterFL.value)
				# if robot leans right
				if local.lr_imu_angle - start_angle <= -local.max_diff: 
					#if velocity >= local.max_vel:
					#	pin31 -= 1
					#	pin37 -= 1
					#	pin31_opt = pin31 # use this optimal val below
					#	pin37_opt = pin37
						# we must assign here because we no longer adjust
					print("leaning right")
					pin31 = loco.duty - local.left_adjust
					pin37 = loco.duty + local.right_adjust
					print("pin31: ", pin31, "pin37: ", pin37)
					loco.drive([pin31, 0, 0, pin37]) # speed up right wheels
				# if robot leans left
				elif local.lr_imu_angle - start_angle >= local.max_diff:
					#if velocity >= local.max_vel:
					#	pin31 -= 1
					#	pin37 -= 1
					#	pin31_opt = pin31 # use this optimal val below
					#	pin37_opt = pin37
						# we must assign here because we no longer adjust
					#else:
					print("leaning left")
					pin31 = loco.duty + local.left_adjust
					pin37 = loco.duty - local.right_adjust
					print("pin31: ", pin31, "pin37: ", pin37)
					loco.drive([pin31, 0, 0, pin37]) # speed up left wheels

			x2 = local.tick_2_distance(local.counterFL.value)
			t2 = time.time()
			j += 1

		print("obj should be close and centered enough by now")
		#while True:
			#print("robot thinks it's at x: ", local.x, "y: ", local.y)
			#ans = input("is object close enough and aligned?")
			#if ans == 'y':
			#	break
		# obj should be close and center enough by now
		loco.drive([loco.duty - 10, 0, 0, loco.duty - 10]) # drive straight
		while True:
			frame = percep.get_pic()
			edged = percep.detect_color(frame, color)
			frame, cx, cy, _, w, h = percep.detect_contours(edged, frame)
			#print("w: ", w, "h: ", h)
			#object is close enough so...
			if percep.object_check(w, h) is "grip":
				print("object is within grasp")
				while True:
					# record angle before driving straight
					with local.imu_angle_lock:
						local.lr_imu_angle = local.imu_angle
					loco.drive([loco.duty, 0, 0, loco.duty]) # drive to grab object
					_, _ = local.get_tick_count() # update tick count
					# 3 inches = .0732m, and 4687 ticks/m
					avg_tick = (local.counterFL.value + \
							local.counterBR.value)/2
					dist = local.tick_2_distance(avg_tick)
					if dist >= .8: # if we drove almost 1ft
						break
				loco.grip("close")
				loco.drive([0, 0, 0, 0])
				local.email(frame)
				avg_tick = (local.counterFL.value + local.counterBR.value) / 2
				distance = local.tick_2_distance(avg_tick)
				print("distance traveled inside of get_object(): ", \
				distance)

				# update position before returning
				local.x = local.x + distance * math.cos(math.radians(\
					start_angle))
				local.y = local.y + distance * math.sin(math.radians(\
					start_angle))
				print("current location is x: ", local.x, "y: ", local.y)
				print("current heading: ", local.lr_imu_angle)

				while True:
					ans = input("check coords")
					if ans == 'y':
						break
				return True
			# if the object was lost
			elif w == 0 and h == 0:
				print("lost object..")
				loco.drive([0, 0, 0, 0])
				avg_tick = (local.counterFL.value + local.counterBR.value) / 2
				distance = local.tick_2_distance(avg_tick)
				print("distance traveled inside of get_object(): ", \
					distance)

				# update position before returning
				local.x = local.x + distance * math.cos(math.radians(\
					start_angle))
				local.y = local.y + distance * math.sin(math.radians(\
					start_angle))
				print("elif w==0 and h == 0")
				print("current location is x: ", local.x, "y: ", local.y)
				while True:
					ans = input("check coords")
					if ans == 'y':
						break
				if cx <= 320:
					return "left"
				else:
					return "right"
				#return False


def look4colorv2(color, lt_angle, rt_angle):
	return


def look4color(color, lt_angle, rt_angle):
	print("\ncalled look4color!")

	if color == "green":
		lower = percep.green_lower
		upper = percep.green_upper
	elif color == "red":
		lower = percep.red_lower
		upper = percep.red_upper
	elif color == "blue":
		lower = percep.blue_lower
		upper = percep.blue_upper

	# update prior imu_angle
	with local.imu_angle_lock:
		local.prior_imu_angle = local.imu_angle
	print("angle before turning left is: ", local.prior_imu_angle)

	if lt_angle is not None: # if we want to turn left
		print("turning left to: ", lt_angle, "degrees")
		# start turning left
		pin33 = loco.duty_turn - 5 # check
		pin37 = loco.duty_turn - 5 # check
		loco.drive([0, pin33, 0, pin37]) # check

		i = 0

		while True:
			frame = percep.get_pic() # look for obj
			# check for object
			edged = percep.detect_color(frame, color)

			# turning control logic
			t1 = time.time()

			if i != 0:
				with local.imu_angle_lock:
					local.lr_imu_angle = local.imu_angle
				# th1 is local.lr_imu_angle
				angle_roc = abs(th2 - local.lr_imu_angle) / abs(t2 - t1)
				print("rate of change in angle is: ", angle_roc)
				if angle_roc >= local.high_angle_roc:
					print("decreasing left turn speed..")
					if angle_roc >= local.max_angle_roc:
						pin33 -= 5.5 # check all these
						pin37 -= 5.5
					else:
						pin33 -= 1.5
						pin37 -= 1.5
					loco.drive([0, pin33, 0, pin37])
					#loco.drive([0, pin33, 0, loco.duty_turn - 17])
				elif angle_roc <= local.min_angle_roc:
					pin33 += .75
					pin37 += .75
					print("increasing left turn speed..")
					loco.drive([0, pin33, 0, pin37])
					#loco.drive([0, loco.duty_turn - 5, 0, loco.duty_turn - 5])


			if percep.detect_contours(edged, frame) is not None:
				frame, cx, cy, edged, w, h = percep.detect_contours(edged, frame)
				if abs(percep.get_angle2center(cx)) <= 10: # check
					# slow down
					loco.drive([0, pin33 - 4, 0, pin37 - 4]) # check

				# if object is close to center
				with local.imu_angle_lock:
						local.lr_imu_angle = local.imu_angle
				if abs(percep.get_angle2center(cx)) <= 4: # check
					loco.drive([0, 0, 0, 0]) # stop
					# get obj angle

					print("bot is pointed at: ",local.lr_imu_angle, "degrees")
					#while True:
					#	ans = input("exiting look4color, want to continue?")
					#	if ans == 'y':
					#		break
					return True, frame
					#get_object(color, frame) # consider moving this out?

			# get current angle
			with local.imu_angle_lock:
				local.lr_imu_angle = local.imu_angle
			print("current angle: ", local.lr_imu_angle)
			th2 = local.lr_imu_angle
			t2 = time.time()

			# check this 
			# if the bot has turned left > lt_angle
			if local.lr_imu_angle >= lt_angle:
				print("turned left to:", local.imu_angle, "degrees")
				frame = percep.get_pic()
				#out.write(frame)
				break # break out of loop to start turning right
			i += 1 ## end of left turn while loop ##

	i = 0 # reset for use in next while loop
	with local.imu_angle_lock:
		local.prior_imu_angle = local.imu_angle
	#print("initial angle: ", local.prior_imu_angle)


	if rt_angle is not None:
		print("turning right to: ", lt_angle, "degrees")
		# start turning right, thise config works best when batteries are not fully charged
		pin31 = loco.duty_turn
		pin35 = loco.duty_turn
		loco.drive([pin31, 0, pin35, 0]) # check
		while True:
			frame = percep.get_pic()
			edged = percep.detect_color(frame, color)

			# turning control logic
			t1 = time.time()

			if i != 0:
				with local.imu_angle_lock:
					local.lr_imu_angle = local.imu_angle
				# th1 is local.lr_imu_angle
				angle_roc = abs(th2 - local.lr_imu_angle) / abs(t2 - t1)
				print("rate of change in angle is: ", round(angle_roc, 2))
				if angle_roc >= local.high_angle_roc:
					print("decreasing right turn speed..")
					if angle_roc >= local.max_angle_roc:
						pin31 -= 5.5 #check
						pin35 -= 5.5
					else:
						pin31 -= 1.5
						pin35 -= 1.5
					loco.drive([pin31, 0, pin35, 0])
				elif angle_roc <= local.min_angle_roc:
					pin31 += .75
					pin35 += .75
					print("increasing right turn speed..")
					loco.drive([pin31, 0, pin35, 0])


			# if we found the object
			if percep.detect_contours(edged, frame) is not None:
				frame, cx, cy, edged, w, h = percep.detect_contours(edged, frame)
				if abs(percep.get_angle2center(cx)) <= 15: # check
					# slow down
					loco.drive([loco.duty_turn, 0, loco.duty_turn, 0])
				text = "obj is" + str(percep.get_angle2center(cx)) + "degrees from center"
				frame = percep.write_on_frame(frame, text)
				# if object is close to center
				with local.imu_angle_lock:
					local.lr_imu_angle = local.imu_angle
				if abs(percep.get_angle2center(cx)) <= 4:
					loco.drive([0, 0, 0, 0]) # stop
					print("obj is at: ", local.lr_imu_angle, "degrees")
					#while True:
					#	ans = input("exiting look4color want to continue?: ")
					#	if ans == 'y':
					#		break
					return True, frame
					#get_object(color, frame) # consider moving this out of this function?

			# get current angle
			with local.imu_angle_lock:
				local.lr_imu_angle = local.imu_angle
			print("current angle: ", local.lr_imu_angle)
			th2 = local.lr_imu_angle
			t2 = time.time()

			# check this if statement
			print("prior_imu_angle: ", local.prior_imu_angle)
			print("lr_imu_angle: ", local.lr_imu_angle)
			if local.lr_imu_angle <= rt_angle:
				print("turned right to ", local.lr_imu_angle, "degrees")
				frame = percep.get_pic()
				#out.write(frame)
				break
			i += 1 ## end of right turn while loop ##
	return False, frame


def drive2(targ_x, targ_y):
	print("\ncalled drive2!")
	print("starting at: ", local.x, local.y)
	with local.imu_angle_lock:
		local.prior_imu_angle = local.imu_angle
	print("pointed at: ", local.prior_imu_angle)
	target_angle , distance = local.get_angle_dist(targ_x, targ_y)
	print("target angle is: ", target_angle)
	print("driving to x: ", targ_x, "y: ", targ_y)
	while True:
		ans = input("want to continue? enter y or n: ")
		if ans == 'y':
			break

	# turn in this while loop
	while True:
		if abs(target_angle - local.lr_imu_angle - 2) <= 6:
			print("pointed at ", target_angle ,\
				"breaking out of turning loop")
			loco.drive([0, 0, 0, 0])
			time.sleep(1)
			break
		elif target_angle <= 0: # if we want to turn right
			loco.drive([loco.duty_turn + 20, 0, loco.duty_turn + 20, 0])
			with local.imu_angle_lock:
				local.lr_imu_angle = local.imu_angle
			if abs(local.imu_angle - target_angle) <= 1: #current angle is more negative
				loco.drive([0, 0, 0, 0]) # stop turning
				break
		elif target_angle > 0: # if we want to turn left
			loco.drive([0, loco.duty_turn + 20, 0, loco.duty_turn + 20])
			with local.imu_angle_lock:
				local.lr_imu_angle = local.imu_angle
			if abs(local.imu_angle - target_angle - 4) <= 1: # check this
				loco.drive([0, 0, 0, 0]) # stop turning
				break

	i = 0
	print("\nresetting FL, BR tick count to: ", local.reset_tick_count())
	time.sleep(0.5)
	with local.imu_angle_lock:
		start_angle = local.imu_angle
	print("before driving straight, record the reference angle: ", start_angle)
	current_distance = 0
	print("current_distance: ", current_distance)

	while True:
		ans = input("want to continue? enter y or n: ")
		if ans == 'y':
			break
	inc = 40
	loco.drive([loco.duty + inc, 0, 0, loco.duty + inc]) # drive straight

	# drive forward in this while loop
	while True:
		with local.imu_angle_lock:
			local.lr_imu_angle = local.imu_angle
		# update position as we go?
		#local.x = current_distance * math.cos(math.radians(local.lr_imu_angle))
		#local.y = current_distance * math.sin(math.radians(local.lr_imu_angle))
		#print("curr angle: ", round(local.lr_imu_angle, 4), "curr_dist: ",\
		#round(current_distance, 2), " target_dist: ", round(distance, 2), \
		#"counterFL: ", local.counterFL.value, "counterBR: ", \
		#local.counterBR.value, "x:", round(local.x, 3), "y: ", round(local.y, 3))
		#print("distance from wall: ", round(percep.measure_distance(), 2))
		if local.lr_imu_angle - start_angle <= -local.max_diff: # if robot leans right
			print("leaning right")
			pin31 = loco.duty + inc - local.left_adjust
			pin37 = loco.duty + inc + local.right_adjust
			loco.drive([pin31, 0, 0, pin37]) # speed up right wheels
		elif local.lr_imu_angle - start_angle >= local.max_diff: # if robot leans left
			print("leaning left")
			pin31 = loco.duty  + inc + local.left_adjust
			pin37 = loco.duty + inc - local.right_adjust
			loco.drive([pin31, 0, 0, pin37]) # speed up left wheels
		if i % 2 == 0: # update current distance every other iteration
			tick_avg = (local.counterFL.value + local.counterBR.value) / 2
			current_distance = local.tick_2_distance(tick_avg)
		# once we start to get within 2 feet of the x walls, and we're pointed at it
		# we should measure distance to relocalize the x coordinate
		#if local.right_x_wall - local.x <= 2 and -.5 <= local.lr_imu_angle <= .5: # once we get within 2 feet of the right wall
		#	dist = percep.measure_distance()
		#	print("wall is at a distance of: ", init_dist, "cm")
		#	local.x = local.right_x_wall - dist
		if current_distance + .28 >= distance:
			loco.drive([0, 0, 0, 0])
			break
		i += 1
	print("local.lr_imu_angle: ", local.lr_imu_angle)
	local.x = local.x + distance * math.cos(math.radians(local.lr_imu_angle))
	local.y = local.y + distance * math.sin(math.radians(local.lr_imu_angle))
	print("distance traveled was: ", distance)
	print("x: ", local.x, "y: ", local.y)

	## end of drive2(x, y)
def turn2(angle):
	print("called turn2! ")
	with local.imu_angle_lock:
		local.lr_imu_angle = local.imu_angle
	print("pointed at: ", local.lr_imu_angle)
	# turn right
	if local.lr_imu_angle >= angle:
		loco.drive([loco.duty_turn + 30, 0, loco.duty_turn + 30, 0])
		while True:
			with local.imu_angle_lock:
				local.lr_imu_angle = local.imu_angle
			if local.lr_imu_angle <= angle:
				break
	# turn left
	else:
		loco.drive([0, loco.duty_turn + 30, 0, loco.duty_turn + 30])
		while True:
			with local.imu_angle_lock:
				local.lr_imu_angle = local.imu_angle
			if local.lr_imu_angle >= angle:
				break
	loco.drive([0, 0, 0, 0])
	print("exiting turn2, pointed at: ", local.lr_imu_angle)

def main():


	# video parameters
	#cap = cv.VideoCapture(0)
	fourcc = cv.VideoWriter_fourcc(*'mp4v')
	fps = 10
	out_video = cv.VideoWriter("grand_challenge.mp4", fourcc, fps, (640, 480), isColor=True)

	while True:
		with local.imu_angle_lock:
			local.lr_imu_angle = local.imu_angle
		lr_imu_angle_str = str(local.lr_imu_angle)
		print("local.imu_angle: ", local.imu_angle)
		decimal_idx = lr_imu_angle_str.find('.') # find position of decimal pt
		if decimal_idx != -1:
			decimal_places = len(lr_imu_angle_str) - decimal_idx - 1
			print("decimal_places: ", decimal_places)
			if decimal_places != 0:
				break

	i = 0
	order = ['green', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red'] # update
	for color in order:
		start = time.time()
		### 2: look4color ###
		with local.imu_angle_lock:
			local.lr_imu_angle = local.imu_angle
		print("\nlooking for", color, "blocks i: ", i)
		print("pointed at: ", local.lr_imu_angle)
		while True:
			if i == 0:
				print("x: ", local.x, "y: ", local.y)
				obj_found, frame = look4color(color, 90, 0)
			else:
				print("x: ", local.x, "y: ", local.y)
				obj_found, frame = look4color(color, None, -90)

			if obj_found is True:
				print("found obj, robot is pointing: ", local.imu_angle)
				break
			# update : what if the obj is not found?: look again through this same loop

		### 3: get_object ###
		while True:
			grabbed_obj=get_object(color, frame)
			if grabbed_obj is True:
				break
			elif grabbed_obj is not True:
				print("lost object, need to look again")
				print("currently at: x: ", local.x, "y: ", local.y)
				local.reset_tick_count()
				# reverse 1 ft
				loco.drive([0, loco.duty, loco.duty])
				while True:
					avg_tick = (local.counterFL.value + \
						local.counterBR.value) / 2
					reverse_dist = local.tick_2_distance(avg_tick)
					if reverse_dist >= 1:
						loco.drive([0, 0, 0, 0])
						break

					with local.imu_angle_lock:
						local.lr_imu_angle = local.imu_angle
				local.x -= reverse_dist * math.cos(math.radians(local.lr_imu_angle))
				local.y -= reverse_dist * math.sin(math.radians(local.lr_imu_angle))
				print("x: ", local.x, "y: ", local.y)
				while True:
					ans = input("do the updated coordinates after reversinglook right after reversing?")
					if ans == 'y':
						break
				if grabbed_obj == "left":
					obj_found = look4color(color, \
						local.lr_imu_angle + 45, 0)
				else:
					obj_found = look4color(color, 0, \
						local.lr_imu_angle - 45)
				#print("obj_found is: ", obj_found)

		### deliver ###
		drive2(2, 8)
		relocalize()
		loco.drive([0, 0, 0, 0])
		loco.grip("open")
		frame = percep.get_pic()
		local.email(frame)
		local.reset_tick_count()
		print("reversing")
		loco.drive([0, loco.duty_turn + 20, loco.duty_turn + 20, 0])
		while True:
			avg_tick = (local.counterFL.value + \
				local.counterBR.value) / 2
			reverse_dist = local.tick_2_distance(avg_tick)
			print("reverse_dist: ", reverse_dist)
			if reverse_dist >= 1: # if we backed out 1 ft
				loco.drive([0, 0, 0, 0])
				print("breaking out of reverse loop")
				local.y = local.y - reverse_dist - .50 # check update .75
				print("backed up, should be at x:" , local.x, "y: ", local.y)
				break
		loco.grip("close")
		turn2(10)

		while True:
			ans = input("check location")
			if ans == 'y':
				break

		# turn right until we face landing zone
		#print("turning to landing zone")
		#loco.drive([loco.duty_turn + 20, 0, loco.duty_turn + 20, 0]) # check
		#while True:
			#print("local.lr_imu_angle: ", local.lr_imu_angle)
			#with local.imu_angle_lock:
				#local.lr_imu_angle = local.imu_angle
			#if local.lr_imu_angle <= 0:
				#loco.drive([0, 0, 0, 0]) # stop turning
				#print("breaking out of right turn to landing loop")
				#break
		end = time.time()
		print("time taken to get block", i, ":", abs(start - end))
		i += 1

def main2():

	while True:
		with local.imu_angle_lock:
			local.lr_imu_angle = local.imu_angle
		lr_imu_angle_str = str(local.lr_imu_angle)
		print("local.imu_angle: ", local.imu_angle)
		decimal_idx = lr_imu_angle_str.find('.') # find position of decimal pt
		if decimal_idx != -1:
			decimal_places = len(lr_imu_angle_str) - decimal_idx - 1
			print("decimal_places: ", decimal_places)
			if decimal_places != 0:
				break
	frame = percep.get_pic()
	get_object("green", frame)


def main3():
	while True:
		with local.imu_angle_lock:
			local.lr_imu_angle = local.imu_angle
		lr_imu_angle_str = str(local.lr_imu_angle)
		print("local.imu_angle: ", local.imu_angle)
		decimal_idx = lr_imu_angle_str.find('.') # find position of decimal pt
		if decimal_idx != -1:
			decimal_places = len(lr_imu_angle_str) - decimal_idx - 1
			print("decimal_places: ", decimal_places)
			if decimal_places != 0:
				break
	relocalize()

def main4():
	while True:
		with local.imu_angle_lock:
			local.lr_imu_angle = local.imu_angle
		lr_imu_angle_str = str(local.lr_imu_angle)
		print("local.imu_angle: ", local.imu_angle)
		decimal_idx = lr_imu_angle_str.find('.') # find position of decimal pt
		if decimal_idx != -1:
			decimal_places = len(lr_imu_angle_str) - decimal_idx - 1
			print("decimal_places: ", decimal_places)
			if decimal_places != 0:
				break

	colorList = ["green", "red", "green", "red"]

	for color in colorList:
		print("looking for ", color)
		if color == "green":
			color_found, frame = look4color(color, 120, 0)
		elif color == "red":
			color_found, frame = look4color(color, 0, -120)
		print("color_found = ", color_found)
		#if color_found == True:
		#	grabbed_obj = get_object("green", frame)

def main5():
	while True:
		with local.imu_angle_lock:
			local.lr_imu_angle = local.imu_angle
		lr_imu_angle_str = str(local.lr_imu_angle)
		print("local.imu_angle: ", local.imu_angle)
		decimal_idx = lr_imu_angle_str.find('.') # find position of decimal pt
		if decimal_idx != -1:
			decimal_places = len(lr_imu_angle_str) - decimal_idx - 1
			print("decimal_places: ", decimal_places)
			if decimal_places != 0:
				break

	frame = percep.get_pic()
	color = "green"

	while True:
		grabbed_obj=get_object(color, frame)
		if grabbed_obj is True:
			break
		elif grabbed_obj is not True:
			print("lost object, need to look again")
			print("currently at: x: ", local.x, "y: ", local.y)
			local.reset_tick_count()
			# reverse 1 ft
			loco.drive([0, loco.duty, loco.duty])
			while True:
				avg_tick = (local.counterFL.value + \
					local.counterBR.value) / 2
				reverse_dist = local.tick_2_distance(avg_tick)
				if reverse_dist >= 1:
					loco.drive([0, 0, 0, 0])
					break

				with local.imu_angle_lock:
					local.lr_imu_angle = local.imu_angle
			# believe this is right
			local.x -= reverse_dist * math.cos(math.radians(local.lr_imu_angle))
			local.y -= reverse_dist * math.sin(math.radians(local.lr_imu_angle))
			print("x: ", local.x, "y: ", local.y)
			while True:
				ans = input("do the updated coordinates look right after reversing?")
				if ans == 'y':
					break
			if grabbed_obj == "left":
				obj_found = look4color(color, \
					local.lr_imu_angle + 45, 0)
			else:
				obj_found = look4color(color, 0, \
					local.lr_imu_angle - 45)
			#print("obj_found is: ", obj_found)

def main6():
	frame = percep.get_pic()
	local.email(frame)

if __name__ == "__main__":
	start = time.time()
	main()
	#main2()
	#main3()
	#main4()
	#main5()
	#main6()
	end = time.time()
	print("time taken: ", abs(end - start), "seconds")
