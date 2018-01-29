import os
import cv2
import shutil
from pathlib import Path


class CapManager:

    SAFE_MODE = 0
    DELETE_MODE = 1

    def ___init___(self, anime, story_no):
        self.anime = anime
        self.story_no = story_no
        self.caps_dir = Path(__file__).parent.parent.parent.parent.joinpath("images").joinpath(anime).joinpath(story_no)
        self.face_cascade = cv2.CascadeClassifier(str(Path(__file__).parent.parent.joinpath("cascaders/lbpcascade_animeface.xml")))

    def extract_and_save_face(self):
        files = os.listdir(str(self.caps_dir))
        if len(files) == 0: return

        save_dir = str(self.caps_dir.joinpath("face"))
        if not os.path.exists(save_dir): os.mkdir(save_dir)
        for file in files:
            img = cv2.imread(file)
            face_rect = self.__get_faces(img)
            if face_rect is None: continue

            for (x, y, w, h) in face_rect:
                cv2.imwrite("", img[y:y+h, x:x+w])

    def __get_faces(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_rect = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=1, minSize=(10,10))

        if len(face_rect) <= 0: return None
        return face_rect

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
