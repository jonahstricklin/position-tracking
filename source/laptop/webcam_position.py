# This script use the webcam to find location relative to QR code anchor

import cv2, time, numpy, csv

# Output collected from webcam_camera_calibration.py
with numpy.load("webcam_calib_data.npz") as data:
    mtx = data["mtx"]
    dist = data["dist"]
    newcameramtx = data["newcameramtx"]
    roi = data["roi"]

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
        
        rvec, jacobian = cv2.Rodrigues(rvec)
        camera_position = -rvec.transpose() @ tvec

        camera_position = [camera_position[0][0], camera_position[1][0], camera_position[2][0]]
    return img, camera_position

log = []
cam = cv2.VideoCapture(0)
while True:
    ret, frame = cam.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    img, qr_camera_position = show_axes(mtx, dist, gray)
    cv2.imshow("frame", img)
    
    if qr_camera_position: recorded_camera_position = qr_camera_position
    else: recorded_camera_position = [0, 0, 0]
    log.append(recorded_camera_position)
    print(recorded_camera_position)

    k = cv2.waitKey(20)
    if k == 27: break # 27 is ESC key

with open("position_log_webcam.csv", "w") as file:
    writer = csv.writer(file)
    writer.writerows(log)
