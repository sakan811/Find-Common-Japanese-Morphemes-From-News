import bs4
import requests
from bs4 import BeautifulSoup
from requests import Response

from jp_news_scraper_pipeline.configure_logging import configure_logging_with_file

logger = configure_logging_with_file(log_file='main.log', logger_name='main', level='INFO')


def extract_href_tags(soup: BeautifulSoup) -> list[str]:
    """
    Extract all href attributes from anchor tags to get a list of URLs.
    :param soup: BeautifulSoup object.
    :return: List of URLs.
    """
    logger.info(f'Extract href attributes with BeautifulSoup')
    href_tags = soup.find_all('a', href=True)
    if len(href_tags) == 0:
        logger.error("No href tags found.")
        logger.info("Return an empty list")
        return []
    else:
        return [tag['href'] for tag in href_tags]


def parse_response_to_bs4(response: Response) -> BeautifulSoup:
    """
    Parse URL response to BeautifulSoup.
    :param response: Response from the URL.
    :return: BeautifulSoup object.
    """
    logger.info(f'Parsing a response to BeautifulSoup')
    return BeautifulSoup(response.text, 'html.parser')


def get_unique_urls(url: str) -> list[str]:
    """
    Get a list of unique URLs from the given URL.
    :param url: URL to parse.
    :return: List of unique URLs.
    """
    logger.info(f'Get unique hrefs from {url}')
    response = requests.get(url)
    soup = parse_response_to_bs4(response)
    url_list = extract_href_tags(soup)
    return list(set(url_list))


def find_all_news_articles(inner_soup) -> bs4.ResultSet | None:
    """
    Find all news articles from the section tag.
    :param inner_soup: BeautifulSoup object.
    :return: Set of the news articles found by BeautifulSoup or None if news articles not found.
    """
    logger.debug('Find all news articles\' texts from section tags')
    news_articles: bs4.ResultSet = inner_soup.find_all('section', class_='content--detail-main')
    if len(news_articles) == 0:
        return None
    else:
        return news_articles


def append_extracted_text(news_articles: bs4.ResultSet) -> list[str]:
    """
    Append the extracted text to a list.
    :param news_articles: Scraped news articles.
    :return: List of extracted texts from the scraped news articles.
    """
    logger.debug('Append the extracted text from the scraped news articles to a list')
    news_article_list = []
    for news_article in news_articles:
        news_article_list.append(news_article.text)
    return news_article_list


def extract_text_from_url_list(href_list: list[str]) -> list[str]:
    """
    Extract all text from the given href attributes.
    :param href_list: List of href attributes.
    :return: List of extracted texts.
    """
    logger.info('Extract news articles\' texts from a href list')
    text_list = []
    for href in href_list:
        url = 'https://www3.nhk.or.jp' + href

        inner_response = requests.get(url)
        inner_response.encoding = 'utf-8'
        inner_soup = BeautifulSoup(inner_response.text, 'html.parser')

        news_articles = find_all_news_articles(inner_soup)

        if news_articles:
            text_list += append_extracted_text(news_articles)
        else:
            logger.warning(f"No news articles found from url: {url}.")

    if not text_list:
        logger.warning('No text extracted from the news articles')

    return text_list
