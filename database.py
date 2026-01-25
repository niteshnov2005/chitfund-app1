from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_DB = os.getenv('MONGO_DB', 'chitfund_db')

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

# Collections
users_collection = db['users']
members_collection = db['members']
payments_collection = db['payments']
auctions_collection = db['auctions']
sheets_collection = db['sheets']

def init_db():
    """Initialize database with indexes and default admin user"""
    # Create indexes
    users_collection.create_index('username', unique=True)
    members_collection.create_index('name')
    members_collection.create_index('user_id')
    payments_collection.create_index('member_id')
    payments_collection.create_index('sheet_name')
    auctions_collection.create_index('date')
    
    # Create default admin user if not exists
    import bcrypt
    if users_collection.count_documents({'role': 'admin'}) == 0:
        default_password = os.getenv('DEFAULT_ADMIN_PASSWORD', 'changeme')
        hashed_pw = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt())
        users_collection.insert_one({
            'username': 'admin',
            'password': hashed_pw,
            'role': 'admin',
            'name': 'Administrator',
            'created_at': datetime.utcnow()
        })
        print("Default admin user created")

def get_db():
    """Get database instance"""
    return db