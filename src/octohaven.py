#!/usr/bin/env python

from flask import Flask

app = Flask("octohaven")

@app.route("/")
def hello():
    return "Hello World!"

def run(host=None, port=None):
    host = str(host)
    port = int(port)
    app.run(debug=True, host=host, port=port)
