# -*- coding: utf-8 -*-
from __future__ import print_function  # (at top of module)
import sys
import codecs
import argparse
import csv
from spotipy.oauth2 import SpotifyClientCredentials
import os
import json
import spotipy
import time
import sys
import logging
import lyricwikia
import pprint
import utils

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
log_filename = os.path.join(ROOT_DIR, "log/" + os.path.splitext(os.path.basename(__file__))[0] + ".log")
print("Write the %s log file" % log_filename)
logger = logging.getLogger(__name__)
hdlr_1 = logging.FileHandler(log_filename)
hdlr_1.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(hdlr_1)
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    # sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer)

    parser = argparse.ArgumentParser(description='')
    parser.add_argument("-o", "--output", help="Output existing directory, will contain the JSON files", required=True)
    parser.add_argument("-l", "--label", help="label", required=True)
    parser.add_argument("-n", "--num_tracks", help="num_tracks", default=1)
    parser.add_argument("-k", "--artist_index", help="index of artist in CSV", default=0)
    parser.add_argument("-s", "--song_index", help="index of song in CSV", default=1)
    parser.add_argument("-y", "--starting_year", help="year of the song")
    parser.add_argument("-x", "--year_index", help="year of the song", default=-1)
    parser.add_argument("-i", "--input_csv", help="CSV file")
    parser.add_argument("-j", "--input_json", help="JSON file")
    parser.add_argument("-a", "--just_artists", help="if you want to get the first n tracks", default=False)
    parser.add_argument("-b", "--album", help="If you put album", default=False, required=True)
    parser.add_argument("-p", "--album_index", help="where to find album in CSV file", default=1)

    args = parser.parse_args()

    LYRICS_DIR = args.output
    LABEL = args.label
    ARTIST_INDEX = int(args.artist_index)
    SONG_INDEX = int(args.song_index)
    starting_year = args.starting_year
    client_credentials_manager = SpotifyClientCredentials()

    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    songs_to_check = dict()
    artists = dict()
    current_year = 0
    album = ""
    song = ""
    # create the dictionary for scraping
    if args.input_csv:
        with open(args.input_csv) as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if len(row) == 1:
                    current_year = row[0]
                    continue
                if args.album:
                    album = row[args.album_index]
                else:
                    song = row[SONG_INDEX]
                info_song = {}
                artist = row[ARTIST_INDEX]
                year = int(row[args.year_index])
                if not year in songs_to_check:
                    songs_to_check[year] = [{"song": song, "artist": artist, "album": album}]
                else:
                    songs_to_check[year].append({"song": song, "artist": artist, "album": album})
        artists = songs_to_check

    if args.input_json:
        with open(args.input_json) as f:
            try:
                data = json.load(f)
                artists = data
            except ValueError:
                # if it isn't a correct json, print to log and go on
                exit()

    logger.info(songs_to_check)

    limit_tracks = args.num_tracks

    logger.info("Starting getting info and lyrics from this list of artists {} ".format(artists))

    for year in artists:
        # if json:
        '''
        for song_info in artists[year]["artist"]:
            artist = song_info
        '''
        # if csv:
        '''
        for song_info in artists[year]:
            artist = song_info["artist"]
        '''
        for song_info in artists[year]:
            songs = dict()
            artist = song_info["artist"]
            song = ""
            album = ""
            year_query = ""
            if not args.just_artists:
                song = song_info["song"]
            if args.album:
                album = song_info["album"]
            if starting_year:
                year_query = " year:{}-{}".format(starting_year, year)
            search_query = "{} {} {} {}".format(artist, song, album, year_query)
            print(search_query)
            results = sp.search(q=search_query, limit=limit_tracks, type="album", market="it")
            track_ids = []
            batch_songs = dict()
            print("{} in {}".format(artist, year))
            if len(results['albums']['items']) == 0:
                logger.error("No results found for {}".format(search_query))
                continue
            album_id_to_get = results['albums']['items'][0]
            album_id = album_id_to_get["id"]
            results = sp.album_tracks(album_id)
            for i, t in enumerate(results["items"]):
                spotify_info = dict()
                info_song = dict()
                track_id = t["id"]
                track_name = t["name"]
                track_name = t["name"]
                song_name = song if song else track_name
                artist_id = t["artists"][0]["id"]
                if "karaoke" in t["name"].lower():
                    logger.info("Skip karaoke version of this song {} by {}".format(track_name, artist))
                    continue
                print(' ', i, t['name'], "...\t", end="")
                lyrics = None
                description = ""

                try:
                    [lyrics, description] = utils.get_lyrics_from_genius(song_name, artist)
                    print("GENIUS found")
                except Exception as err:
                    logger.error("{} by {}, GENIUS lyrics not found".format(track_name, artist))
                    print("GENIUS LYRICS not found!", "\t", end=" ")

                if not lyrics:
                    try:
                        lyrics = lyricwikia.get_lyrics(artist, t['name'])
                        print("LYRICWIKIA found")

                    except Exception as err:
                        logger.warning("{} by {}, LYRIWIKIA lyrics not found".format(track_name, artist))
                        print("Lyrics not found")
                        continue

                try:
                    features = sp.audio_features(track_id)
                    track_info = sp.track(track_id)
                    album_info = sp.album(album_id)
                    artist_info = sp.artist(artist_id)

                    spotify_info["artist"] = album_info
                    spotify_info["album"] = artist_info
                    spotify_info["track"] = track_info
                    audio_features = features[0]
                except:
                    logger.error(
                        "GET SPOTIFY INFO - something didn't work with the song {} by {} (id: {})\n {}".format(
                            track_name, artist, track_id, artist_info))

                info_song["song"] = track_name
                info_song["artist"] = artist
                info_song["lyrics"] = lyrics
                info_song["label"] = LABEL
                info_song["year"] = year
                info_song["description"] = description
                batch_songs[track_id] = {"info_song": info_song, "spotify_info": spotify_info}
                track_ids.append(track_id)

            features = sp.audio_features(track_ids)
            for i, track_id in enumerate(track_ids):
                batch_songs[track_id]["audio_features"] = features[i]

            for song_id in batch_songs:
                track_name = batch_songs[song_id]["info_song"]["song"].replace("/", " ")
                with open(os.path.join(LYRICS_DIR,
                                       artist.replace(' ', '_') + "+" + track_name.replace(' ', '_') + ".json"),
                          "w") as f:
                    a = batch_songs[song_id]
                    json.dump(a, f)
                    # print(lyrics)
                    # time.sleep(5)
