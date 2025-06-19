from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT, GEOSPHERE
from datetime import datetime
from config import MONGODB_URI, DB_NAME, COLLECTIONS

def setup_database():
    """Set up all collections and indexes in MongoDB Atlas"""
    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]
    
    print("\n=== Setting up MongoDB Collections and Indexes ===\n")
    print(f"Database: {DB_NAME}")
    print(f"Collections: {', '.join(COLLECTIONS.values())}\n")
    
    try:
        # 1. Users Collection
        print("1. Setting up Users Collection...")
        users = db[COLLECTIONS['users']]
        users.create_index([("email", ASCENDING)], unique=True)
        users.create_index([("phone", ASCENDING)], unique=True)
        users.create_index([("family_id", ASCENDING)])
        users.create_index([("location", GEOSPHERE)])
        print("✓ Users collection setup complete")
        
        # 2. Families Collection
        print("\n2. Setting up Families Collection...")
        families = db[COLLECTIONS['families']]
        families.create_index([("name", TEXT)])
        families.create_index([("creator_id", ASCENDING)])
        families.create_index([("members", ASCENDING)])
        print("✓ Families collection setup complete")
        
        # 3. Events Collection
        print("\n3. Setting up Events Collection...")
        events = db[COLLECTIONS['events']]
        events.create_index([("family_id", ASCENDING)])
        events.create_index([("created_by", ASCENDING)])
        events.create_index([("start_time", ASCENDING)])
        events.create_index([("end_time", ASCENDING)])
        events.create_index([("type", ASCENDING)])
        events.create_index([("priority", ASCENDING)])
        events.create_index([("status", ASCENDING)])
        events.create_index([("participants", ASCENDING)])
        print("✓ Events collection setup complete")
        
        # 4. SOS Alerts Collection
        print("\n4. Setting up SOS Alerts Collection...")
        sos_alerts = db[COLLECTIONS['sos_alerts']]
        sos_alerts.create_index([("user_id", ASCENDING)])
        sos_alerts.create_index([("family_id", ASCENDING)])
        sos_alerts.create_index([("status", ASCENDING)])
        sos_alerts.create_index([("created_at", DESCENDING)])
        sos_alerts.create_index([("location", GEOSPHERE)])
        sos_alerts.create_index([("acknowledged_by", ASCENDING)])
        print("✓ SOS Alerts collection setup complete")
        
        # 5. Fitness Data Collection
        print("\n5. Setting up Fitness Data Collection...")
        fitness_data = db[COLLECTIONS['fitness_data']]
        fitness_data.create_index([("user_id", ASCENDING)])
        fitness_data.create_index([("date", DESCENDING)])
        fitness_data.create_index([("type", ASCENDING)])
        print("✓ Fitness Data collection setup complete")
        
        
        # Print collection statistics
        print("\nCollection Statistics:")
        for collection_name in COLLECTIONS.values():
            stats = db.command("collstats", collection_name)
            print(f"\n{collection_name}:")
            print(f"  Documents: {stats['count']}")
            print(f"  Size: {stats['size'] / 1024:.2f} KB")
            print(f"  Indexes: {len(stats['indexSizes'])}")
        
    except Exception as e:
        print(f"\nError during setup: {str(e)}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    setup_database() 
