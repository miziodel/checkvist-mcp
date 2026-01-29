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

@mcp.tool()
async def move_task_tool(list_id: str, task_id: str, new_parent_id: str) -> str:
    """ Move a task to a new parent task within the same list. 
        Useful for organizing (Triage).
    """
    c = get_client()
    if not c.token:
        await c.authenticate()
    
    # Optional: Get task context first to confirm safe move? 
    # For now, just move.
    moved = await c.move_task(int(list_id), int(task_id), int(new_parent_id))
    return f"Moved task {task_id} to new parent {new_parent_id}."

@mcp.tool()
async def triage_inbox(inbox_name: str = "Inbox") -> str:
    """ Fetch tasks from the 'Inbox' list for triage. 
        Returns tasks with their IDs for the agent to decide where to move them.
    """
    c = get_client()
    if not c.token:
        await c.authenticate()
        
    checklists = await c.get_checklists()
    inbox = next((l for l in checklists if inbox_name.lower() in l['name'].lower()), None)
    
    if not inbox:
        return f"List named '{inbox_name}' not found."
        
    tasks = await c.get_tasks(inbox['id'])
    # Filter only open tasks
    open_tasks = [t for t in tasks if t.get('status', 0) == 0]
    
    if not open_tasks:
        return "Inbox is empty! Good job."
        
    return "\n".join([f"- {t['content']} (ID: {t['id']}, ListID: {inbox['id']})" for t in open_tasks])

@mcp.tool()
async def get_tree(list_id: str, depth: int = 1) -> str:
    """ Get the task tree for a list, respecting a depth limit to save tokens.
        depth=1: Top level tasks only.
        depth=2: Top level + direct children.
    """
    c = get_client()
    if not c.token:
        await c.authenticate()
        
    tasks = await c.get_tasks(int(list_id))
    
    # Build Tree
    # 1. Map ID -> Task
    task_map = {t['id']: {'data': t, 'children': []} for t in tasks}
    roots = []
    
    for t in tasks:
        pid = t.get('parent_id')
        if pid and pid in task_map:
            task_map[pid]['children'].append(task_map[t['id']])
        else:
            roots.append(task_map[t['id']])
            
    # Traverse with depth limit
    def print_node(node, current_depth):
        if current_depth > depth:
            return ""
        
        task = node['data']
        status = 'x' if task.get('status', 0) == 1 else ' '
        # Indent based on logical depth (not purely string based)
        # But here we just output flat list with visual indentation for the LLM
        indent = "  " * (current_depth - 1)
        line = f"{indent}- [{status}] {task['content']} (ID: {task['id']})"
        
        children_output = ""
        for child in node['children']:
            children_output += "\n" + print_node(child, current_depth + 1)
            
        return line + children_output

    output = []
    for root in roots:
        res = print_node(root, 1)
        if res.strip():
            output.append(res)
            
    return "\n".join(output)

@mcp.tool()
async def resurface_ideas() -> str:
    """ Randomly pick open tasks from old lists to resurface ideas. """
    import random
    c = get_client()
    if not c.token:
        await c.authenticate()
        
    checklists = await c.get_checklists()
    if not checklists:
        return "No lists found."
        
    # Pick 3 random lists to check
    random.shuffle(checklists)
    candidates = []
    
    for l in checklists[:3]:
        tasks = await c.get_tasks(l['id'])
        # Open tasks only
        open_tasks = [t for t in tasks if t.get('status', 0) == 0]
        if open_tasks:
            t = random.choice(open_tasks)
            candidates.append(f"- {t['content']} (List: {l['name']}, ID: {t['id']})")
            
    if not candidates:
        return "No ideas found to resurface."
        
    return "Here are some forgotten tasks/ideas:\n" + "\n".join(candidates)

if __name__ == "__main__":
    mcp.run()
