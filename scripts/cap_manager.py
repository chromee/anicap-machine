import os
import cv2
import shutil
from pathlib import Path
import numpy as np


class CapManager:

    SAFE_MODE = 0
    DELETE_MODE = 1

    def ___init___(self, cap, anime, story_no):
        self.anime = anime
        self.story_no = story_no
        root = Path(__file__).parent.parent
        self.caps_dir = str(Path(cap).joinpath(anime).joinpath(story_no))
        self.face_cascade = cv2.CascadeClassifier(str(root.joinpath(r"cascaders/lbpcascade_animeface.xml")))

    def extract_face_and_save(self):
        save_dir = str(self.caps_dir.joinpath("face"))
        if not os.path.exists(save_dir): os.mkdir(save_dir)

        for file in self.__find_all_files(self.caps_dir):
            if os.path.isdir(file): continue
            img = self.__imread(file)
            face_rect = self.__get_faces(img)
            if face_rect is None: continue

            for (x, y, w, h) in face_rect:
                self.__imwrite("", img[y:y+h, x:x+w])

    def __find_all_files(self, directory):
        for root, dirs, files in os.walk(directory):
            yield root
            for file_path in files:
                yield os.path.join(root, file_path)

    def __get_faces(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_rect = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=1, minSize=(10,10))

        if len(face_rect) <= 0: return None
        return face_rect

    def __imread(self, filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
        try:
            n = np.fromfile(filename, dtype)
            img = cv2.imdecode(n, flags)
            return img
        except Exception as e:
            print(e)
            return None

    def __imwrite(self, filename, img, params=None):
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
            print(e)
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
