import os
import sys
import asyncio

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from src.client import CheckvistClient

async def check():
    load_dotenv()
    username = os.getenv("CHECKVIST_USERNAME")
    api_key = os.getenv("CHECKVIST_API_KEY")
    
    if not username or not api_key:
        print("ERROR: CHECKVIST_USERNAME or CHECKVIST_API_KEY not found in environment.")
        return

    print(f"Connecting as {username}...")
    client = CheckvistClient(username, api_key)
    
    try:
        await client.authenticate()
        print("Authentication successful!")
        
        checklists = await client.get_checklists()
        print(f"\nFound {len(checklists)} checklists:")
        for l in checklists:
            print(f"- {l['name']} (ID: {l['id']})")
            
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(check())
