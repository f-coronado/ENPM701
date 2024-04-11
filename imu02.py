import serial
import RPi.GPIO
from libraries.localization import Localization
from libraries.locomotion import Locomotion

def init():

        gpio.setmode(gpio.BOARD)
        gpio.setup(31, gpio.OUT) # IN1
        gpio.setup(33, gpio.OUT) # IN2
        gpio.setup(35, gpio.OUT) # IN3
        gpio.setup(37, gpio.OUT) # IN4

def main():

	locomotion = Locomotion()
	localization = Localization()

	ser = serial.Serial('/dev/ttyUSB0', 9600) # identify serial connection
	cnt = 0

	sequence = input("Enter a sequence of commands separated by spaces. \nAvailable commands are: f, b, r, l:\n").split()
	print("the sequence of commands entered was: \n", sequence)

	max_count = 2343 # ticks needed for half a meter
	duty = 20
	duty_turn = 80

	for command in sequence:
		print("command: ", command)
		cntrBR = 0
		cntrFL = 0
		localization.reset_tick_count()
		while cntrBR <= max_count and cntrFL <= max_count:

			if command == 'f':
				locomotion.drive([duty, 0, 0, duty])
				print("driving forward")

			if command == 'b':
				locomotion.drive([0, duty, duty, 0])
				print("driving in reverse")

			if command =='l':
				locomotion.drive([0, duty_turn, 0, duty_turn])
				print("pivoting left")

			if command == 'r':
				locomotion.drive([duty_turn, 0, duty_turn, 0])
				print("pivoting right")

			cntrBR, cntrFL = localization.get_tick_count()
			print("cntrBR, cntrFL: ", cntrBR, cntrFL)
			if cntrBR and cntrFL >= max_count:
				locomotion.gameover()
				break

if __name__ == "__main__":
	main()
