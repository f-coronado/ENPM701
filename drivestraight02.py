from libraries.localization import Localization
from libraries.locomotion import Locomotion
import time

def control():

	loco = Locomotion()
	local = Localization()
	duty = 70
	#start = time.time()
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

		end = time.time()
		if end - start >= sample_time: # if sample time has been reached, apply correction
			print("\n	unadjusted speed: ")
			print("		FL_speed : ", FL_speed, "BR_speed: ", BR_speed)
			print("		counterFL: ", local.counterFL, "counterBR: ", local.counterBR)
			FL_speed = max(min(100, FL_speed), -max_change)
			BR_speed = max(min(100, BR_speed), -max_change)
			loco.drive([FL_speed, 0, 0, BR_speed])
			print("		counterFL: ", local.counterFL, "counterBR: ", local.counterBR)
			print("		FL_speed : ", FL_speed, "BR_speed: ", BR_speed)
			print("		FL_error: ", FL_error, "BR_error: ", BR_error)
			start = time.time() # reset the start
			local.reset_tick_count()
			#FL_error = 0
			#BR_error = 0
			time.sleep(sample_time)


def main():
	control()

if __name__ == "__main__":

	main()
