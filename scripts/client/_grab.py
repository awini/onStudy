#coding: utf-8
import sys, time

import numpy as np
import cv2
from PIL import ImageGrab

width = 1280
height = 720

try:
    fourcc = cv2.VideoWriter_fourcc('X','V','I','D') #you can use other codecs as well.
except:
    fourcc = cv2.cv.CV_FOURCC(*'XVID')

####vid = cv2.VideoWriter('record.avi', fourcc, 20, (width, height))

# Find OpenCV version
(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

cap = cv2.VideoCapture(0)



if int(major_ver)  < 3 :
    fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
    print("Frames per second using video.get(cv2.cv.CV_CAP_PROP_FPS): {0}".format(fps))
else :
    fps = cap.get(cv2.CAP_PROP_FPS)
    print("Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps))


# Number of frames to capture
num_frames = 120


print("Capturing {0} frames".format(num_frames))

# Start time
start = time.time()


frame_i = 0


while(True):
    if frame_i == num_frames and 'check' in sys.argv:
        break

    img = ImageGrab.grab() #x, y, w, h
    # img = ImageGrab.grab(bbox=(100, 10, 600, 500)) #x, y, w, h
    # res = cv2.resize(img, None, fx=img.height/height,fy=img.width/width, interpolation=cv2.INTER_CUBIC)
    # print((int)(img.height/height), (int)(img.width/width))
    res = cv2.resize(np.array(img), (width, height), interpolation=cv2.INTER_CUBIC)
    img_np = np.array(res)

    # prepare capture frame
    ret, frame = cap.read()

    frame = cv2.resize(frame, (320, 240), interpolation=cv2.INTER_CUBIC)

    rows, cols, channels = frame.shape
    roi = img_np[0:rows, 0:cols]
    # cv2.addWeighted(img_np, 0.5, frame, 0.5, 0)

    #print(rows, cols)

    # merge two image
    img_np[0:rows, 0:cols] = frame

    # save on disk
    #frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

    ####vid.write(img_np)

    if 'check' not in sys.argv:
        sys.stdout.write(img_np.tostring())

    ####cv2.imshow("frame", img_np)
    key = cv2.waitKey(41)
    if key == 27:
        break

    frame_i += 1

# End time
end = time.time()

# Time elapsed
seconds = end - start
print("Time taken : {0} seconds".format(seconds))

# Calculate frames per second
fps = num_frames / seconds;
print("Estimated frames per second : {0}".format(fps))


####vid.release()
cv2.destroyAllWindows()
