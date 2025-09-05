import time
import json

import httpx
from bs4 import BeautifulSoup

headers = {'user-agent': 'curl/8.15.0'}
client = httpx.Client(cookies=httpx.Cookies())

def fetch_timebest():
    url = "https://gall.dcinside.com/board/lists?id=dcbest"
    return client.get(url, headers=headers).text

def get_post_urls(content):
    soup = BeautifulSoup(content, 'html.parser')
    url_list = []
    for el in soup.css.select(".ub-content .gall_tit a:first-of-type"):
        href = el.get('href')
        if href == 'javascript:;':
            continue
        url_list.append(f"https://gall.dcinside.com{href}")
    return url_list

def add_post_content(url, ls):
    print(url)
    comment_headers = {'user-agent': 'curl/8.15.0', 'x-requested-with': 'XMLHttpRequest'}

    content = client.get(url, headers=headers).text
    soup = BeautifulSoup(content, 'html.parser')

    esno = soup.css.select_one("input#e_s_n_o").get('value')
    comment_post_data = {}

    url_data = httpx.URL(url)
    comment_page = 0

    comment_post_data['id'] = url_data.params.get('id')
    comment_post_data['cmt_id'] = url_data.params.get('id')
    comment_post_data['no'] = url_data.params.get('no')
    comment_post_data['cmt_no'] = url_data.params.get('no')
    comment_post_data['e_s_n_o'] = esno
    comment_post_data['comment_page'] = '1'
    comment_post_data['sort'] = 'D'
    comment_post_data['_GALLTYPE_'] = 'G'

    while True:
        comment_page += 1
        comment_post_data['comment_page'] = comment_page
        comments_response = client.post("https://gall.dcinside.com/board/comment/", 
                                        headers=comment_headers, data=comment_post_data)

        if comments_response.status_code != 200:
            break
        comments = json.loads(comments_response.text)
        if comments['comments'] == None:
            break

        for cmt in comments['comments']:
            if cmt['memo'][0] == "<":
                continue
            ls.append(cmt['memo'])

    title_span = soup.css.select_one('span.title_subject')
    write_div = soup.css.select_one('div.write_div')
    content = title_span.get_text() + write_div.get_text()

    ls.append(content)
