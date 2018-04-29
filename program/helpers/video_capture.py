from datetime import datetime
import numpy as np
import cv2

cap = [cv2.VideoCapture(i) for i in range(3)]

fourcc = cv2.VideoWriter_fourcc(*'XVID')

names = [datetime.now().strftime("%Y-%m-%d-at-%H-%M") + '-' + str(i) + '.avi' for i in range(len(cap))]
outputs = [cv2.VideoWriter('captured_videos/' + output, fourcc, 20.0, (640,480)) for output in names]
exit = False
while True:
    for i, c in enumerate(cap):
        ret, frame = c.read()
        if ret == True:
            outputs[i].write(frame)

            cv2.imshow('frame' + str(i),frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                exit = True
                break
        else:
            exit = True
            break
    if exit:
        break

# Release everything if job is finished
for i, c in enumerate(cap):
    c.release()
    outputs[i].release()

cv2.destroyAllWindows()