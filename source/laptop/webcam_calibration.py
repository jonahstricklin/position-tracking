# Code used to obtain calib_data.npz for USB webcam
# https://docs.opencv.org/3.4/dc/dbb/tutorial_py_calibration.html

import numpy as np
import cv2 as cv
import glob, time

# termination crite
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((5*7,3), np.float32)
objp[:,:2] = np.mgrid[0:5,0:7].T.reshape(-1,2)
# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.
images = glob.glob('*.jpg')

cam = cv.VideoCapture(0)

# Get the default frame width and height
frame_width = int(cam.get(cv.CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(cv.CAP_PROP_FRAME_HEIGHT))

while True:

    ret, frame = cam.read()
    
    #frame = cv.imread("calib_radial.jpg")
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    
    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (5,7), None)
    # If found, add object points, image points (after refining them)
    if ret == True:
        print("object detected")
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners2)
        # Draw and display the corners
        #img = frame
        #img_gray = gray
        cv.drawChessboardCorners(gray, (5,7), corners2, ret)
    
    cv.imshow('Camera', gray)
    
    time.sleep(0.5)

    k = cv.waitKey(20)
    if k == 27: break # 27 is ESC keyk

# Release the capture and writer objects
cv.destroyAllWindows()

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
h,  w = gray.shape[:2]
newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
cv.imwrite('distorted.png', gray)

# undistort
dst = cv.undistort(gray, mtx, dist, None, newcameramtx)
# crop the image
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv.imwrite('calibresult.png', dst)

np.savez("webcam_calib_data.npz", mtx=mtx, dist=dist, newcameramtx=newcameramtx, roi=roi)

 
  