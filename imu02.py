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

	localization = Localization()
	locomotion = Locomotion()

	ser = serial.Serial('/dev/ttyUSB0', 9600) # identify serial connection
	cnt = 0

	sequence = input("Enter a sequence of commands separated by spaces. \nAvailable commands are: f, b, r, l:\n").split()
	print("the sequence of commands entered was: \n", sequence)

	max_count = 2343 # ticks needed for half a meter
	duty = 20

	for command in sequence:
		if command == 'f':
			locomotion.drive([duty, 0, 0, duty])

		if command == 'b':
			locomotion.drive([0, duty, duty, 0])

		if command == 'r':
			locomotion.drive([0, duty, 0, duty])

		if command == 'l':
			locomotion.drive([duty, 0, duty, 0])

		cntrBR, cntrFL = localization.get_tick_count()
		if cntrBR and cntrFL >= max_count:
			locomoution.gameover()

if __name__ == "__main__":
	main()
