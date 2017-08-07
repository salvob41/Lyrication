import csv
import re
import time
import os
import json
import logging
import urllib.request

# This page will be Top Settimanali Single: Raccoglie le classifiche settimanali, a partire dal 1959 sino ai nostri giorni.
# Questa sezione elenca, settimana per settimana, la classifica dei dischi singoli (78 o 45 giri, CD, download e streaming in base alla tecnica dell'epoca).

FILE_PATH = "sanremo_ranking_mod.csv"
LYRICS_BASE_URL = "http://wikitesti.com/?s="
LYRICS_PATH = "lyrics"
SEARCH = "sanremo"
checkpoint = time.time()
PAGES_DIR = "broken"

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
log_filename = "log/" + os.path.splitext(os.path.basename(__file__))[0] + ".log"
print("Write the %s log file" % log_filename)
logger = logging.getLogger(__name__)
hdlr_1 = logging.FileHandler(log_filename)
hdlr_1.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(hdlr_1)
logger.setLevel(logging.INFO)


urllib.request.urlretrieve()