from pymongo import MongoClient
import datetime

try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["student_wellbeing"]
    
    print("Collections:", db.list_collection_names())
    
    if "diary_entries" in db.list_collection_names():
        count = db.diary_entries.count_documents({})
        print(f"Count of diary_entries: {count}")
        for doc in db.diary_entries.find().sort("created_at", -1).limit(5):
            print(f"Entry: {doc}")
    else:
        print("Collection 'diary_entries' does not exist.")

    # Check users too
    user_count = db.users.count_documents({})
    print(f"User count: {user_count}")

except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
