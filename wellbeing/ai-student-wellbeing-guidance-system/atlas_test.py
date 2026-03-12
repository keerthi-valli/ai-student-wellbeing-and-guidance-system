from pymongo import MongoClient

uri = "mongodb+srv://<USERNAME>:<PASSWORD>@cluster0.fbjsciw.mongodb.net/student_wellbeing?retryWrites=true&w=majority"

client = MongoClient(uri, serverSelectionTimeoutMS=5000)

print(client.server_info())
