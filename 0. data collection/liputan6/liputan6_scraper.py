import requests
from bs4 import BeautifulSoup as bs
import json, os, glob
import threading
from scraper_utils import write_file, load_data

def get_id(url):
    '''Getting the ID of the news from its url'''
    return url.split('/')[-2]

def get_summary(text):
    summary = ''
    for line in text.split('\n'):
        if 'window.kmklabs.channel =' in line:
            target = line
            break
    temp = target.split('window.kmklabs.article = ')[1]
    temp = temp.split(';')[0]
    data = json.loads(temp)
    return data['shortDescription']

def collect_data(text):
    soup = bs(text)
    title = soup.find_all('h1', {'class': 'read-page--header--title'})[0].get_text()
    date = soup.find_all('time', {'class': 'read-page--header--author__datetime updated'})[0].get_text()
    contents = soup.find_all('div', {'class': 'article-content-body__item-content'})
    article = []
    for content in contents:
        article.append(content.get_text())
    summary = get_summary(text)
    return title, date, article, summary

def scrape_article(url, destination):
    request = requests.get(url)
    url = request.url
    id = get_id(url)
    title, date, article, summary = collect_data(request.text)

    write_file(id, url, title, date, article, summary, destination)

def multiple_article_scraper(urls, destination):
    num_error = 0
    for i, url in enumerate(urls):
        try:
            scrape_article(url, destination)
        except:
            num_error += 1
            print('Error scraping ID {}; {}'.format(get_id(url), url))

def multi_threading(urls, destination, num_thread=1):
    os.makedirs(destination, exist_ok=True)
    threads = []
    for i in range(num_thread):
        cur_idx = int(i*len(urls)/num_thread)
        cur_urls = urls[cur_idx:cur_idx+int(len(urls)/num_thread)]
        t = threading.Thread(target=multiple_article_scraper, args=(cur_urls, destination,))
        threads.append(t)
        t.start()


#url = 'https://www.liputan6.com/regional/read/4947491/resensi-babad-banyumas-belajar-sejarah-dengan-cara-asyik-melalui-komik'
#scrape_article(url, 'dataset')

urls = load_data('0. data collection/liputan6/url.json')

THREAD = 1

multi_threading(urls['dev_urls'], 'dataset/raw/dev', THREAD)
multi_threading(urls['test_urls'], 'dataset/raw/test', THREAD)
multi_threading(urls['train_urls'], 'dataset/raw/train', THREAD)