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
	loco.drive([0, 40, 0, 40])
	while True:
		with local.imu_angle_lock:
			local.lr_imu_angle = local.imu_angle
		print("pointed at ", local.lr_imu_angle, "degrees")
		# if we're facing the left wall
		if local.lr_imu_angle >= 175 or local.lr_imu_angle <= -175:
			print("should be facing left wall now")
			loco.drive([0, 0, 0, 0]) # stop
			break

	# drive straight to left wall
	loco.drive([loco.duty, 0, 0, loco.duty])
	print("driving to left wall")
	while True:
		# if we're closer than 1.2 feet from the wall
		if percep.dist2wall.value <= 1.2:
			loco.drive([0, 0, 0, 0])
			print("left wall is at a distance of: ", percep.dist2wall.value)
			 # measure distance and relocalize x
			local.x = percep.dist2wall.value
			print("relocalized x to: ", local.x)
			break


#	elif local.x <= 5: # if robot is closer to left wall
#		with local.imu_angle_lock:
#			local.lr_imu_angle = local.imu_angle # check what direction we're looking
#		print("current angle: ", local.lr_imu_angle)
#		time.sleep(1)
#		loco.drive([0, loco.duty_turn + 8, 0, loco.duty_turn + 5]) # turn left
#		while True:
#			with local.imu_angle_lock:
#				local.lr_imu_angle = local.imu_angle # check what direction we're lookin
#			if local.lr_imu_angle >= 179: # turn until we face left wall
#				break 
#		loco.drive([0, 0, 0, 0]) # stop turning
#		time.sleep(1)
#		loco.drive([loco.duty, 0, 0, loco.duty]) # drive straight to left wall
#		while True:
#			if local.x <= 1.95: # if we're within 2 feet of the left wall
#				break

#	elif local.x <= 2: # if robot is near left wall
#		with local.imu_angle_lock:
#			local.lr_imu_angle = local.imu_angle # check what direction we're looking
#		if 0 <= local.lr_imu_angle <= 180: # if robot is facing anywhere in 
						  # NE or NW quadrant
#			local.drive([0, loco.duty_turn + 8, 0, loco.duty_turn + 5]) # turn left
#			while True: # turn until..
#				with local.imu_angle_lock:
#					local.lr_imu_angle = local.imu_angle
#				if local.lr_imu_angle >= 180: # facing left wall so break
#					break
#		elif -180 <= local.lr_imu_angle <= 0: # if robot is facing anywhere in 
						   # SE or SW quadrant
#			local.drive([loco.duty_turn + 10, 0, loco.duty_turn + 8, 0]) # turn right
#			while True: # turn until..
#				with local.imu_angle_lock:
#					local.lr_imu_angle = local.imu_angle
#				if local.lr_imu_angle <= -180: # facing left wall so break
#					break
#		loco.drive([0, 0, 0, 0])
#		time.sleep(2)
#		local.x = percep.measure_distance()
#		print("relocalizing x to: ", local.x)
#
#	elif local.x >= 8: # if robot is near right wall
#		with local.imu_angle_lock:
#			local.lr_imu_angle = local.imu_angle # check what direction we're looking
#		if 0 <= local.lr_imu_angle <= 180: # if robot is facing anywhere in NE quadrant
						  # or NW quadrant
#			local.drive([loco.duty_turn + 8, 0, loco.duty_turn + 5, 0]) # turn right
#			while True: # turn until..
#				with local.imu_angle_lock:
#					local.lr_imu_angle = local.imu_angle
#				if local.lr_imu_angle <= 1: # facing right wall so break
#					break
#		elif -180 <= local.lr_imu_angle <= 0: # if robot is facing anywhere in 
						     # SE or SW quadrant
#			local.drive([0, loco.duty_turn + 8, 0, loco.duty_turn + 5]) # turn left
#			while True: # turn until..
#				with local.imu_angle_lock:
#					local.lr_imu_angle = local.imu_angle
#				if local.lr_imu_angle <= -180: # facing left wall so break
#					break
#		loco.drive([0, 0, 0, 0])
#		time.sleep(2)
#		local.x = percep.measure_distance()
#		print("relocalizing x to: ", local.x)

def deliver():

	print("\ncalled deliver!")
	with local.imu_angle_lock:
		local.lr_imu_angle = local.imu_angle
	print("using tracking, currently located at x: ", local.x, "y: ", local.y, \
		"pointed at: ", local.lr_imu_angle)

	# relocalize
	relocalize()

	loco.grip("open") # drop off object

	print("reversing out of construction zone!")
	loco.drive([0, loco.duty, 0, loco.duty])
	# reverse until we're 
