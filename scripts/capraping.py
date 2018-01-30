import os, re, time, requests, threading
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
from pathlib import Path


class CapScraper:

    def __init__(self, start_page, end_page, save):
        self.lock = threading.Lock()
        self.start = start_page
        self.end = end_page
        self.save_dir = save
        self.fail_file = str(Path(__file__).parent.parent.joinpath('done.txt'))

    def execute(self):
        for page in range(self.start, self.end):
            root_url = "http://anicobin.ldblog.jp/?p="+str(page)
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
                    if os.path.exists(story_dir):
                        continue    # すでにある時はスキップ
                    else:
                        os.mkdir(story_dir)

                    img_url_array = [link.get('src') for link in soup.find_all('img')]
                    img_index = 1
                except Exception as e:
                    print("ANIME ERROR", e)
                    continue

                start_time = time.time()
                for img_url in img_url_array:
                    if not self.is_cap(img_url): continue
                    img_url = self.remake_img_url(img_url)

                    wait_sec = 0.1
                    max_download = 10
                    while threading.active_count() > max_download:
                        time.sleep(wait_sec)

                    file = "%s_%s話_%s" % (anime_title, story_no, img_index)
                    ext = os.path.splitext(img_url)[1]
                    file_path = os.path.join(story_dir, file + ext)

                    threading.Thread(name=img_url, target=self.download_image, args=(page, img_url, file_path)).start()
                    img_index += 1
                end_time = time.time()
                print("{0} ms".format((end_time - start_time) * 1000))

    def download_image(self, page, img_url, file_path):
        try:
            session = requests.Session()
            retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
            session.mount("http://", HTTPAdapter(max_retries=retries))
            session.mount("https://", HTTPAdapter(max_retries=retries))
            response = session.get(url=img_url, stream=True, timeout=(10.0, 30.0))
            image = response.content

            with open(file_path, "wb") as file:
                file.write(image)

            print("page:%s \t path:%s" % (page, file_path))
        except Exception as e:
            self.save_fail(img_url)
            print("IMG ERROR", e)

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

    def save_fail(self, url):
        self.lock.acquire()
        with open(self.fail_file, 'a') as f:
            f.write(url + '\n')
        self.lock.release()
