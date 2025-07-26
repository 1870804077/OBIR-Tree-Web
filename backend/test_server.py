#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/test', methods=['GET'])
def test():
    return {'message': 'Server is running!'}

if __name__ == '__main__':
    print("Starting test server on port 8080...")
    app.run(host='127.0.0.1', port=8080, debug=True) 