#	while True:



def get_object(color, frame):
		print("\ncalled get_object()!")
		with local.imu_angle_lock:
			start_angle = local.imu_angle
		print("current position is x: ", local.x, "y:", local.y, "pointed at: ", \
			start_angle)
		start = time.time()
		edged_frame = percep.detect_color(frame, color)
		frame, cx, cy, edged_frame, w, h = percep.detect_contours(edged_frame, frame)
		end = time.time()
		print("time taken to capture edge and contour within get_object", end-start)

		current_distance = 0
		local.reset_tick_count()
		print("tick count before driving straight in get_obj: ", local.counterFL.value, \
			local.counterBR.value)

		pin31 = loco.duty
		pin37 = loco.duty
		pin31_opt = pin31
		pin37_opt = pin37
		loco.drive([pin31, 0, 0, pin37]) # drive straight to obj
		j = 0
		while True:

			velocity = 0
			if j != 0:
				velocity = abs(x2 - x1) / abs(t2 - t1)
				print("speed: ", round(velocity, 3))
				#if velocity >= local.max_vel:
				#	pin31 -= 1
				#	pin37 -= 1
				#	print("lower pin31 to: ", pin31, "pin37 to: ", pin37)
				#	loco.drive([pin31, 0, 0, pin37])
			t1 = time.time()
			x1 = local.tick_2_distance(local.counterFL.value)

			frame = percep.get_pic()
			edged_frame = percep.detect_color(frame, color)
			frame, cx, cy, edged_frame, w, h = percep.detect_contours(edged_frame, frame)
			#print("angle2center: ", percep.get_angle2center(cx), \
			#	"obj width: ", w, "height: ", h)
			#cv.imshow("contours", frame)
			#cv.waitKey(30)
