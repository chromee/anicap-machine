import cv2
import numpy as np
import sys
import os

drawing = False
sx, sy = 0, 0
gx, gy = 0, 0
rectangles = []
ok = False


def draw_circle(event, x, y, flags, param):
    global sx, sy, gx, gy, drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        sx, sy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if 0 < x < img.shape[1]:
            gx = x
        if 0 < y < img.shape[0]:
            gy = y

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        w = abs(sx - x)
        h = abs(sy - y)
        if w < h * 1.1 and h < w * 1.1:
            rectangles.append([(sx, sy), (x, y)])


img = np.zeros((512, 512, 3), np.uint8)
cv2.namedWindow('image')
cv2.setMouseCallback('image', draw_circle)

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
img_dir = project_dir + '/data/test/front/'
finish_img_dir = project_dir + '/data/test/front/finish/'

finish_data = []
index = 1

files = os.listdir(img_dir)
for file in files:
    rectangles = []
    while True:
        img = cv2.imread(img_dir + file)

        for r in rectangles:
            cv2.rectangle(img, r[0], r[1], (255, 255, 255), 2)

        if drawing:
            w = abs(sx - gx)
            h = abs(sy - gy)
            if w < h * 1.1 and h < w * 1.1:
                color = (0, 255, 0)
            else:
                color = (0, 0, 255)
            cv2.rectangle(img, (sx, sy), (gx, gy), color, 2)
        cv2.imshow('image', img)

        k = cv2.waitKey(1) & 0xFF
        if k == ord('d'):
            if rectangles:
                rectangles.pop()
        elif k == ord('s'):
            if len(rectangles) > 0:
                for r in rectangles:
                    x = min(r[0][0], r[1][0])
                    y = min(r[0][1], r[1][1])
                    w = abs(r[0][0] - r[1][0])
                    h = abs(r[0][1] - r[1][1])
                    trimming_img = img[y:y+h, x:x+w]
                    cv2.imwrite(finish_img_dir+"front"+"{0:03d}".format(index)+".jpg", trimming_img)
                    index += 1
                break
        elif k == ord('q'):
            sys.exit()

sys.exit()
