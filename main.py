from os import lseek
import time
import json

import httpx
from bs4 import BeautifulSoup

class DCBestFetcher:
    requests = 0
    client = httpx.Client(cookies=httpx.Cookies())
    mainpage_content = ''
    url_list = []
    posts = []

    def fetch_timebest_page(self):
        headers = {'user-agent': 'curl/8.15.0'}
        url = "https://gall.dcinside.com/board/lists?id=dcbest"
        self.mainpage_content = self.client.get(url, headers=headers).text
        self.requests += 1

    def get_post_urls(self):
        soup = BeautifulSoup(self.mainpage_content, 'html.parser')
        for el in soup.css.select(".ub-content .gall_tit a:first-of-type"):
            href = el.get('href')
            if href == 'javascript:;':
                continue
            self.url_list.append(f"https://gall.dcinside.com{href}")
        self.url_list.pop(0)

    def add_post_content(self, url):
        headers = {'user-agent': 'curl/8.15.0'}
        comment_headers = {'user-agent': 'curl/8.15.0', 'x-requested-with': 'XMLHttpRequest'}
        post_object = {}

        content = self.client.get(url, headers=headers).text
        soup = BeautifulSoup(content, 'html.parser')
        
        title_span = soup.css.select_one('span.title_subject')
        write_div = soup.css.select_one('div.write_div')
        post_object['title'] = title_span.get_text()
        post_object['content'] = write_div.get_text()
        post_object['comments'] = []

        esno = soup.css.select_one("input#e_s_n_o").get('value')
        comment_post_data = {}

        url_data = httpx.URL(url)

        comment_post_data['id'] = url_data.params.get('id')
        comment_post_data['cmt_id'] = url_data.params.get('id')
        comment_post_data['no'] = url_data.params.get('no')
        comment_post_data['cmt_no'] = url_data.params.get('no')
        comment_post_data['e_s_n_o'] = esno
        comment_post_data['comment_page'] = '1'
        comment_post_data['sort'] = 'D'
        comment_post_data['_GALLTYPE_'] = 'G'

        comment_page = 0
        while True:
            comment_page += 1
            comment_post_data['comment_page'] = comment_page
            comments_response = self.client.post("https://gall.dcinside.com/board/comment/", 
                                            headers=comment_headers, data=comment_post_data)
            time.sleep(0.8)

            if comments_response.status_code != 200:
                break
            comments = json.loads(comments_response.text)
            if comments['comments'] == None:
                break

            for cmt in comments['comments']:
                if cmt['memo'][0] == "<":
                    continue
                post_object['comments'].append(cmt['memo'])

        self.posts.append(post_object)
    
    def save_posts_json(self):
        self.fetch_timebest_page()
        self.get_post_urls()
        for url in self.url_list:
            self.add_post_content(url)
        file = open("posts.json", 'w')
        file.write(json.dumps(self.posts, ensure_ascii=False))

fetcher = DCBestFetcher()
fetcher.save_posts_json()