### begin perception steering ###
			if w >= 35 and h >= 50: # start perception to steer
				print("using camera to steer")
				print("pin31: ", pin31, "pin37: ", pin37)
				with local.imu_angle_lock:
					local.lr_imu_angle = local.imu_angle
				if percep.get_angle2center(cx) >= 4: # if obj to right more than 7 degrees
					print("obj is to the right ", cx, "degrees")
					# stop recenter then drive to it again
					loco.drive([0, 0, 0, 0]) # stop
					time.sleep(1)
					#avg_tick = (local.counterFL.value + local.counterBR.value) / 2
					#distance = local.tick_2_distance(avg_tick)
					#print("distance traveled inside of get_object(): ", \
					#distance)
					# update position before turning
					#local.x = local.x + distance * math.cos(math.radians(\
					#	local.lr_imu_angle))
					#local.y = local.y + distance * math.cos(math.radians(\
					#	local.lr_imu_angle))
					#print("current location is x: ", local.x, "y: ", local.y)
					#while True:
					#	ans = input("position look right?: ")
					#	if ans == 'y':
					#		break
					#local.reset_tick_count()
					look4color(color, 0, 135) # recenter object
					loco.drive([0, 0, 0, 0]) # stop turning
				elif percep.get_angle2center(cx) <= -4: # if obj to left more than 7 degrees
					print("pin31: ", pin31, "pin37: ", pin37)
					print("obj is to left ", cx, "degrees")
					loco.drive([0, 0, 0, 0]) # stop
					time.sleep(1)
					#avg_tick = (local.counterFL.value + local.counterBR.value) / 2
					#distance = local.tick_2_distance(avg_tick)
					#print("distance traveled inside of get_object(): ", \
					#distance)

					# update position before turning
					#local.x = local.x + distance * math.cos(math.radians(\
					#	local.lr_imu_angle))
					#local.y = local.y + distance * math.cos(math.radians(\
					#	local.lr_imu_angle))
					#print("current location is x: ", local.x, "y: ", local.y)
					#while True:
					#	ans = input("position look right?: ")
					#	if ans == 'y':
					#		break

					#local.reset_tick_count()
					look4color(color, 135, 0) # recenter object
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
				#local.x = current_distance * math.cos(math.radians(local.lr_imu_angle))
				#local.y = current_distance * math.sin(math.radians(local.lr_imu_angle))
				print("curr angle: ", round(local.lr_imu_angle, 4), "curr_dist: ",\
					round(current_distance, 2), "counterFL: ", \
					local.counterFL.value, "counterBR: ", \
					local.counterBR.value, "x:", round(local.x, 3), "y: ", \
					round(local.y, 3))

				current_distance = local.tick_2_distance(local.counterFL.value)
				# if robot leans right
				if local.lr_imu_angle - start_angle <= -local.max_diff: 
					#if velocity >= local.max_vel:
					#	pin31 -= 1
					#	pin37 -= 1
					#	pin31_opt = pin31 # use this optimal val below
					#	pin37_opt = pin37
						# we must assign here because we no longer adjust
					#else:
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
		while True:
			#print("robot thinks it's at x: ", local.x, "y: ", local.y)
			ans = input("is object close enough and aligned?")
			if ans == 'y':
				break
		# obj should be close and center enough by now
		loco.drive([30, 0, 0, 30]) # drive straight
		while True:
			frame = percep.get_pic()
			edged = percep.detect_color(frame, color)
			frame, cx, cy, _, w, h = percep.detect_contours(edged, frame)
			cv.imshow("get_object", frame)
			cv.waitKey(30)
			print("w: ", w, "h: ", h)
			# if w > 100 and h > 145
			#object is close enough so...
			if percep.object_check(w, h) is "grip":
				print("object is within grasp")
			#	while True:
					#ans = input("is object within grasp?: ")
					#if ans == 'y':
				#		break

				while True:
					# record angle before driving straight
					with local.imu_angle_lock:
						local.lr_imu_angle = local.imu_angle
					loco.drive([30, 0, 0, 30]) # drive to grab object
					_, _ = local.get_tick_count() # update tick count
					# 3 inches = .0732m, and 4687 ticks/m
					if local.counterFL.value >= .0762 * 4687:
						break
				loco.grip("close")
				loco.drive([0, 0, 0, 0])
				avg_tick = (local.counterFL.value + local.counterBR.value) / 2
				distance = local.tick_2_distance(avg_tick)
				print("distance traveled inside of get_object(): ", \
				distance)

				# update position before turning
				local.x = local.x + distance * math.cos(math.radians(\
					start_angle))
					#local.lr_imu_angle))
				local.y = local.y + distance * math.sin(math.radians(\
					start_angle))
				print("current location is x: ", local.x, "y: ", local.y)
				print("current heading: ", local.lr_imu_angle)

				return True



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

	# start turning left
	pin33 = loco.duty_turn - 5
	pin37 = loco.duty_turn - 5
	loco.drive([0, pin33, 0, pin37]) # check

	i = 0

	# this works best when not fully charged batteries
	#loco.drive([0, loco.duty_turn + 5, 0, loco.duty_turn + 5]) # check
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
					pin33 -= 6.5
					pin37 -= 6.5
				else:
					pin33 -= 4.5
					pin37 -= 4.5
				loco.drive([0, pin33, 0, pin37])
				#loco.drive([0, pin33, 0, loco.duty_turn - 17])
			elif angle_roc <= local.min_angle_roc:
				pin33 += .75
				pin37 += .75
				print("increasing left turn speed..")
				loco.drive([0, pin33, 0, pin37])
				#loco.drive([0, loco.duty_turn - 5, 0, loco.duty_turn - 5])

		if lt_angle is None: # if we dont want to turn left
			loco.drive([0, 0, 0, 0]) # stop turning left
			break
		elif percep.detect_contours(edged, frame) is not None:
			frame, cx, cy, edged, w, h = percep.detect_contours(edged, frame)
			if abs(percep.get_angle2center(cx)) <= 15:
				# slow down
				loco.drive([0, loco.duty_turn, 0, loco.duty_turn])

			#cv.imshow("look4color: ", frame)
			#cv.waitKey(30)
			# if object is close to center
			with local.imu_angle_lock:
					local.lr_imu_angle = local.imu_angle
			if abs(percep.get_angle2center(cx)) <= 5:
				loco.drive([0, 0, 0, 0]) # stop
				# get obj angle
				print("obj is at: ",local.lr_imu_angle, "degrees")
				cv.imshow("look4color", frame)
				while True:
					ans = input("exiting look4color, want to continue?")
					if ans == 'y':
						break
				return True, frame
				#get_object(color, frame) # consider moving this out?

		# get current angle
		with local.imu_angle_lock:
			local.lr_imu_angle = local.imu_angle
		print("current angle: ", local.lr_imu_angle)
		th2 = local.lr_imu_angle
		t2 = time.time()

		# if the bot has turned left > lt_angle
		if abs(local.prior_imu_angle - local.lr_imu_angle) >= lt_angle:
			print("turned left to:", local.imu_angle, "degrees")
			frame = percep.get_pic()
			#out.write(frame)
			break # break out of loop to start turning right
		i += 1

	i = 0 # reset for use in next while loop
	with local.imu_angle_lock:
		local.prior_imu_angle = local.imu_angle
	#print("initial angle: ", local.prior_imu_angle)


	loco.drive([loco.duty_turn - 5, 0, loco.duty_turn - 5, 0]) # check
	# start turning right, thise config works best when batteries are not fully charged
	pin31 = loco.duty_turn + 10
	pin35 = loco.duty_turn + 10
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
			print("rate of change in angle is: ", angle_roc)
			if angle_roc >= local.high_angle_roc:
				print("decreasing left turn speed..")
				if angle_roc >= local.max_angle_roc:
					pin31 -= 4.5
					pin35 -= 4.5
				else:
					pin31 -= 2.5
					pin35 -= 2.5
				loco.drive([pin31, 0, pin35, 0])
				#loco.drive([0, pin33, 0, loco.duty_turn - 17])
			elif angle_roc <= local.min_angle_roc:
				pin31 += .75
				pin35 += .75
				print("increasing left turn speed..")
				loco.drive([pin31, 0, pin35, 0])

		if rt_angle is None: # if we dont want to turn right
			loco.drive([0, 0, 0, 0]) # stop turning right
			break
		# if we found the object
		elif percep.detect_contours(edged, frame) is not None:
			frame, cx, cy, edged, w, h = percep.detect_contours(edged, frame)
			if abs(percep.get_angle2center(cx)) <= 15:
				# slow down
				loco.drive([loco.duty_turn, 0, loco.duty_turn, 0])
			text = "obj is" + str(percep.get_angle2center(cx)) + "degrees from center"
			frame = percep.write_on_frame(frame, text)
			#cv.imshow("look4color", frame)
			#cv.waitKey(30)
			#print("angle2center: ", percep.get_angle2center(cx))
			# if object is close to center
			if abs(percep.get_angle2center(cx)) <= 2:
				loco.drive([0, 0, 0, 0]) # stop
				print("cx: ", cx, "cy: ", cy)
				print("waiting before get_object")
				# get obj angle
				with local.imu_angle_lock:
					local.lr_imu_angle = local.imu_angle
				print("obj is at: ", local.lr_imu_angle, "degrees")
				cv.imshow("look4color", frame)
				while True:
					ans = input("exiting look4color want to continue?: ")
					if ans == 'y':
						break
				return True, frame
				#get_object(color, frame) # consider moving this out of this function?

		# get current angle
		with local.imu_angle_lock:
			local.lr_imu_angle = local.imu_angle
		print("current angle: ", local.lr_imu_angle)
		th2 = local.lr_imu_angle
		t2 = time.time()


		# else if the bot has turned right > rt_angledegrees
		if abs(local.prior_imu_angle - local.lr_imu_angle) >= rt_angle:
			print("turned right to ", rt_angle, "degrees")
			frame = percep.get_pic()
			#out.write(frame)
			break
		i += 1


