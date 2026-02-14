import os
import asyncio
import sys
import re
import time
import json
from pathlib import Path

# Add project root to path (one level up from tests/)
sys.path.append(str(Path(__file__).parent.parent))

from src.server import (
    get_client, get_service, create_list, add_task, 
    import_tasks, archive_task, apply_template, get_tree,
    search_tasks, move_task_tool, close_task, reopen_task,
    add_note, rename_list
)

async def run_complex_live_tests():
    print("🚀 Starting COMPLEX Live Verification...")
    
    # -- TEST 1: Deep Hierarchy & Smart Syntax --
    test_list_name = f"MCP_COMPLEX_{int(time.time())}"
    print(f"\n1. Creating complex list: {test_list_name}")
    list_res = json.loads(await create_list(test_list_name))
    list_id = str(list_res["data"]["id"])
    
    print("Importing 5-level hierarchy with Smart Syntax...")
    complex_content = (
        "Level 1 Root !1 #urgent\n"
        "  Level 2 Child ^tomorrow #work\n"
        "    Level 3 Grandchild @meeting\n"
        "      Level 4 Great-Grandchild #focus\n"
        "        Level 5 Deepest Leaf #done\n"
        "Flat Task #simple"
    )
    await import_tasks(list_id, complex_content)
    
    # Verify creation
    tree_res = json.loads(await get_tree(list_id, depth=5))
    tree_v1 = tree_res["data"]
    print("\nInitial Complex Tree:")
    print(tree_v1)
    
    # -- TEST 2: Recursive Archiving with Metadata --
    root_id_match = re.search(r"Level 1 Root .*?\(ID: (\d+)\)", tree_v1)
    if root_id_match:
        root_id = root_id_match.group(1)
        print(f"\n2. Archiving recursive root ID: {root_id}")
        await archive_task(list_id, root_id)
        print("Waiting 1.5s for archive propagation...")
        await asyncio.sleep(1.5)
        
        # Check tree - everything under root should be hidden
        tree_after_res = json.loads(await get_tree(list_id, depth=5))
        tree_after = tree_after_res["data"]
        if "Level 1 Root" not in tree_after and "Level 5 Deepest" not in tree_after:
            print("✅ Success: Deep hierarchy recursively archived.")
        else:
            print("❌ Failure: Deep tasks still visible after archive.")

    # -- TEST 3: Template Application with Metadata & Complexity --
    dest_list_name = f"MCP_TEMPLATE_DEST_{int(time.time())}"
    print(f"\n3. Creating destination list: {dest_list_name}")
    dest_res = json.loads(await create_list(dest_list_name))
    dest_id = str(dest_res["data"]["id"])
    
    print(f"Applying complex template from {list_id} to {dest_id}...")
    await apply_template(list_id, dest_id, confirmed=True)
    
    dest_tree_res = json.loads(await get_tree(dest_id, depth=5))
    dest_tree = dest_tree_res["data"]
    print("\nDestination Tree (after template - should be filtered of archived):")
    print(dest_tree)
    
    if "Flat Task #simple" in dest_tree and "Level 1 Root" not in dest_tree:
        print("✅ Success: Template applied with filtering of archived tasks.")
    else:
        print("❌ Failure: Template still contains archived tasks or missing others.")

    # -- TEST 4: Metadata Restoration (New List, Clean Template) --
    print("\n4. Testing Metadata Restoration in Template...")
    src_list_2 = f"MCP_SRC_2_{int(time.time())}"
    src_res_2 = json.loads(await create_list(src_list_2))
    src_id_2 = str(src_res_2["data"]["id"])
    await import_tasks(src_id_2, "Source Task !2 #meta ^2026-12-31\n  Nested !3 #sub")
    
    dest_list_2 = f"MCP_DEST_2_{int(time.time())}"
    dest_res_2 = json.loads(await create_list(dest_list_2))
    dest_id_2 = str(dest_res_2["data"]["id"])
    
    await apply_template(src_id_2, dest_id_2, confirmed=True)
    dest_tree_2_res = json.loads(await get_tree(dest_id_2, depth=2))
    dest_tree_2 = dest_tree_2_res["data"]
    print("Restore Tree:")
    print(dest_tree_2)
    
    if "!2" in dest_tree_2 and "#meta" in dest_tree_2 and "!3" in dest_tree_2 and "#sub" in dest_tree_2:
        print("✅ Success: Metadata (priorities/tags) restored in template.")
    else:
        print("❌ Failure: Metadata lost in template application.")

    # -- TEST 5: Search Verification with Breadcrumbs --
    # -- TEST 5: Search Verification --
    # We use a very unique string to make search faster or easier to verify
    unique_search_term = f"Flat Task {int(time.time())}"
    print(f"\n5. Verifying search with unique term: {unique_search_term}")
    await add_task(list_id, unique_search_term)
    
    search_res_str = await search_tasks(unique_search_term)
    search_res = json.loads(search_res_str)
    print("Search Result:")
    print(search_res)
    if search_res["success"] and len(search_res["data"]) > 0:
        print("✅ Success: Search results found the unique task.")
    else:
        print("❌ Failure: Search failed to find the unique task.")

    # -- TEST 6: Reopen Task Logic --
    print("\n6. Testing reopen_task logic...")
    add_data = json.loads(await add_task(list_id, "Task to Close and Reopen"))
    print(f"Add task result: {add_data}")
    target_id = str(add_data["data"]["id"])
    print(f"Closing task {target_id}...")
    await close_task(list_id, target_id)
    print(f"Reopening task {target_id}...")
    reopen_res_str = await reopen_task(list_id, target_id)
    reopen_res = json.loads(reopen_res_str)
    print(f"Reopen result: {reopen_res}")
    if reopen_res["success"]:
        print("✅ Success: Task reopened without error.")
    else:
        print(f"❌ Failure: Unexpected response from reopen_task: {reopen_res}")

    # -- TEST 7: Regression Check (Bug #0 & #1 Verification) --
    print("\n7. Testing Regression Scenarios (ID Mismatch & 403 checks)...")
    repro_list = f"MCP_REPRO_{int(time.time())}"
    repro_res = json.loads(await create_list(repro_list))
    r_lid = str(repro_res["data"]["id"])

    # Immediate import (Bug #0 check)
    await import_tasks(r_lid, "Regression Task 1\nRegression Task 2")
    
    # Add task + Note (Bug #1 check)
    r_add_res = json.loads(await add_task(r_lid, "Note Target"))
    if "success" in r_add_res and r_add_res["success"]:
        r_tid = str(r_add_res["data"]["id"])
        r_note_res = json.loads(await add_note(r_lid, r_tid, "Regression Note Test"))
        if r_note_res["success"]:
            print("✅ Success: Regression scenarios passed (No ID mismatch or 403).")
        else:
            print(f"❌ Failure: Add Note failed: {r_note_res}")
    else:
        print("❌ Failure: Could not create task for Note check.")

    # -- TEST 8: BUG-010 Cross-List Parent ID Preservation --
    print("\n8. Testing BUG-010: Cross-List Parent ID Preservation...")
    src_list_10 = f"MCP_BUG10_SRC_{int(time.time())}"
    tgt_list_10 = f"MCP_BUG10_TGT_{int(time.time())}"
    
    print(f"Creating source list: {src_list_10}")
    src_res_10 = json.loads(await create_list(src_list_10))
    src_id_10 = str(src_res_10["data"]["id"])
    
    print(f"Creating target list: {tgt_list_10}")
    tgt_res_10 = json.loads(await create_list(tgt_list_10))
    tgt_id_10 = str(tgt_res_10["data"]["id"])
    
    # Add target container
    target_parent_res = json.loads(await add_task(tgt_id_10, "Target Parent Container"))
    target_parent_id = str(target_parent_res["data"]["id"])
    
    # Add task to move (with child to verify hierarchy preservation)
    await import_tasks(src_id_10, "Moving Parent\n  Moving Child")
    
    # Get the ID of the moving parent from the tree
    src_tree_res = json.loads(await get_tree(src_id_10, depth=2))
    src_tree = src_tree_res["data"]
    moving_parent_match = re.search(r"Moving Parent .*?\(ID: (\d+)\)", src_tree)
    if moving_parent_match:
        moving_parent_id = moving_parent_match.group(1)
    else:
        print(f"❌ Failure: Could not find Moving Parent ID in tree: {src_tree}")
        return
    
    print(f"Moving task {moving_parent_id} from {src_id_10} to {tgt_id_10} under parent {target_parent_id}...")
    await move_task_tool(
        list_id=src_id_10, 
        task_id=moving_parent_id, 
        target_list_id=tgt_id_10, 
        target_parent_id=target_parent_id, 
        confirmed=True
    )
    
    # Verify final state
    tgt_tree_final_res = json.loads(await get_tree(tgt_id_10, depth=3))
    tgt_tree_final = tgt_tree_final_res["data"]
    print("\nTarget List Tree (Final):")
    print(tgt_tree_final)
    
    # Check if 'Moving Parent' is nested under 'Target Parent Container'
    # Flexible regex to handle status brackets [ ], indentation, and any metadata
    if re.search(fr"Target Parent Container.*ID: {target_parent_id}.*?\n\s+- \[.\] Moving Parent.*?ID: {moving_parent_id}", tgt_tree_final, re.DOTALL):
        print("✅ Success: BUG-010 verified! Task correctly nested under target parent across lists.")
    else:
        print("❌ Failure: BUG-010 verification failed. Nesting logic check failed.")
        print(f"Debug: Expected nesting not found in tree. Parent ID: {target_parent_id}, Child ID: {moving_parent_id}")

    print("\n🏁 COMPLEX Live Verification Completed.")

async def main():
    try:
        await run_complex_live_tests()
    finally:
        from src.server import shutdown, get_client
        
        # New Cleanup Logic: Delete all lists created in this session (MCP_ prefix)
        print("\n🗑️  Starting Automatic Cleanup...")
        try:
            client = get_client()
            if not client.token: await client.authenticate()
            lists = await client.get_checklists()
            mcp_lists = [l for l in lists if l.name.startswith("MCP_")]
            print(f"Found {len(mcp_lists)} temporary lists to remove.")
            for cl in mcp_lists:
                print(f"Deleting list: {cl.name} ({cl.id})")
                try:
                    await client.delete_checklist(cl.id)
                except Exception as e:
                    print(f"Failed to delete {cl.name}: {e}")
        except Exception as cleanup_err:
            print(f"Cleanup error: {cleanup_err}")

        print("\n🧹 Cleaning up client connections...")
        await shutdown()

if __name__ == "__main__":
    asyncio.run(main())
