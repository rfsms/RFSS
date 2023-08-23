from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['status_db']
collection = db['status_collection']

# Retrieve all documents in the collection
documents = collection.find()

# Print the documents
for document in documents:
    print(document)
