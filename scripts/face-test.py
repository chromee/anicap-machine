import animeface
import PIL.Image
from PIL import ImageOps
import cv2
import os

path = r"/code/data/"
files = os.listdir(path)
face_cascade = cv2.CascadeClassifier(r"/code/cascaders/lbpcascade_animeface.xml")

i = 1
for file in files:
    if os.path.isdir(file): continue
    print(path+file)
    img = cv2.imread(path+file)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_rects = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(100, 100))

    for (x, y, w, h) in face_rects:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    im = PIL.Image.open(path+file)
    gray = ImageOps.grayscale(im)
    faces = animeface.detect(gray)

    for face in faces:
        x = face.face.pos.x
        y = face.face.pos.y
        w = face.face.pos.width
        h = face.face.pos.height
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imwrite(r"/code/data/face/"+str(i)+".jpg", img)
    i+=1
