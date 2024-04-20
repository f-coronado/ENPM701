import serial
from libraries.localization import Localization

def main():

	ser = serial.Serial('/dev/ttyUSB0', 9600) # identify serial connection
	cnt = 0
	localization = Localization()
	localization.get_imu_angle(ser, cnt)

if __name__ == "__main__":
	main()
