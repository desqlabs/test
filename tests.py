#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# 2019. Artem Bondar
#

import unittest

from scan import term_frequency_stats, text_corpus_from_html
from scan import InvalidHtmlData


class TestTermFrequency(unittest.TestCase):

    def test_empty(self):
        lines = []
        terms = term_frequency_stats(lines, verbose=False)
        self.assertListEqual(list(terms), [])

    def test_empty_lines(self):
        lines = ['', '']
        terms = term_frequency_stats(lines, verbose=False)
        self.assertListEqual(list(terms), [])

    def test_stopwords(self):
        lines = ['a about hamburger']
        terms = term_frequency_stats(lines, verbose=False)
        self.assertListEqual(list(terms), ['hamburger'])

    def test_lowercasing(self):
        lines = ['Hamburger hamburger']
        terms = term_frequency_stats(lines, verbose=False)
        self.assertListEqual(list(terms), ['hamburger'])

    def test_punctuation(self):
        lines = ['Hamburger? hamburger!']
        terms = term_frequency_stats(lines, verbose=False)
        self.assertListEqual(list(terms), ['hamburger'])

    def test_counting(self):
        lines = ['hamburger hamburger hamburger']
        terms = term_frequency_stats(lines, verbose=False)
        self.assertEqual(terms['hamburger'], 3)

class TestParser(unittest.TestCase):

    def test_trivial(self):
        html = '''
            <html>
                <head>
                    <title>hey</title>
                </head>
                <body>
                    <div>hello world&#33;</div>
                </body>
            </html>
        '''
        title, lines = text_corpus_from_html(html, verbose=False)
        self.assertListEqual(lines, ['hello world!'])
        self.assertEqual(title, 'hey')

    def test_nested(self):
        html = '''
        <html>
            <head>
                <title>hey</title>
            </head>
            <body>
                <div>hello world
                    <div>how are you&#33;</div>
                </div>
            </body>
        </html>
        '''
        title, lines = text_corpus_from_html(html, verbose=False)
        self.assertListEqual(lines, ['hello world', 'how are you!'])
        self.assertEqual(title, 'hey')

    def test_deep_nested(self):
        html = '''
        <html>
            <head>
                <title>hey</title>
            </head>
            <body>
                <div>hello world
                    <cell>
                        <div>how are you</div>
                    </cell>
                </div>
            </body>
        </html>
        '''
        title, lines = text_corpus_from_html(html, verbose=False)
        self.assertListEqual(lines, ['hello world', 'how are you'])
        self.assertEqual(title, 'hey')

    def test_empty(self):
        html = ''''''
        with self.assertRaises(InvalidHtmlData):
            text_corpus_from_html(html, verbose=False)

    def test_no_title(self):
        html = '''
            <html>
                <body>
                    <div>hello world</div>
                </body>
            </html>
        '''
        with self.assertRaises(InvalidHtmlData):
            text_corpus_from_html(html, verbose=False)

    def test_no_html(self):
        html = '''oj029hg0hni1d1h9i nmm0n i0wn 0i'''
        with self.assertRaises(InvalidHtmlData):
            text_corpus_from_html(html, verbose=False)

if __name__ == '__main__':
    unittest.main()
