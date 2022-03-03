from pymongo import MongoClient
import certifi

# cluster = MongoClient('mongodb+srv://Khaled:Khaled123@cluster0.bdpuf.mongodb.net/mydb?retryWrites=true&w=majority')
cluster = MongoClient(host='localhost', port=27017)
db = cluster['mydb']
users = db['user']

users.insert_one({'name':'Khaledtest'})

print(users.find_one({'name':'Khaledtest'}))