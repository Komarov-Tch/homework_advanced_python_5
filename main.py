from datetime import datetime
import json
import requests as req
import re
from bs4 import BeautifulSoup as Bs


def logged(namefile, t_start):
    def my_decor(func):
        def decorated_func(*args, **kwargs):
            result = func(*args, **kwargs)
            log = {
                'time': str(datetime.now() - t_start),
                'name_func': func.__name__,
                'args': args,
                'kwargs': kwargs,
                'result': result
            }
            with open(f'{namefile}.txt', 'a') as out:
                json.dump(
                    f'{log["time"]}:'
                    f'{log["name_func"]}:'
                    f'{log["args"]}:'
                    f'{log["kwargs"]}:'
                    f'{log["result"]}\n', out)
            return result

        return decorated_func

    return my_decor


start = datetime.now()
name_file = input('введите название файла: ')


@logged(name_file, start)
def cleaning_list(news: list, KEYWORDS: list) -> list:
    cleaning_news = []
    for n in news:
        blog_text = re.findall(r'[а-яёА-ЯЁa-zA-Z-]+', n['text'])
        search_keywords = any(map(lambda word: word in blog_text, KEYWORDS))
        if search_keywords:
            cleaning_news.append([n['date'], n['title'], n['link']])
    return cleaning_news


@logged(name_file, start)
def create_news_list(soup: list) -> list:
    tag1 = 'article-formatted-body article-formatted-body article-formatted-body_version-1'
    tag2 = 'article-formatted-body article-formatted-body article-formatted-body_version-2'
    news = []
    for i in soup:
        head = i.find('a', {'class': 'tm-article-snippet__title-link'})
        title = head.text
        link = 'https://habr.com' + head.get('href')
        text1 = i.find('div', class_=tag1)
        text2 = i.find('div', class_=tag2)
        text_news = text1 if text1 else text2
        date = i.find('span', {'class': 'tm-article-snippet__datetime-published'}).find('time').get('datetime')[:10]
        news.append({
            'date': date,
            'title': title,
            'link': link,
            'text': str(text_news)
        })
    return news



def cooking(response: req.models.Response) -> list:
    soup = Bs(response.text, 'html.parser')
    result_review = soup.find_all('article', {'data-test-id': "articles-list-item"})
    return result_review


def main():
    KEYWORDS = ['дизайн', 'фото', 'web', 'python']
    url = 'https://habr.com/ru/all/'
    response = req.get(url, headers={'User-Agent': 'Chrome'})
    soup = cooking(response)
    news = create_news_list(soup)
    clean_news = cleaning_list(news, KEYWORDS)
    for n in clean_news:
        print(f'{n[0]} - {n[1]} - {n[2]}')


main()
