#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# 2019. Artem Bondar
#

import click
import requests

from bs4 import BeautifulSoup
from collections import Counter
from typing import Optional, List, Tuple

from nltk.tokenize import wordpunct_tokenize
from nltk.corpus import stopwords


class InvalidUrlException(Exception):
    def __init__(self, url: str, code: Optional[int]=None):
        """
        Raised, when have issues with fetching web page
        :param url: url of page, which couldn't be loaded
        """
        super().__init__()
        self.url, self.code = url, code

    def __str__(self):
        if self.code is None:
            return 'Exception occurred while loading {}'.format(self.url)
        else:
            return 'Remote server returned {} code for {}'.format(self.code, self.url)


class InvalidHtmlData(Exception):
    def __init__(self):
        """
        Raised if the data, passed to the parser is a not a valid html
        """
        super().__init__()

    def __str__(self):
        return 'Given web page is not a valid html file'


def fetch_web_page(url: str, verbose: bool) -> str:
    """
    load web page via http and return it's html text if possible

    :param url: web page's url
    :return: html text for this web page
    """
    try:
        req_response = requests.get(url)
        if req_response.status_code != 200:
            raise InvalidUrlException(url, req_response.status_code)
        return req_response.text
    except Exception as e:
        if verbose:
            print('Exception during loading web page: {}'.format(e))
        raise InvalidUrlException(url)


def text_corpus_from_html(html_text: str, verbose: bool) -> Tuple[str, List[str]]:
    """
    grabs all the text data from<div></div> tags on given web page and the web page's title

    :param html_text: web page's text
    :param verbose: verbosity
    :return: title and list of found text phrases on this page
    """
    try:
        soup_parse = BeautifulSoup(html_text, 'html.parser')

        # for every div node take all the children, which are strings, and flatten them into single array
        text_pieces = [content for node in soup_parse.find_all('div') for content in node.contents if isinstance(content, str)]

        # also split pieces of text into the lines (and un-nest)
        all_lines = [line for text_piece in text_pieces for line in text_piece.strip().split('\n')]

        # and remove empty ones
        all_lines = list(filter(lambda line: len(line) > 0, all_lines))

        title = soup_parse.title.string
        return title, all_lines
    except Exception as e:
        if verbose:
            print('Exception occurred during parsing: {}'.format(e))
        raise InvalidHtmlData()


def term_frequency_stats(all_texts: List[str], verbose: bool) -> Counter:
    """
    Term frequency calculations for given corpora details:

    - all string are tokenized using nltk default tokenizer
    - stopwords are removed using nltk's default dictionary (which seems to be similar to
      mentioned in task https://www.ranks.nl/stopwords)

    :param all_texts: list of string lines to be processed
    :return: Counter, containing given-corpora-words and their frequencies
    """

    terms = Counter()
    stop_words = set(stopwords.words('english'))
    for text in all_texts:
        # tokenize and lowercase
        tokens = (t.lower() for t in wordpunct_tokenize(text) if t.isalpha())

        # filter stopwords
        for term in filter(lambda t: t not in stop_words, tokens):

            # and count stats
            terms[term] += 1

    return terms


def print_term_frequencies_stats(title, terms_frequencies, first_n=None):
    print(title)
    print('')

    # at first calculate output lines len (at least 16)
    out_lines_text_len, out_lines_freq_len = 12, 4
    for term, frequency in terms_frequencies.most_common(first_n):
        out_lines_text_len = max(out_lines_text_len, len(term))
        out_lines_freq_len = max(out_lines_freq_len, len(str(frequency)))

    # now print the results
        print('{} {}'.format(
            term.ljust(out_lines_text_len),
            str(frequency).rjust(out_lines_freq_len))
        )


@click.command(help='Calculates term frequency for given web page')
@click.argument('url')
@click.option('--verbose', '-v', is_flag=True, default=False)
def calculate_term_frequency(url: str, verbose: bool):
    if verbose:
        print('Start calculating for URL: {}'.format(url))
    try:
        html_text = fetch_web_page(url, verbose)
        title, text_corpus = text_corpus_from_html(html_text, verbose)
        term_frequencies_stats = term_frequency_stats(text_corpus, verbose)
        print_term_frequencies_stats(title, term_frequencies_stats)
    except InvalidUrlException as e:
        print('Failed. {}'.format(str(e)))
    except InvalidHtmlData as e:
        print('Failed. {}'.format(str(e)))
    except Exception as e:
        print('Failed. Unexpected exception occurred: {}'.format(e))


if __name__ == '__main__':
    calculate_term_frequency()
