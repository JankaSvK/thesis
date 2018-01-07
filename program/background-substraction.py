
# Aktualizuje pozadie, nie je potrebna prvotna fotka

import cv2
cap = cv2.VideoCapture(0)
fgbg = cv2.createBackgroundSubtractorKNN()
while(1):
    ret, frame = cap.read()
    fgmask = fgbg.apply(frame)
    cv2.imshow('mask',fgmask)

    thresh = cv2.dilate(fgmask, None, iterations=2)
    im2, cnts, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)



    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < 1000:
            continue

        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow('frame', frame)


    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
cap.release()
cv2.destroyAllWindows()