def drive2(targ_x, targ_y):
	print("\ncalled drive2!")
	print("starting at: ", local.x, local.y)
	with local.imu_angle_lock:
		local.prior_imu_angle = local.imu_angle
	print("pointed at: ", local.prior_imu_angle)
	target_angle , distance = local.get_angle_dist(targ_x, targ_y)
	print("target angle is: ", target_angle)
	print("abs(target_angle -local.lr_imu_angle: ", \
			abs(target_angle - local.lr_imu_angle))
	while True:
		ans = input("want to continue? enter y or n: ")
		if ans == 'y':
			break

	# turn in this while loop
	while True:
		if abs(target_angle - local.lr_imu_angle - 2) <= 1:
			print("pointed at ", target_angle ,\
				"breaking out of turning loop")
			loco.drive([0, 0, 0, 0])
			time.sleep(1)
			break
		elif target_angle <= 0: # if we want to turn right
			loco.drive([loco.duty_turn + 10, 0, loco.duty_turn + 8, 0])
			with local.imu_angle_lock:
				local.lr_imu_angle = local.imu_angle
			print("lr_imu_angle: ", local.lr_imu_angle, "need to turn right to: ", \
				target_angle)
			if abs(local.imu_angle - target_angle) <= 1: #current angle is more negative
				loco.drive([0, 0, 0, 0]) # stop turning
				break
		elif target_angle > 0: # if we want to turn left
			loco.drive([0, loco.duty_turn + 8, 0, loco.duty_turn + 5])
			with local.imu_angle_lock:
				local.lr_imu_angle = local.imu_angle
			print("lr_imu_angle: ", local.lr_imu_angle, "need to turn left to: ", \
				target_angle)
			if abs(local.imu_angle - target_angle - 4) <= 1: # check this
				loco.drive([0, 0, 0, 0]) # stop turning
				break

	i = 0
	print("\nresetting FL, BR tick count to: ", local.reset_tick_count())
	time.sleep(3)
	with local.imu_angle_lock:
		start_angle = local.imu_angle
	print("before driving straight, record the reference angle: ", start_angle)
	current_distance = 0
	print("current_distance: ", current_distance)

	while True:
		ans = input("want to continue? enter y or n: ")
		if ans == 'y':
			break
	loco.drive([loco.duty, 0, 0, loco.duty]) # drive straight

	# drive forward in this while loop
	while True:
		with local.imu_angle_lock:
			local.lr_imu_angle = local.imu_angle
		# update position as we go?
		#local.x = current_distance * math.cos(math.radians(local.lr_imu_angle))
		#local.y = current_distance * math.sin(math.radians(local.lr_imu_angle))
		print("curr angle: ", round(local.lr_imu_angle, 4), "curr_dist: ",\
		round(current_distance, 2), " target_dist: ", round(distance, 2), \
		"counterFL: ", local.counterFL.value, "counterBR: ", \
		local.counterBR.value, "x:", round(local.x, 3), "y: ", round(local.y, 3))
		#print("distance from wall: ", round(percep.measure_distance(), 2))
		if local.lr_imu_angle - start_angle <= -local.max_diff: # if robot leans right
			print("leaning right")
			pin31 = loco.duty - local.left_adjust
			pin37 = loco.duty + local.right_adjust
			loco.drive([pin31, 0, 0, pin37]) # speed up right wheels
		elif local.lr_imu_angle - start_angle >= local.max_diff: # if robot leans left
			print("leaning left")
			pin31 = loco.duty  + local.left_adjust
			pin37 = loco.duty - local.right_adjust
			loco.drive([pin31, 0, 0, pin37]) # speed up left wheels
		if i % 2 == 0: # update current distance every other iteration
			tick_avg = (local.counterFL.value + local.counterBR.value) / 2
			current_distance = local.tick_2_distance(tick_avg)
		# once we start to get within 2 feet of the x walls, and we're pointed at it
		# we should measure distance to relocalize the x coordinate
		if local.right_x_wall - local.x <= 2 and -.5 <= local.lr_imu_angle <= .5: # once we get within 2 feet of the right wall
			dist = percep.measure_distance()
			print("wall is at a distance of: ", init_dist, "cm")
			local.x = local.right_x_wall - dist
		if current_distance + .28 >= distance:
			loco.drive([0, 0, 0, 0])
			break
		i += 1
	print("local.lr_imu_angle: ", local.lr_imu_angle)
	local.x = local.x + distance * math.cos(math.radians(local.lr_imu_angle))
	local.y = local.y + distance * math.sin(math.radians(local.lr_imu_angle))
	print("distance traveled was: ", distance)
	print("x: ", local.x, "y: ", local.y)


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

	### loop1: look for QR code ###
#	while True:
#		print("looking for qr code..")
#		data = percep.detect_qr_code()
#		if data == "ENPM701":
#			print("starting grand challenge!")
#			break


	order = ['green', 'blue', 'red', 'green', 'blue', 'red', 'green', 'blue'] # update

	for color in order:
		### loop2: look4color ###

		print("\nlooking for", color, "blocks")
		while True:
			print("x: ", local.x, "y: ", local.y)
			obj_found, frame = look4color(color, 90, 0)
			if obj_found is True:
				print("found obj, robot is pointing: ", local.imu_angle)
				break
		### loop3: get_object and deliver
		while True:
			grabbed_obj=get_object(color, frame)
			if grabbed_obj is True:
				break

		drive2(2, 8)


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


if __name__ == "__main__":
	start = time.time()
	#main()
	#main2()
	main3()
	end = time.time()
	print("time taken: ", abs(end - start), "seconds")
