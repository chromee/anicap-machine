import os
import re
import struct
import requests
import urllib.request
from bs4 import BeautifulSoup

cap_save_dir = ""

class Capraping:

    global x, y, start, end

    def __init__(self, min_x, min_y, start_page, end_page):
        self.x = min_x
        self.y = min_y
        self.start = start_page
        self.end = end_page

    def execute(self):
        for i in range(self.start, self.end):
            root_url = "http://anicobin.ldblog.jp/?p="+str(i)
            response = requests.get(root_url, allow_redirects=True, timeout=10)
            soup = BeautifulSoup(response.text)
            anime_urls = soup.find_all("h2", class_='top-article-title')
            for anime in anime_urls:
                anime_url = anime.a.get("href")

                response = requests.get(anime_url, allow_redirects=True, timeout=10)
                soup = BeautifulSoup(response.text)
                img_url_array = [link.get('src') for link in soup.find_all('img')]

                page_title = soup.find("h1", class_="article-title").string
                anime_title = re.search(r"【(?P<name>.*?)】", page_title).group("name")
                story_no = re.search(r"第(?P<no>.*?)話", anime_title).group("no")

                img_index = 1
                for img_url in img_url_array:
                    if not __is_cap(img_url): continue

                    image_size = __get_img_size(img_url)
                    if not (image_size[0] > x and image_size[1] > y): continue

                    img_url = __remake_img_url(img_url)
                    response = requests.get(img_url, allow_redirects=True, timeout=10)
                    image = response.content

                    anime_dir = os.path.join(cap_save_dir, anime)
                    if not os.path.exists(anime_dir): os.mkdir(anime_dir)
                    story_dir = os.path.join(anime_dir, "%s_%s話" % (anime, story_no))
                    if not os.path.exists(story_dir): os.mkdir(story_dir)
                    file = "%s_%s_%s" % (anime, story_no, img_index)
                    ext = os.path.splitext(img_url)[1]
                    file_name = file + ext
                    file_path = os.path.join(story_dir, file_name)

                    print(file_path)

                    with open(file_path, "wb") as file:
                        file.write(image)
                    img_index += 1


    # あにこ便でのみ使用可
    def __is_cap(self, img_url):
        pattern = r"http://livedoor.blogimg.jp/anico_bin/imgs/.*-s.(jpg|png|gif)"
        anti_pattern = r"http://resize.blogsys.jp/.*/" + pattern
        result = len(re.findall(pattern, img_url)) > 0
        anti_result = len(re.findall(anti_pattern, img_url)) > 0
        return result and not anti_result


    # あにこ便でのみ使用可
    def __remake_img_url(self, img_url):
        remade_url = ""
        ext = os.path.splitext(img_url)[1]
        if ext == ".jpg":
            remade_url = img_url.replace('-s.jpg', '.jpg')
        elif ext == ".png":
            remade_url = img_url.replace('-s.png', '.png')
        return remade_url


    def __get_img_size(self, url):
        response = urllib.request.urlopen(url)
        size = (-1, -1)
        if response.status == 200:
            signature = response.read(2)
            if signature == b'\xff\xd8':  # jpg
                while not response.closed:
                    (marker, size) = struct.unpack('>2sH', response.read(4))
                    if marker == b'\xff\xc0':
                        (_, height, width, _) = struct.unpack('>chh10s', response.read(size - 2))
                        size = width, height
                    else:
                        response.read(size - 2)
            elif signature == b'\x89\x50':  # png
                (_, width, height) = struct.unpack(">14sII", response.read(22))
                size = width, height
            elif signature == b'\x47\x49':  # gif
                (_, width, height) = struct.unpack("<4sHH", response.read(8))
                size = width, height
        response.close()
        return size
