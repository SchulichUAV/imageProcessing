﻿import numpy as np
import cv2
import glob

print("i loaded the libraries")
# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((7 * 7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:7].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.
imgcorners = [] #2d corners of the chessboard
images = glob.glob('*.jpg')

enumi = enumerate(images)



for enum_fname in enumi:

    iteration = next(enumi)
    index,fname = iteration
    print ("Iteration", index)
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    grid = (7,7)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, grid,None)
    print ("Corners: ", len(corners))

    # If found, add object points, image points (after refining them)
    if ret == True:
        print ("Found Chessboard")
        objpoints.append(objp)
        cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(corners)
        print ("objpoints: ", objpoints, "imgpoints: ", imgpoints)

        # Draw and display the corners
        cv2.drawChessboardCorners(img, grid, corners,ret)
        smol = cv2.resize(img, (0,0), fx = 0.4, fy = 0.4)
        cv2.imshow('thesight',smol)
    
    print ("Calibrate? Y / N")

    if cv2.waitKey(0) == ord('y'):
        print ("Calibrating.")
        test = gray.shape[::-1]
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
       
        h, w = gray.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
        x,y,h,w = roi

        if 0: #error of the project, err -> 0 is better
            imgpoints2 = []
            jacob = []
            print (objpoints)
            imgpoints2, jacob = cv2.projectPoints(objpoints[0],rvecs[0],tvecs[0],mtx,dist)
            err = cv2.norm(imgpoints[0],imgpoints2, cv2.NORM_L2)
            print (err)

        if 1: #two methods of undistortion which should give the same result
            dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
        else:
            mapx,mapy = cv2.initUndistortRectifyMap(mtx,dist,None,newcameramtx,(w,h),5)
            dst = cv2.remap(img,mapx,mapy,cv2.INTER_LINEAR)
        
        #display the undistorted image
        dstsmol = cv2.resize(dst, (0,0), fx = 0.4, fy = 0.4)
        cv2.imshow("undistort",dstsmol)

        print ("Crop? ROI is: ", roi)
        if cv2.waitKey(0) == ord('y'):
            dst = dst[y:y+h, x:x+w]
            cv2.imshow("cropped",dst)
            print ("Save Photo? Y /N")
            if cv2.waitKey(0) == ord('y'):    
                cv2.imwrite('calibresult.png',dst)

        #find the corners and perspective translate
        print (imgpoints[0][0][0])
        imgcorners = np.float32([imgpoints[0][0][0],imgpoints[0][6][0],imgpoints[0][42][0],imgpoints[0][48][0]])
        #imgcorners.append(list(imgpoints[0][0][0]))
        #imgcorners.append(list(imgpoints[0][6][0]))
        #imgcorners.append(list(imgpoints[0][42][0]))
        #imgcorners.append(list(imgpoints[0][48][0]))


        persp = np.float32([[0,0],[300,0],[0,300],[300,300]])

        M = cv2.getPerspectiveTransform(imgcorners,persp)
        dest = cv2.warpPerspective(img,M,(300,300))

        cv2.imshow("warp",dest)


        cv2.waitKey(0)
        cv2.destroyAllWindows()
cv2.destroyAllWindows()