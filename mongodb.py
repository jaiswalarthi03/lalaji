from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

MONGO_URI = "mongodb+srv://root:root@preventive.i7rpqdb.mongodb.net/?retryWrites=true&w=majority&appName=preventive"
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
db = client['inventory_master'] 