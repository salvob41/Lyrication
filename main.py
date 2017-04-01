import billboard
import datetime
import lyricwikia

date = datetime.datetime.now().strftime ("%Y-%m-%d")
chart = billboard.ChartData('hot-100', date=date)


last_hits = []
not_found = 0
for song in chart:

    artist = song.artist
    if "featuring" in song.artist.lower():
        artist = song.artist.lower().split("featuring")[0]
    artist = artist.replace("/", "&").strip()
    print artist, song.title
    try:
        song.lyrics = lyricwikia.get_lyrics(artist, song.title)
    except:
        not_found += 1
        print "not found %s by %s" % (artist, song.title)
    last_hits.append(song)

print not_found
# add to ES


