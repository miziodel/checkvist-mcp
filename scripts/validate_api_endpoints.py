import os
import sys
import httpx
import asyncio
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.client import CheckvistClient
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

async def validate_endpoints():
    username = os.getenv("CHECKVIST_USERNAME")
    api_key = os.getenv("CHECKVIST_API_KEY")
    
    if not username or not api_key:
        print("❌ Missing credentials. Check .env file.")
        return

    print(f"🔄 Authenticating as {username}...")
    client = CheckvistClient(username, api_key)
    if not await client.authenticate():
        print("❌ Authentication failed!")
        await client.close()
        return

    print("✅ Authenticated. Token received.\n")
    
    endpoints = [
        ("GET", "/checklists.json", "List Checklists"),
        ("GET", "/checklists/due.json", "Due Tasks (Undocumented)"),
    ]
    
    # We need a list ID for further tests
    lists = await client.get_checklists()
    if not lists:
        print("⚠️ No checklists found. Skipping list-dependent tests.")
    else:
        test_list_id = lists[0]['id']
        print(f"ℹ️ Using list '{lists[0]['name']}' (ID: {test_list_id}) for context tests.\n")
        
        endpoints.extend([
            ("GET", f"/checklists/{test_list_id}/tasks.json?with_notes=true&limit=1", "List Tasks"),
        ])

    print(f"{'METHOD':<8} {'ENDPOINT':<50} {'STATUS':<10} {'RESULT'}")
    print("-" * 80)

    success_count = 0
    for method, url, name in endpoints:
        try:
            full_url = url
            # We use the internal client's http client which already has the base url
            if method == "GET":
                response = await client.client.get(url)
            elif method == "POST":
                 # Just a dry run or safe ping if possible, avoiding state change here for now
                 # For validation script we mostly check reads.
                 continue 
            
            status = response.status_code
            status_icon = "✅" if status == 200 else "❌"
            if status == 200: success_count += 1
            
            print(f"{method:<8} {url[:48]:<50} {status:<10} {status_icon} {name}")
            
        except Exception as e:
            print(f"{method:<8} {url[:48]:<50} {'ERR':<10} ❌ {name} - {str(e)}")

    print("-" * 80)
    print(f"Done. Verified {success_count}/{len(endpoints)} safe read endpoints.")
    print("For full regression including Writes, run `pytest tests/test_regressions.py`.")
    
    await client.close()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(validate_endpoints())
