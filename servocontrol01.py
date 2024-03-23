import RPi.GPIO as gpio

def key_input(event):
        init()
        print("key: ", event)
        key_press = event
        tf = 1

        if key_press.lower() == 'f':
                forward(tf)
        elif key_press.lower() == 'b':
                reverse(tf)
        elif key_press.lower() == 'l':
                pivotleft(tf)
        elif key_press.lower() == 'r':
                pivotright(tf)
        else:
                print("invalid key pressed")

