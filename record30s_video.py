import cv2

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'H264')
output_file = 'output_video.mp4'
frame_rate = 10.0
resolution = (640, 480)
video_writer = cv2.VideoWriter(output_file, fourcc, frame_rate, resolution)

# Open the default camera
video_capture = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not video_capture.isOpened():
    print("Error: Unable to open camera.")
    exit()

# Record video for 30 seconds
start_time = cv2.getTickCount()
while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    if not ret:
        print("Error: Unable to capture frame.")
        break

    # Write the frame to the video file
    video_writer.write(frame)

    # Display the frame
    cv2.imshow('Recording...', frame)

    # Break the loop if the recording time exceeds 30 seconds
    if cv2.getTickCount() - start_time > 30 * cv2.getTickFrequency():
        break

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video writer and camera, and close all OpenCV windows
video_writer.release()
video_capture.release()
cv2.destroyAllWindows()

