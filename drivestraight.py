from libraries.localization import Localization
from libraries.locomotion import Locomotion
import time
import matplotlib.pyplot as plt

def control():

	loco = Locomotion()
	local = Localization()
	duty = 70
	start = time.time()
	loco.drive([duty, 0, 0, duty])

	sample_time = 0.5 # in .5s at 70% pwm, cntrFL = 265 cntrBR = 345
	tickspersample = 265
	target = 0.75 * tickspersample # should be 75% of encoder ticks per sample
	kp = 1 /tickspersample
	FL_speed = duty
	BR_speed = duty

	start = time.time() # start sample time
	max_change = 15
	#time.sleep(2)

	while True:
#		print("initial counters")
		#print("counterFL: ", local.counterFL, "counterBR: ", local.counterBR)
		local.counterFL, local.counterBR = local.get_tick_count()
		FL_error = target - local.counterFL
		BR_error = target - local.counterBR
		FL_speed += FL_error * kp
		BR_speed += BR_error * kp
		print("FL_error: ", FL_error, "BR_error: ", BR_error)
		print("FL_speed: ", FL_speed, "BR_speed: ", BR_speed)

		#end = time.time()
#		if end - start >= sample_time: # if sample time has been reached, apply correction
#		print("\n	unadjusted speed: ")
#		print("		FL_speed : ", FL_speed, "BR_speed: ", BR_speed)
		#print("		counterFL: ", local.counterFL, "counterBR: ", local.counterBR)
		FL_speed = max(min(100, FL_speed), -max_change)
		BR_speed = max(min(100, BR_speed), -max_change)
		loco.drive([FL_speed, 0, 0, BR_speed])
		print("		counterFL: ", local.counterFL, "counterBR: ", local.counterBR)
		print("		FL_speed : ", FL_speed, "BR_speed: ", BR_speed)
		print("		FL_error: ", FL_error, "BR_error: ", BR_error)
		start = time.time() # reset the start
		#local.reset_tick_count()
		#FL_error = 0
		#BR_error = 0
		time.sleep(sample_time)

def control2():
	loco = Locomotion()
	local = Localization()

	left_adjustment = 8
	right_adjustment = 18

	time.sleep(4)

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
	max_diff = .25
	time.sleep(5)
	loco.drive([loco.duty, 0, 0, loco.duty])
	pin31 = loco.duty
	pin37 = loco.duty
	distance = 0

	while True:

		#local.counterFL, local.counterBR = local.get_tick_count()

		with local.imu_angle_lock:
			local.lr_imu_angle = local.imu_angle
		print("start_angle: ", start_angle, "current angle: ", round(local.lr_imu_angle, 3), "pin speeds: 31=", pin31, "37=",pin37,\
		"distance: ", round(distance, 2), "counterFL: ", local.counterFL.value, "counterBR: ", \
		local.counterBR.value)

		if local.lr_imu_angle - start_angle >= max_diff: # this mean heading is toward the right
			#print("angle diff: ", local.lr_imu_angle - start_angle)
			print("leaning right")
			pin31 = loco.duty - left_adjustment
			pin37 = loco.duty + right_adjustment

			#pin37 = loco.duty

			#pin31 -= adjustment
			#pin37 += adjustment
			#pin31 = max(30, min(pin31, 90))
			#pin37 = max(30, min(pin37, 90))
			loco.drive([pin31, 0, 0, pin37]) # speed up right wheels
		elif local.lr_imu_angle - start_angle <= -max_diff: # if robot is leaning towards left...
			print("leaning left")
			pin31 = loco.duty  + left_adjustment
			pin37 = loco.duty - right_adjustment
			#pin31 += adjustment
			#pin37 -= adjustment
			#pin31 = max(30, min(pin31, 90))
			#pin37 = max(30, min(pin37, 90))
			loco.drive([pin31, 0, 0, pin37]) # speed up right wheels
		distance = local.tick_2_distance(local.counterFL) # check how far we have traveled
		if distance >= 2: # if traveled 2m break
			print("traveled: ", distance, "meters")
			break

	loco.drive([0, 0, 0, 0]) # stop
	y = []
	for tick in local.FL_encoder_cnt:
		y_dist = local.tick_2_distance(tick)
		y.append(y_dist)
	x = 
	plt.plot(


def main():
	#control()
	control2()

if __name__ == "__main__":

	main()
