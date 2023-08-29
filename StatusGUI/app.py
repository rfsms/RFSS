from flask import Flask, jsonify, render_template
from flask_cors import CORS
from flask_compress import Compress
from pymongo import MongoClient
from bson.json_util import dumps
import json

app = Flask(__name__)
CORS(app)  # Enable CORS
Compress(app)  # Enable Compression

# MongoDB Connection
client = MongoClient('localhost', 27017)
db = client['status_db']
collection = db['status_collection']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    # Fetch data from MongoDB
    data = fetch_data_from_mongo()
    return jsonify(data)

def fetch_data_from_mongo():
    cursor = collection.find()
    return json.loads(dumps(cursor))

if __name__ == '__main__':
    app.run(debug=False, port=3000)
