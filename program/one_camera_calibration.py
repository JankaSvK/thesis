import numpy as np
import cv2
import glob

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Chessboard size
size = (7,9)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((size[0] * size[1],3), np.float32)
objp[:,:2] = np.mgrid[0:size[0],0:size[1]].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [[], []]  # 3d point in real world space
imgpoints = [[], []]  # 2d points in image plane.

images = [
    glob.glob('images/single_camera_calibration/left/*.jpg'),
    glob.glob('images/single_camera_calibration/right/*.jpg'),
]

for camera_index, camera_images in enumerate(images):
    for fname in camera_images:
        img = cv2.imread(fname)
        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, size, None)

        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints[camera_index].append(objp)
            #print(objp)
            corners2=cv2.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
            imgpoints[camera_index].append(corners2)

            # Draw and display the corners
            cv2.drawChessboardCorners(img, size, corners2, ret)
            cv2.imshow('img', img)
            cv2.waitKey(500)

#ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
#newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

# Undistord image
img = cv2.imread('images/single_camera_calibration/WIN_20171208_23_27_21_Pro.jpg')
dst = cv2.undistort(img, mtx, dist, None, newcameramtx)

# Crop the image
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv2.imwrite('images/single_camera_calibration/calibresult.png', dst)

# Compute an error
mean_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2)/len(imgpoints2)
    mean_error += error
print( "total error: {}".format(mean_error/len(objpoints)) )

cv2.destroyAllWindows()