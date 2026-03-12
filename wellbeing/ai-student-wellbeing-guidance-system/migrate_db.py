import os
import pymongo
from pymongo import MongoClient
import ssl

# Configuration
LOCAL_URI = "mongodb://localhost:27017/student_wellbeing"
# Get ATLAS_URI from environment variable or prompt user
ATLAS_URI = os.environ.get("MONGO_URI")

def migrate():
    print("--- MongoDB Local to Atlas Migration Tool ---")
    
    if not ATLAS_URI:
        print("ERROR: MONGO_URI environment variable not set.")
        print("Please set MONGO_URI to your Atlas connection string.")
        print("Example: set MONGO_URI=mongodb+srv://<user>:<pass>@cluster.mongodb.net/student_wellbeing")
        return

    print(f"Target Atlas URI: {ATLAS_URI.split('@')[-1]}") # Hide credentials
    
    confirm = input("Begin migration? (y/n): ")
    if confirm.lower() != 'y':
        print("Migration cancelled.")
        return

    try:
        # Connect to Local
        print("Connecting to Local MongoDB...")
        local_client = MongoClient(LOCAL_URI)
        local_db = local_client.get_database()
        
        # Connect to Atlas
        print("Connecting to Atlas MongoDB...")
        # Ensure SSL/TLS is handled (usually auto for mongodb+srv, but explicit valid certs might be needed)
        atlas_client = MongoClient(ATLAS_URI, tls=True, tlsAllowInvalidCertificates=True) 
        atlas_db = atlas_client.get_database() # Uses db name from URI
        
        # Collections to migrate
        collections = local_db.list_collection_names()
        print(f"Found collections: {collections}")
        
        for col_name in collections:
            print(f"Migrating collection: {col_name}...")
            local_col = local_db[col_name]
            atlas_col = atlas_db[col_name]
            
            docs = list(local_col.find())
            if not docs:
                print(f"  - No documents in {col_name}, skipping.")
                continue
                
            # Insert logic (using bulk write could be better, but simple loop is fine for small data)
            count = 0
            for doc in docs:
                try:
                    # Upsert based on _id to prevent duplicates
                    atlas_col.replace_one({"_id": doc["_id"]}, doc, upsert=True)
                    count += 1
                except Exception as e:
                    print(f"  - Error inserting doc {doc.get('_id')}: {e}")
            
            print(f"  - Migrated/Updated {count} documents.")
            
        print("\nMigration Complete!")
        
    except Exception as e:
        print(f"\nMIGRATION FAILED: {e}")

if __name__ == "__main__":
    migrate()
