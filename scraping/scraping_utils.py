#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import time
import requests
from bs4 import BeautifulSoup
import os

def save_page(html_url):
    parser = etree.HTMLParser()
    tree = etree.parse(html_url, parser)
    if tree.getroot() is None:
        return None
    with open('pretty.html', 'wb') as file:
        file.write(str)

def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f


def get_lyrics(page):
    html = BeautifulSoup(open(page), "html.parser")
    # remove script tags that they put in the middle of the lyrics
    [h.extract() for h in html('a')]
    [h.extract() for h in html('strong')]
    # at least Genius is nice and has a tag called 'lyrics'!
    lyrics_p = html.find_all("p")

    lyrics = ""
    # we need this to skip the first line
    for p in lyrics_p:
        if "Il testo contenuto in questa pagina" in p.text:
            break
        if "contenuto nei seguenti album" not in p.text and "tutti possono collaborare inserendo testi" not in p.text:
            lyrics += p.get_text(separator=' ')

    if not lyrics:
        raise Exception('Cannot download lyrics from this page {}'.format(page))
    return lyrics


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), 6):
        yield l[i:i + n]


def xstr(s):
    return '' if s is None else str(s.encode('utf-8').strip())


def substitute(s):
    d = {"à": "a", "è": "e", "é": "e", "ì": "i", "ò": "o", "ù": "u"}
    pattern = re.compile('|'.join(d.keys()))
    result = pattern.sub(lambda x: d[x.group()], s)
    return result


def substitute_ascii(s):
    d = {
        "Ã": "à",
        "Ã¡": "á",
        "Ã¨": "è",
        "Ã©": "é",
        "Ã¬": "ì",
        "Ã­": "í",
        "Ã²": "ò",
        "Ã³": "ó",
        "Ã¹": "ù",
        "Ãº": "ú",
        "Ã\x88": "È",
        "Ãš": "è",
        "â": "'"
    }
    '''
    http://string-functions.com/encodingtable.aspx?encoding=65001
    https://r12a.github.io/apps/conversion/
    
    '''
    pattern = re.compile('|'.join(d.keys()))
    result = pattern.sub(lambda x: d[x.group()], s)
    return result


def minute_passed(oldepoch, n=1):
    return time.time() - oldepoch >= 60 * n
