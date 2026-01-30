import os
import asyncio
from mcp.server.fastmcp import FastMCP
from src.client import CheckvistClient
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

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

@mcp.tool()
async def search_list(query: str) -> str:
    """ Search for a checklist by name (fuzzy match). 
        Returns ID and Name of matching lists.
    """
    c = get_client()
    if not c.token:
        await c.authenticate()
        
    lists = await c.get_checklists()
    matches = [l for l in lists if query.lower() in l['name'].lower()]
    
    if not matches:
        return f"No lists found matching '{query}'"
        
    return "\n".join([f"- {l['name']} (ID: {l['id']})" for l in matches])

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
    try:
        c = get_client()
        if not c.token:
            await c.authenticate()
        task = await c.add_task(int(list_id), content, int(parent_id) if parent_id else None)
        return f"Task added: {task['content']} (ID: {task['id']})"
    except Exception as e:
        return f"Error adding task: {str(e)}"

@mcp.tool()
async def close_task(list_id: str, task_id: str) -> str:
    """ Close a task. """
    try:
        c = get_client()
        if not c.token:
            await c.authenticate()
        
        # Robust type coercion
        l_id = int(list_id)
        t_id = int(task_id)
        
        response = await c.close_task(l_id, t_id)
        
        # Handle potential list response (Bug Fix)
        if isinstance(response, list) and len(response) > 0:
            task = response[0]
        else:
            task = response
            
        return f"Task closed: {task.get('content', 'Unknown content')}"
    except Exception as e:
        return f"Error closing task: {str(e)}"

@mcp.tool()
async def create_list(name: str, public: bool = False) -> str:
    """ Create a new checklist. """
    try:
        c = get_client()
        if not c.token:
            await c.authenticate()
        
        checklist = await c.create_checklist(name, public)
        return f"Checklist created: {checklist['name']} (ID: {checklist['id']})"
    except Exception as e:
        return f"Error creating checklist: {str(e)}"

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
async def move_task_tool(list_id: str, task_id: str, target_list_id: str = None, target_parent_id: str = None) -> str:
    """ Move a task within a list or to a completely different list. 
        If target_list_id is provided, it performs a cross-list move.
    """
    c = get_client()
    if not c.token:
        await c.authenticate()
    
    if target_list_id and int(target_list_id) != int(list_id):
        moved = await c.move_task_to_list(int(list_id), int(task_id), int(target_list_id), int(target_parent_id) if target_parent_id else None)
        return f"Moved task {task_id} from list {list_id} to list {target_list_id}."
    else:
        # Same list move (reparenting)
        moved = await c.move_task(int(list_id), int(task_id), int(target_parent_id) if target_parent_id else None)
        return f"Moved task {task_id} under new parent {target_parent_id} in list {list_id}."

@mcp.tool()
async def import_tasks(list_id: str, content: str, parent_id: str = None) -> str:
    """ Bulk import tasks using a hierarchical text format (one per line, indent with 2 spaces). """
    c = get_client()
    if not c.token:
        await c.authenticate()
    tasks = await c.import_tasks(int(list_id), content, int(parent_id) if parent_id else None)
    return f"Tasks imported successfully. New items count: {len(tasks)}"

@mcp.tool()
async def add_note(list_id: str, task_id: str, note: str) -> str:
    """ Add a note (comment) to a specific task. """
    c = get_client()
    if not c.token:
        await c.authenticate()
    await c.add_note(int(list_id), int(task_id), note)
    return f"Note added to task {task_id} in list {list_id}."

@mcp.tool()
async def set_priority(list_id: str, task_id: str, priority: int) -> str:
    """ Set task priority (1-6, where 1 is highest/red). Use 0 for no priority. """
    c = get_client()
    if not c.token:
        await c.authenticate()
    await c.update_task(int(list_id), int(task_id), priority=priority)
    return f"Priority set to {priority} for task {task_id}."

@mcp.tool()
async def set_due_date(list_id: str, task_id: str, due: str) -> str:
    """ Set a due date using Checkvist's smart syntax (e.g., 'tomorrow', 'next mon', '2024-12-31'). """
    c = get_client()
    if not c.token:
        await c.authenticate()
    await c.update_task(int(list_id), int(task_id), due_date=due)
    return f"Due date set to '{due}' for task {task_id}."

@mcp.tool()
async def apply_template(template_list_id: str, target_list_id: str) -> str:
    """ Clone all tasks from a template list into a target list. """
    c = get_client()
    if not c.token:
        await c.authenticate()
    
    template_tasks = await c.get_tasks(int(template_list_id))
    # Filter for root tasks to avoid duplicating children twice 
    # (import_tasks handles hierarchy if we provide the right text)
    # For simplicity, we use import_tasks with the content of all tasks
    import_text = "\n".join([t['content'] for t in template_tasks if t.get('parent_id') is None])
    await c.import_tasks(int(target_list_id), import_text)
    return f"Template applied to list {target_list_id}."

@mcp.tool()
async def get_review_data(timeframe: str = "weekly") -> str:
    """ Get statistics about completed vs open tasks to help with periodic review. """
    c = get_client()
    if not c.token:
        await c.authenticate()
    
    checklists = await c.get_checklists()
    report = [f"Review Report ({timeframe}):"]
    
    for l in checklists[:5]: # Limit to first 5 for speed
        tasks = await c.get_tasks(l['id'])
        done = len([t for t in tasks if t.get('status', 0) == 1])
        open_ts = len([t for t in tasks if t.get('status', 0) == 0])
        report.append(f"- {l['name']}: {done} completed, {open_ts} open")
        
    return "\n".join(report)

@mcp.tool()
async def migrate_incomplete_tasks(source_list_id: str, target_list_id: str) -> str:
    """ Move all incomplete tasks from one list to another (e.g., closing a cycle/sprint). """
    c = get_client()
    if not c.token:
        await c.authenticate()
    
    tasks = await c.get_tasks(int(source_list_id))
    incomplete = [t for t in tasks if t.get('status', 0) == 0]
    
    for t in incomplete:
        await c.move_task_to_list(int(source_list_id), t['id'], int(target_list_id))
        
    return f"Migrated {len(incomplete)} incomplete tasks to list {target_list_id}."

@mcp.tool()
async def triage_inbox(inbox_name: str = "Inbox") -> str:
    """ Fetch tasks from the 'Inbox' list for triage. 
        Returns tasks with their IDs and current list IDs.
    """
    c = get_client()
    if not c.token:
        await c.authenticate()
        
    checklists = await c.get_checklists()
    inbox = next((l for l in checklists if inbox_name.lower() in l['name'].lower()), None)
    
    if not inbox:
        lists_available = ", ".join([l['name'] for l in checklists])
        return f"List named '{inbox_name}' not found. Available: {lists_available}"
        
    tasks = await c.get_tasks(inbox['id'])
    # Filter only open tasks
    open_tasks = [t for t in tasks if t.get('status', 0) == 0]
    
    if not open_tasks:
        return f"Inbox ({inbox['name']}) is empty! Good job."
        
    return f"Tasks in {inbox['name']} (ID: {inbox['id']}):\n" + \
           "\n".join([f"- {t['content']} (ID: {t['id']})" for t in open_tasks])

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
