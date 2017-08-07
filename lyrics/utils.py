# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import wikipedia
import os
import re
import time
import unicodedata


def check_if_string_contains_list(list_of_words, stack):
    words_re = re.compile("|".join(list_of_words))
    return True if words_re.search(stack) else False


def get_wiki_hits():
    page_base = wikipedia.page("List of number-one hits (Italy)")
    # dal 52 in poi c'è il 2007
    # dal 4 c'è il 1959
    links = page_base.links[4:]
    year = 1959
    songs_by_year = dict()
    for link in links:
        print(year)
        try:
            url_page = wikipedia.page(link).url
        except:
            print(link)
            url_page = fix_wiki_url(link)

        page = requests.get(url_page)
        html = BeautifulSoup(page.text, "html.parser")
        tables = html.findChildren('table')
        my_table = tables[0]
        rows = my_table.findChildren(['tr'])
        list = []
        for row in rows:
            cells = row.findChildren('td')
            if len(cells) >= 3:
                [date, song, artist] = cells[:3]
                song = song.get_text()
                if "\"" in song:
                    print(song)
                    song = song.replace("\"", "")
                else:
                    continue
                list.append({"song": song, "artist": artist.get_text().replace("\"", ""),
                             "year": year})
        songs_by_year[year] = list
        year += 1

    return songs_by_year


BASE_URL = "https://api.genius.com"
HEADERS = {'Authorization': 'Bearer nLIT83G5LHNNX-BirfK7bZD1ciGdWscJPrVYmOaSEMxKQmGyDqQ5joeJJA69uB8_'}


def lyrics_from_song_api_path(song_api_path):
    song_url = BASE_URL + song_api_path
    data = {"text_format": "plain"}
    response = requests.get(song_url, data=data, headers=HEADERS)
    json = response.json()
    path = json["response"]["song"]["path"]
    song_info = json["response"]["song"]
    description = song_info["description"]["plain"]

    # gotta go regular html scraping... come on Genius
    page_url = "http://genius.com" + path
    page = requests.get(page_url)
    html = BeautifulSoup(page.text, "html.parser")
    # remove script tags that they put in the middle of the lyrics
    [h.extract() for h in html('script')]
    # at least Genius is nice and has a tag called 'lyrics'!
    lyrics = html.find("div", {"class": "lyrics"}).get_text()
    if not lyrics:
        raise Exception('Cannot download lyrics from GENIUS')
    return lyrics, description


def get_lyrics_from_genius(song_title, artist_name):
    search_url = BASE_URL + "/search"
    data = {'q': song_title[:song_title.find("(")] + " " + artist_name, "text_format": "plain"}
    response = requests.get(search_url, data=data, headers=HEADERS)
    json = response.json()
    song_info = None
    for hit in json["response"]["hits"]:
        if hit["result"]["primary_artist"]["name"].lower() in artist_name.lower() \
                or strip_accents(artist_name.lower()) in strip_accents(hit["result"]["primary_artist"]["name"].lower()):
            song_info = hit
            break
    if song_info:
        song_api_path = song_info["result"]["api_path"]
        return lyrics_from_song_api_path(song_api_path)
    else:
        raise Exception('{} by {} not found in GENIUS'.format(song_title, artist_name))


def rename_files(dir, new_dir):
    list_files = os.listdir(dir)
    for filename in list_files:
        filename_json = os.path.splitext(os.path.basename(filename))[0] + ".json"
        os.rename(os.path.join(dir, filename), os.path.join(new_dir, filename_json))


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
        "Ãš": "è"
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


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


def fix_wiki_url(link):
    base_wiki_url = "https://en.wikipedia.org/wiki/"
    return base_wiki_url+link
