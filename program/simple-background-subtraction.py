import cv2

cap = cv2.VideoCapture(0)

ret, original = cap.read()

while(1):
    ret, frame2 = cap.read()
    frame = frame2.copy()
    #ziskaj masku

    diff = cv2.absdiff(original,frame)
    diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    _, diff = cv2.threshold(diff, 30,255,0)

    cv2.imshow('diff', diff)

    im2, cnts, hierarchy = cv2.findContours(diff,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    largest_area = 0
    set = 0
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < 1000:
            continue

        if largest_area < cv2.contourArea(c):
            set = 1
            largest_cnt = c
            largest_area = cv2.contourArea(c)
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame2, (x, y), (x + w, y + h), (0, 255, 0), 2)

    if set == 1:
        (x, y, w, h) = cv2.boundingRect(largest_cnt)
        cv2.circle(frame2, (int(w/2 + x), int(h/2 + y)), 5, (0,255,255), -1)
        cv2.rectangle(frame2, (x, y), (x + w, y + h), (255, 255, 0), 2)
    cv2.imshow('frame', frame2)


    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
cap.release()
cv2.destroyAllWindows()