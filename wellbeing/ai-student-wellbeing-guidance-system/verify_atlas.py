import os
from pymongo import MongoClient
from dotenv import load_dotenv
import ssl

# Load environment variables
load_dotenv()

def verify_connection():
    uri = os.environ.get("MONGO_URI")
    print(f"Testing Connection to: {uri.split('@')[-1] if uri else 'None'}")
    
    if not uri:
        print("❌ Error: MONGO_URI not found in environment variables.")
        return

    try:
        # Create a new client and connect to the server
        client = MongoClient(uri, tls=True, tlsAllowInvalidCertificates=True)
        
        # Send a ping to confirm a successful connection
        client.admin.command('ping')
        print("✅ Pinged your deployment. You successfully connected to MongoDB Atlas!")
        
        # List databases
        dbs = client.list_database_names()
        print(f"Databases found: {dbs}")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    verify_connection()
