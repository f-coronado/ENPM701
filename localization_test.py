from libraries.localization import Localization
from libraries.locomotion import Locomotion
import time

def main():

	loco = Locomotion()
	print("intialized locomotion")
	time.sleep(5)
	local = Localization()
	print("initialized localization")


	loco.drive([loco.duty, 0, 0, loco.duty])
	print("started driving")
	time.sleep(5)

	while True:

		#with local.tick_lock:
		#	counterFL, counterBR = local.get_tick_count()
		print("counterFL: ", local.counterFL, "counterBR: ", local.counterBR)
#		print("counterFL: ", local.counterFL, "counterBR: ", local.counterBR)
		distance = round(local.tick_2_distance(local.counterFL), 2)
		print("distance: ", distance)

		if distance >= 1:
			print("traveled 1 meter")
			loco.drive([0, 0, 0, 0])
			break



if __name__ == "__main__":
	main()
