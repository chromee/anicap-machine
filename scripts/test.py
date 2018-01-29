import os
import re
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup


def __is_cap(img_url):
    pattern = r"http://livedoor.blogimg.jp/anico_bin/imgs/.*-s.(jpg|png|gif)"
    anti_pattern = r"http://resize.blogsys.jp/.*/" + pattern
    result = len(re.findall(pattern, img_url)) > 0
    anti_result = len(re.findall(anti_pattern, img_url)) > 0
    return result and not anti_result


def __remake_img_url(img_url):
    remade_url = ""
    ext = os.path.splitext(img_url)[1]
    if ext == ".jpg":
        remade_url = img_url.replace('-s.jpg', '.jpg')
    elif ext == ".png":
        remade_url = img_url.replace('-s.png', '.png')
    return remade_url

cap_dir = r"D:\cap2"
anime_url = "http://anicobin.ldblog.jp/archives/52872569.html"
response = requests.get(anime_url, allow_redirects=True, timeout=10)
soup = BeautifulSoup(response.text)

page_title = soup.find("h1", class_="article-title").string
anime_title = re.search(r"【(?P<name>.*?)】", page_title).group("name")
story_no = re.search(r"第(?P<no>.*?)話", page_title).group("no")
img_url_array = [link.get('src') for link in soup.find_all('img')]
img_index = 1
for img_url in img_url_array:
    try:
        if not __is_cap(img_url): continue
        img_url = __remake_img_url(img_url)

        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        session.mount("http://", HTTPAdapter(max_retries=retries))
        session.mount("https://", HTTPAdapter(max_retries=retries))
        response = session.get(url=img_url, stream=True, timeout=(10.0, 30.0))
        response.raise_for_status()

        image = response.content

        anime_dir = os.path.join(cap_dir, anime_title)
        if not os.path.exists(anime_dir): os.mkdir(anime_dir)
        story_dir = os.path.join(anime_dir, "%s話" % story_no)
        if not os.path.exists(story_dir): os.mkdir(story_dir)

        file = "%s_%s話_%s" % (anime_title, story_no, img_index)
        ext = os.path.splitext(img_url)[1]
        file_name = file + ext
        file_path = os.path.join(story_dir, file_name)

        print(file_path)

        with open(file_path, "wb") as file:
            file.write(image)
        img_index += 1

    except Exception as e:
        print("IMG ERROR", e)
        continue
