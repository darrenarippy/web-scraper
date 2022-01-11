import string
import requests
import os
import shutil
from bs4 import BeautifulSoup


class NatureScraper:
    def __init__(self):
        self._url = 'https://www.nature.com/nature/articles?sort=PubDate&year=2020'
        self._page_source = {}
        self._articles = {}
        self._saved_articles = {}

    def crawl(self, number_of_pages, article_type):
        for i in range(1, int(number_of_pages) + 1):
            if os.path.exists(f'Page_{i}'):
                shutil.rmtree(f'Page_{i}')
            os.mkdir(f'Page_{i}')
            self._get_page_source(i)
            self._get_articles_from_page(i)
            self._find_articles_by_type_from_page(i, article_type)
            self._save_articles(i)

    def _get_page_source(self, page_number):
        url = self._url + f'&page={page_number}'
        r = requests.get(url)
        if r.status_code == requests.codes.ok:
            self._page_source[page_number] = BeautifulSoup(r.content, 'html.parser')

    def _get_articles_from_page(self, page_number):
        page_articles = self._page_source.get(page_number).find_all('article')
        self._articles[page_number] = page_articles

    def _find_articles_by_type_from_page(self, page_number, article_type):
        self._saved_articles[page_number] = []
        for article in self._articles.get(page_number):
            article_type_span = article.find('span', attrs={'data-test': 'article.type'})
            if article_type_span is not None:
                if article_type_span.contents[1].get_text() == article_type:
                    article_title = article.find('a').get_text()
                    for p in string.punctuation:
                        article_title.maketrans(p, ' ')
                    article_title = '_'.join(article_title.split(' '))
                    link_info = {'title': article_title,
                                 'link': article.find('a')['href']}
                    self._saved_articles.get(page_number).append(link_info)

    def _save_articles(self, page_number):
        for article in self._saved_articles.get(page_number):
            filename = os.getcwd() + f'/Page_{page_number}/' + article['title'] + '.txt'
            file = open(filename, 'wb')
            r = requests.get('https://nature.com' + article['link'])
            if r.status_code == requests.codes.ok:
                soup = BeautifulSoup(r.content, 'html.parser')
                file.write(bytes(soup.find('div', 'c-article-body').get_text().strip(), 'utf-8'))
            file.close()


def main():
    scraper = NatureScraper()
    scraper.crawl(input(), input())
    print('Saved all articles.')


if __name__ == '__main__':
    main()
