import numpy as np
import cv2

cap = cv2.VideoCapture(r"D:\apex\Apex Legends 2022.10.15 - 12.05.55.03.DVR.mp4")

while cap.isOpened():
    ret, frame = cap.read()
    cv2.imshow("frame", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
