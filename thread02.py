from libraries.localization import Localization
import time

def main():
	local = Localization()

	global imu_angle

	print("starting..")
	time.sleep(2)

	# get current angle from imu
	start = time.time()
	local.get_imu_angle()
	end = time.time()
	print("took:", end-start, "seconds to get angle")
	print("starting angle is: ", current_angle)
	print("waiting 5s..")

	time.sleep(5)

	start = time.time()
	local.get_imu_angle()
	end = time.time()
	print("took:", end-start, "seconds to get angle")
	print("updated angle is: ", current_angle)
	print("waiting 5s..")
	time.sleep(5)

	start = time.time()
	local.get_imu_angle()
	end = time.time()
	print("took:", end-start, "seconds to get angle")
	print("updated angle is: ", current_angle)
	print("waiting 5s..")
	time.sleep(5)

	start = time.time()
	local.get_imu_angle()
	print("updated angle is: ", current_angle)
	print("waiting 5s..")
	end = time.time()
	print("took:", end-start, "seconds to get angle")




if __name__ == "__main__":
	main()
