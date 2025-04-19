from libraries.locomotion import Locomotion
import time

def main():
	loco = Locomotion()
	#cap = cv.VideoWriter_fourcc(*'mp4v')
	#out = cv.VideoWriter('locomotion_test.mp4', loco.codec, 1, (640, 480))

	loco.look4color("green")

if __name__ == "__main__":
	main()
