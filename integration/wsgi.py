# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os
import lzma

from flask import Flask
import orjson_ddb

app = Flask(__name__)

filename = os.path.join(os.path.dirname(__file__), "..", "data", "twitter.json.xz")

with lzma.open(filename, "r") as fileh:
    DATA = orjson_ddb.loads(fileh.read())


@app.route("/")
def root():
    data = orjson_ddb.dumps(DATA)
    return app.response_class(
        response=data, status=200, mimetype="application/json; charset=utf-8"
    )
