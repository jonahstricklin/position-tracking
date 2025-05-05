# This script use the Raspberry Pi camera find location relative to QR code anchor

from picamera2 import Picamera2
import cv2, time, numpy, csv, mpu6050
sensor = mpu6050.mpu6050(0x68)

# Initialize Camera
picam = Picamera2()
picam.create_preview_configuration({"format": "BGR888"})
picam.start(show_preview=False)
time.sleep(2)

# Output collected from rpi_camera_calibration.py
with numpy.load("picam_calib_data.npz") as data:
    mtx = data["mtx"]
    dist = data["dist"]
    newcameramtx = data["newcameramtx"]
    roi = data["roi"]

# Interfacing with the MPU6050 accelerometer (NO LONGER USED)
def get_acceleration(offset, unit_length=1):
    raw = sensor.get_accel_data()
    x = (raw['x'] - offset['x']) * 9.8 * unit_length
    y = (raw['y'] - offset['y']) * 9.8 * unit_length
    z = (raw['z'] - offset['z']) * 9.8 * unit_length

    # Adjust axes to match the way the accelerometer is mounted to the Pi
    x_adjusted = y
    y_adjusted = -x
    z_adjusted = z
    return [x_adjusted , y_adjusted , z_adjusted ]
def update_position(pos, vel, acc, dt):
    new_vel = [vel[i] + acc[i] * dt for i in range(3)]
    new_pos = [pos[i] + vel[i] * dt + 0.5 * acc[i] * dt ** 2 for i in range(3)]
    return new_pos, new_vel

def get_qr_coords(cmtx, dist, points):
    # Selected coordinate points for each corner of QR code.
    qr_edges = numpy.array([[0,0,0],
                         [0,1,0],
                         [1,1,0],
                         [1,0,0]], dtype = 'float32').reshape((4,1,3))

    # determine the orientation of QR code coordinate system with respect to camera coorindate system.
    ret, rvec, tvec = cv2.solvePnP(qr_edges, points, cmtx, dist)

    # Define unit xyz axes. These are then projected to camera view using the rotation matrix and translation vector.
    unitv_points = numpy.array([[0,0,0], [1,0,0], [0,1,0], [0,0,1]], dtype = 'float32').reshape((4,1,3))
    if ret:
        points, jac = cv2.projectPoints(unitv_points, rvec, tvec, cmtx, dist)
        return points, rvec, tvec

    # return empty arrays if rotation and translation values not found
    else: return [], [], []

# Very similar to Temuge Batpurev's tutorial with som modification
def show_axes(cmtx, dist, img):
    qr = cv2.QRCodeDetector()

    ret_qr, points = qr.detect(img)

    camera_position = False
    if ret_qr:
        axis_points, rvec, tvec = get_qr_coords(cmtx, dist, points)

        # BGR color format
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0,0,0)]

        # check axes points are projected to camera view.
        if len(axis_points) > 0:
            axis_points = axis_points.reshape((4,2))

            origin = (int(axis_points[0][0]),int(axis_points[0][1]) )

            for p, c in zip(axis_points[1:], colors[:3]):
                p = (int(p[0]), int(p[1]))

                # Sometimes qr detector will make a mistake and projected point will overflow integer value. We skip these cases. 
                if origin[0] > 5*img.shape[1] or origin[1] > 5*img.shape[1]:break
                if p[0] > 5*img.shape[1] or p[1] > 5*img.shape[1]:break

                cv2.line(img, origin, p, c, 5)
        
        # Gives te camera's positio with respect to the QR code, rather than vice versa
        rvec, jacobian = cv2.Rodrigues(rvec)
        camera_position = -rvec.transpose() @ tvec

        camera_position = [camera_position[0][0], camera_position[1][0], camera_position[2][0]]
    return img, camera_position

# Initial values for position log
log = [["x", "y", "z", "Instrument"],
       [0  ,  0 ,  0 , "initial"]]

# Variables for using the MPU6050 (NO LONGER USED)
# Output collected from mpu6050_calibration.py
accel_offset = {'x': -1.2631961061185335, 'y': 0.0016973226763842004, 'z': 9.830343885448244}
gyro_offset = {'x': 1.4331198397535698, 'y': 1.6313658819865837, 'z': -0.14931365040356182}

dt = 0.65 # Contant Δt for the loop (must be longer than the necessary processing time)
unit_length = 0.05 # This means that the width of the QR code is 0.05 meters
position = [0,0,0]
velocity = [0,0,0]

while True:
    # Capture image & convert to grayscale so it's easier to work with
    capture_time = time.time()
    bgr = picam.capture_array()
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    # Look for a QR code
    img, qr_camera_position = show_axes(mtx, dist, gray)
    
    # If QR code is detected, add value to the log
    if qr_camera_position:
        recorded_camera_position = qr_camera_position
        instrument = "camera"
    
    # If QR code is NOT detected use accelerometer (NO LONGER USED)
    else:
        #prev_position = log[-1]
        #acceleration = get_acceleration(accel_offset, unit_length)
        #recorded_camera_position, velocity = update_position(prev_position, velocity, acceleration, dt)
        #instrument = "accelerometer"

        # When a QR code can not be found, just repeat the last position
        recorded_camera_position = log[-1]
        instrument = "repeated"
    log.append(recorded_camera_position)
    print(recorded_camera_position)
    
    cv2.imshow("frame", img)
    
    # Control the speed of the loop to make sure that every loop has the same Δt (NO LONGER USED)
    # elapsed = time.time() - capture_time
    # interval = dt - elapsed
    # if interval < 0: print("Warning: Process is taking too long. dt will be off")
    # else: time.sleep(interval)
    
    k = cv2.waitKey(20)
    if k == 27: break # 27 is ESC key
    
# Record log to csv output so it can be read into MATLAB
with open("position_log_rpi.csv", "w") as file:
    writer = csv.writer(file)
    writer.writerows(log)

