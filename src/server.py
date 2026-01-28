import os
import asyncio
from mcp.server.fastmcp import FastMCP
from client import CheckvistClient
from dotenv import load_dotenv

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("Checkvist")

# Initialize client (will be authenticated on the first request or in a lifecycle hook)
client = None

def get_client():
    global client
    if client is None:
        username = os.getenv("CHECKVIST_USERNAME")
        api_key = os.getenv("CHECKVIST_API_KEY")
        if not username or not api_key:
            raise ValueError("CHECKVIST_USERNAME and CHECKVIST_API_KEY environment variables are required")
        client = CheckvistClient(username, api_key)
    return client

@mcp.resource("checkvist://lists")
async def list_checklists() -> str:
    """ Get all checklists as a formatted string. """
    c = get_client()
    if not c.token:
        await c.authenticate()
    lists = await c.get_checklists()
    return "\n".join([f"- {l['name']} (ID: {l['id']})" for l in lists])

@mcp.resource("checkvist://list/{list_id}")
async def get_list_content(list_id: str) -> str:
    """ Get the content of a specific checklist. """
    c = get_client()
    if not c.token:
        await c.authenticate()
    tasks = await c.get_tasks(int(list_id))
    return "\n".join([f"- [{'x' if t.get('status', 0) == 1 else ' '}] {t.get('content')}" for t in tasks])

@mcp.tool()
async def add_task(list_id: str, content: str, parent_id: str = None) -> str:
    """ Add a new task to a checklist. """
    c = get_client()
    if not c.token:
        await c.authenticate()
    task = await c.add_task(int(list_id), content, int(parent_id) if parent_id else None)
    return f"Task added: {task['content']} (ID: {task['id']})"

@mcp.tool()
async def close_task(list_id: str, task_id: str) -> str:
    """ Close a task. """
    c = get_client()
    if not c.token:
        await c.authenticate()
    task = await c.close_task(int(list_id), int(task_id))
    return f"Task closed: {task['content']}"

@mcp.tool()
async def search_tasks(query: str) -> str:
    """ Search for tasks across all lists. """
    c = get_client()
    if not c.token:
        await c.authenticate()
    results = await c.search_tasks(query)
    if not results:
        return "No tasks found matching the query."
    return "\n".join([f"- {r['content']} [List: {r['list_name']} (ID: {r['list_id']}), Task ID: {r['id']}]" for r in results])

if __name__ == "__main__":
    mcp.run()
