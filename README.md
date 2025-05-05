# position-tracking
Project for Computer Vision CS362V

# Main idea
Using the camera and a QR code anchor, we can estimate and record the camera's relative position in 3d space. The lens must be calibrated (rpi_camera_calibration.py), the position can be recorded (rpi_position.py), and then that telemety can be viewed in MATLAB (3d_viewer.m).

After writing this entirely for the Pi, I decided to also show how it runs on my laptop with a USB webcam.

# Abandoned Accelerometer feature
I wanted to used the accelerometer to fill in the gaps between photos taken. This strategy is used on small, low power satalites: https://www.jpl.nasa.gov/nmp/st6/TECHNOLOGY/compass_tech.html
Using relative acceleration to calculate position is extremely dependent on knowing your sample rate and previous position. Unfortunately, the Raspberry Pi 3 was running too slow, and the MPU6050 exhibiting too much noise for this to be a viable option.

For classroom demo purposes, I have not deleted the code I wrote for the MPU6050 feature. 

# References
These are the main guides I used for each major portion of the project
Camera Calibration: https://docs.opencv.org/3.4/dc/dbb/tutorial_py_calibration.html
QR code tracking: https://temugeb.github.io/python/computer_vision/2021/06/15/QR-Code_Orientation.html
MPU6050: https://www.instructables.com/How-to-Use-the-MPU6050-With-the-Raspberry-Pi-4/
