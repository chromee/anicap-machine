import os
import requests


class RailsConnector:

    global post_url

    def __init__(self, rails_url):
        self.post_url = rails_url

    def send_picture(self, file_path):
        img = open(file_path, "rb")
        file_name = os.path.basename(file_path)
        ext = os.path.splitext(file_path)[1].lstrip(".")

        data = {"picture[name]": file_name, "picture[tag_list]": "aaa"}
        files = {"picture[photo]": (file_name, img, "image/jpeg")}

        res = requests.post(self.post_url, data=data, files=files)
        print(res.status_code)
