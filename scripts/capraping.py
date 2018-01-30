import os
import re
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup


class CapScraper:

    global start, end, save_dir

    def __init__(self, start_page, end_page, save):
        self.start = start_page
        self.end = end_page
        self.save_dir = save

    def execute(self):
        for i in range(self.start, self.end):
            root_url = "http://anicobin.ldblog.jp/?p="+str(i)
            response = requests.get(root_url, allow_redirects=True, timeout=10)
            soup = BeautifulSoup(response.text)
            anime_urls = soup.find_all("h2", class_='top-article-title')
            for anime in anime_urls:
                try:
                    anime_url = anime.a.get("href")
                    response = requests.get(anime_url, allow_redirects=True, timeout=10)
                    soup = BeautifulSoup(response.text)

                    # ページタイトルからアニメと話数を抽出
                    page_title = soup.find("h1", class_="article-title").string
                    anime_title = re.search(r"【(?P<name>.*?)】", page_title).group("name")
                    anime_title = re.sub(r'[¥/:*?"<>|]', " ", anime_title)
                    story_no = re.search(r"第(?P<no>.*?)話", page_title).group("no")

                    # キャプ保存用ディレクトリ作成
                    anime_dir = os.path.join(self.save_dir, anime_title)
                    if not os.path.exists(anime_dir): os.mkdir(anime_dir)
                    story_dir = os.path.join(anime_dir, "%s話" % story_no)
                    if not os.path.exists(story_dir): os.mkdir(story_dir)

                    img_url_array = [link.get('src') for link in soup.find_all('img')]
                    img_index = 1
                except Exception as e:
                    print("ANIME ERROR", e)
                    continue
                for img_url in img_url_array:
                    try:
                        if not self.is_cap(img_url): continue
                        img_url = self.remake_img_url(img_url)

                        session = requests.Session()
                        retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
                        session.mount("http://", HTTPAdapter(max_retries=retries))
                        session.mount("https://", HTTPAdapter(max_retries=retries))
                        response = session.get(url=img_url, stream=True, timeout=(10.0, 30.0))
                        response.raise_for_status()

                        image = response.content

                        file = "%s_%s話_%s" % (anime_title, story_no, img_index)
                        ext = os.path.splitext(img_url)[1]
                        file_path = os.path.join(story_dir, file + ext)

                        print(file_path)

                        with open(file_path, "wb") as file:
                            file.write(image)
                        img_index += 1
                    except Exception as e:
                        print("IMG ERROR", e)
                        continue

    def extract_img_urls(self, page_url):



    # あにこ便でのみ使用可
    def is_cap(self, img_url):
        pattern = r"http://livedoor.blogimg.jp/anico_bin/imgs/.*-s.(jpg|png|gif)"
        anti_pattern = r"http://resize.blogsys.jp/.*/" + pattern
        result = len(re.findall(pattern, img_url)) > 0
        anti_result = len(re.findall(anti_pattern, img_url)) > 0
        return result and not anti_result


    # あにこ便でのみ使用可
    def remake_img_url(self, img_url):
        remade_url = ""
        ext = os.path.splitext(img_url)[1]
        if ext == ".jpg":
            remade_url = img_url.replace('-s.jpg', '.jpg')
        elif ext == ".png":
            remade_url = img_url.replace('-s.png', '.png')
        return remade_url
