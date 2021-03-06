import os
import csv
import cv2
import shutil
import numpy as np
from pathlib import Path


class CapManager:

    SAFE_MODE = 0
    DELETE_MODE = 1

    global caps_dir, save_dir, face_cascade, no_face_img_db

    def __init__(self, dir, face_dir):
        project_dir = Path(__file__).parent.parent
        self.face_cascade = cv2.CascadeClassifier(str(project_dir.joinpath(r"cascaders/lbpcascade_animeface.xml")))
        self.no_face_img_db = open(str(project_dir.joinpath(r'data/no_face_img_db.csv')), 'w')
        self.caps_dir = Path(dir)
        self.save_dir = face_dir

    def extract_face_and_save(self):
        if not os.path.exists(self.save_dir): os.mkdir(self.save_dir)
        writer = csv.writer(self.no_face_img_db, lineterminator='\n')

        for file in self.find_all_files():
            if os.path.isdir(file): continue
            print("face detect:", file)
            img = self.imread(file)
            face_rect = self.get_faces(img)

            if face_rect is None:
                writer.writerow([file])
                continue

            for (x, y, w, h) in face_rect:
                self.imwrite(self.save_dir+"/"+os.path.basename(file), img[y:y+h, x:x+w])
        self.no_face_img_db.close()

    def find_all_files(self):
        for root, dirs, files in os.walk(str(self.caps_dir)):
            yield root
            for file_path in files:
                yield os.path.join(root, file_path)

    def get_faces(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_rect = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(100, 100))

        if len(face_rect) <= 0: return None
        return face_rect

    def imread(self, filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
        try:
            n = np.fromfile(filename, dtype)
            img = cv2.imdecode(n, flags)
            return img
        except Exception as e:
            print("READ ERROR", e)
            return None

    def imwrite(self, filename, img, params=None):
        try:
            ext = os.path.splitext(filename)[1]
            result, n = cv2.imencode(ext, img, params)

            if result:
                with open(filename, mode='w+b') as f:
                    n.tofile(f)
                return True
            else:
                return False
        except Exception as e:
            print("WRITE ERROR", e)
            return False

    def delete_similar_pictures(self, mode):
        files = os.listdir(str(self.caps_dir))
        if len(files) == 0: return 0

        safe_dir = str(self.caps_dir.joinpath("shelter"))
        if mode == self.SAFE_MODE:
            if not os.path.exists(safe_dir): os.mkdir(safe_dir)

        img_size = (320, 180)
        target_file_name = files[0]
        for file in files:
            if file == target_file_name: continue
            target_img_path = str(self.caps_dir.joinpath(target_file_name))
            target_img = cv2.imread(target_img_path)
            target_img = cv2.resize(target_img, img_size)
            target_hist = cv2.calcHist([target_img], [0], None, [256], [0, 256])

            comparing_img_path = str(self.caps_dir.joinpath(file))
            comparing_img = cv2.imread(comparing_img_path)
            comparing_img = cv2.resize(comparing_img, img_size)
            comparing_hist = cv2.calcHist([comparing_img], [0], None, [256], [0, 256])

            ret = cv2.compareHist(target_hist, comparing_hist, 0)

            if ret < 0.95:
                target_file_name = file
            else:
                if mode == self.SAFE_MODE:
                    shutil.move(comparing_img_path, safe_dir + file)
                elif mode == self.DELETE_MODE:
                    os.remove(comparing_img_path)
