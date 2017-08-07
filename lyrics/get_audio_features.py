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

    parser = argparse.ArgumentParser(description='')
    parser.add_argument("-o", "--output", help="Output existing directory, will contain the JSON files", required=True)
    parser.add_argument("input", help="input folder with JSON with lyrics to extend with audio features")

    args = parser.parse_args()

    list_files = os.listdir(args.input)
    LYRICS_DIR = args.output
    client_credentials_manager = SpotifyClientCredentials()

    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    for filename in list_files:
        with open(os.path.join(args.input, filename)) as f:
            try:
                data = json.load(f)
            except ValueError:
                # if it isn't a correct json, print to log and go on
                logger.error("Error decoding json: {}".format(filename))
                continue

        artist = data["artist"].split("&")[0]
        track_name = data["song"]
        search_query = artist + " " + track_name
        results = sp.search(q=search_query, limit=5)
        track_ids = []
        batch_songs = dict()
        audio_features = dict()
        spotify_info = dict()
        for i, t in enumerate(results['tracks']['items']):
            spotify_info = dict()
            track_id = t["id"]
            track_name = t["name"]
            if "karaoke" in t["name"].lower():
                logger.info("Skip karaoke version of this song {} by {}".format(track_name, artist))
                continue
            album_id = t["album"]["id"]
            artist_id = t["artists"][0]["id"]
            print(' ', i, data["artist"], t['name'], "...\t")
            try:
                features = sp.audio_features(track_id)
                track_info = sp.track(track_id)
                album_info = sp.album(album_id)
                artist_info = sp.artist(artist_id)
                spotify_info["artist"] = album_info
                spotify_info["album"] = artist_info
                spotify_info["track"] = track_info
                audio_features = features[0]
                break
            except:
                logger.error(
                    "something didn't work with the song {} by {} (id: {})".format(track_name, artist, track_id))

            time.sleep(5)

        final_json = {"info_song": data, "audio_features": audio_features, "spotify_info": spotify_info}
        if not spotify_info:
            logger.warning("Not found spotify data for {}".format(filename))

        with open(
                os.path.join(args.output, artist.replace(' ', '_') + "+" + track_name.replace("/","").replace(' ', '_') + ".json"),
                "w") as f:
            json.dump(final_json, f)
