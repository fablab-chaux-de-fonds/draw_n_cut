import numpy as np
import cv2
import os

cap = cv2.VideoCapture(1)


# define range of colors in HSV
lower_color = np.array([0,64,32])
upper_color = np.array([255,255,255])

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get only desired range
    mask_color = cv2.inRange(hsv, lower_color, upper_color)

    # Bitwise-AND mask and original image
    # res_color = cv2.bitwise_and(frame, frame, mask = mask_color)

    h, s, v = cv2.split(hsv)

    nv = v.copy()
    
    # Noramlize image to ensure dark pixels representatiosn
    cv2.normalize(v, nv, 0, 64, cv2.NORM_MINMAX)

    # Clean colored areas
    nv = cv2.add(v, mask_color)

    r, nv = cv2.threshold(nv, 30, 255, cv2.THRESH_BINARY_INV)

    # Display the resulting frame
    cv2.imshow('Orig', frame)
    cv2.imshow('Colors', mask_color)
    cv2.imshow('Black', nv)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

    if key == ord('c'):
        r, mask_color = cv2.threshold(mask_color, 30, 255, cv2.THRESH_BINARY_INV)
        r, nv = cv2.threshold(nv, 30, 255, cv2.THRESH_BINARY_INV)
        
        mask_color = cv2.cvtColor(mask_color, cv2.COLOR_GRAY2BGR)
        nv = cv2.cvtColor(nv, cv2.COLOR_GRAY2BGR)

        cv2.imwrite("./img/cvcolor.ppm", mask_color)
        cv2.imwrite("./img/cvblack.ppm", nv)
        
        cv2.imwrite("./vector/cv/orig.png", frame)
        os.system("potrace -t 10 -W 8in -H 6in -u 10 -s ./img/cvcolor.ppm -o ./vector/cv/color.svg")
        os.system("potrace -t 10 -W 8in -H 6in -u 10 -s ./img/cvblack.ppm -o ./vector/cv/black_potrace.svg")
        os.system("autotrace ./img/cvblack.ppm -output-format svg -centerline -output-file ./vector/cv/black_autotrace.svg")


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()