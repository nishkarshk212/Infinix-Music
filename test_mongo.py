import asyncio
from pymongo import AsyncMongoClient
from dotenv import load_dotenv
import os
import certifi

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

async def test_connection():
    try:
        print("Connecting to MongoDB...")
        client = AsyncMongoClient(
            MONGO_URL, 
            serverSelectionTimeoutMS=30000,
            tlsCAFile=certifi.where()
        )
        await client.admin.command("ping")
        print("✅ Connection successful!")
        await client.close()
    except Exception as e:
        print(f"❌ Connection failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())
