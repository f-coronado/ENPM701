import serial
import RPi.GPIO

def init():

        gpio.setmode(gpio.BOARD)
        gpio.setup(31, gpio.OUT) # IN1
        gpio.setup(33, gpio.OUT) # IN2
        gpio.setup(35, gpio.OUT) # IN3
        gpio.setup(37, gpio.OUT) # IN4


def pivotright(tf):
#        init()

        # left wheels
        gpio.output(31, False)
        gpio.output(33, True)

        # right wheels
        gpio.output(35, False)
        gpio.output(37, True)

        # wait
        time.sleep(tf)
        # send all pins low and cleanup
        gameover()
#        gpio.cleanup()

def pivotleft(tf):
#        init()

        # left wheels
        gpio.output(31, True)
        gpio.output(33, False)

        # right wheels
        gpio.output(35, True)
        gpio.output(37, False)

        # wait
        time.sleep(tf)
        # send all pins low and cleanup
        gameover()
#        gpio.cleanup()


def forward(tf):
#        init()

        # left wheels
        gpio.output(31, True)
        gpio.output(33, False)

        # right wheels
        gpio.output(35, False)
        gpio.output(37, True)

        # wait
        time.sleep(tf)
        # send all pins low and cleanup
        gameover()
#        gpio.cleanup()

def reverse(tf):
#        init()

        # left wheels
        gpio.output(31, False)
        gpio.output(33, True)

        # right wheels
        gpio.output(35, True)
        gpio.output(37, False)

        # wait
        time.sleep(tf)
        # send all pins low and cleanup
        gameover()
#        gpio.cleanup()



def main():

	ser = serial.Serial('/dev/ttyUSB0', 9600) # identify serial connection
	cnt = 0

	while True:

		if (ser.in_waiting > 0):
			cnt += 1
			line = ser.readline()
			print(line)

			if cnt > 10: # avoid first 10 lines of serial connection

				# strip serial stream of extra characters
				line = line.rstrip().lstrip()
				print(line)

				line = str(line)
				line = line.strip("'")
				line = line.strip("b'")
				print(line)

				line = float(line)
				print(line, "\n")

	sequence = input("Enter a sequence of commands separated by spaces. Available commands are: f, b, r, l").split()
	

if __name__ == "__main__":
	main()
