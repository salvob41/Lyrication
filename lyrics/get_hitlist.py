import utils
import json
import os

data = utils.get_wiki_hits()
with open("hitlist.json", "w") as f:
    json.dump(data, f)
