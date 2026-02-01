import os
import asyncio
import sys
import re
import time
from pathlib import Path

# Add project root to path (one level up from tests/)
sys.path.append(str(Path(__file__).parent.parent))

from src.server import (
    get_client, get_service, create_list, add_task, 
    import_tasks, archive_task, apply_template, get_tree,
    search_tasks
)

async def run_complex_live_tests():
    print("🚀 Starting COMPLEX Live Verification...")
    
    # -- TEST 1: Deep Hierarchy & Smart Syntax --
    test_list_name = f"MCP_COMPLEX_{int(time.time())}"
    print(f"\n1. Creating complex list: {test_list_name}")
    list_res = await create_list(test_list_name)
    list_id = re.search(r"ID: (\d+)", list_res).group(1)
    
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
    tree_v1 = await get_tree(list_id, depth=5)
    print("\nInitial Complex Tree:")
    print(tree_v1)
    
    # -- TEST 2: Recursive Archiving with Metadata --
    root_id_match = re.search(r"Level 1 Root .* \(ID: (\d+)\)", tree_v1)
    if root_id_match:
        root_id = root_id_match.group(1)
        print(f"\n2. Archiving recursive root ID: {root_id}")
        await archive_task(list_id, root_id)
        
        # Check tree - everything under root should be hidden
        tree_after = await get_tree(list_id, depth=5)
        if "Level 1 Root" not in tree_after and "Level 5 Deepest" not in tree_after:
            print("✅ Success: Deep hierarchy recursively archived.")
        else:
            print("❌ Failure: Deep tasks still visible after archive.")

    # -- TEST 3: Template Application with Metadata & Complexity --
    dest_list_name = f"MCP_TEMPLATE_DEST_{int(time.time())}"
    print(f"\n3. Creating destination list: {dest_list_name}")
    dest_res = await create_list(dest_list_name)
    dest_id = re.search(r"ID: (\d+)", dest_res).group(1)
    
    print(f"Applying complex template from {list_id} to {dest_id}...")
    await apply_template(list_id, dest_id, confirmed=True)
    
    dest_tree = await get_tree(dest_id, depth=5)
    print("\nDestination Tree (after template - should be filtered of archived):")
    print(dest_tree)
    
    if "Flat Task #simple" in dest_tree and "Level 1 Root" not in dest_tree:
        print("✅ Success: Template applied with filtering of archived tasks.")
    else:
        print("❌ Failure: Template still contains archived tasks or missing others.")

    # -- TEST 4: Metadata Restoration (New List, Clean Template) --
    print("\n4. Testing Metadata Restoration in Template...")
    src_list_2 = f"MCP_SRC_2_{int(time.time())}"
    src_res_2 = await create_list(src_list_2)
    src_id_2 = re.search(r"ID: (\d+)", src_res_2).group(1)
    await import_tasks(src_id_2, "Source Task !2 #meta ^2026-12-31\n  Nested !3 #sub")
    
    dest_list_2 = f"MCP_DEST_2_{int(time.time())}"
    dest_res_2 = await create_list(dest_list_2)
    dest_id_2 = re.search(r"ID: (\d+)", dest_res_2).group(1)
    
    await apply_template(src_id_2, dest_id_2, confirmed=True)
    dest_tree_2 = await get_tree(dest_id_2, depth=2)
    print("Restore Tree:")
    print(dest_tree_2)
    
    if "!2 #meta" in dest_tree_2 and "!3 #sub" in dest_tree_2:
        print("✅ Success: Metadata (priorities/tags) restored in template.")
    else:
        print("❌ Failure: Metadata lost in template application.")

    # -- TEST 5: Search Verification with Breadcrumbs --
    print("\n5. Verifying search with breadcrumbs (targeting non-archived task)...")
    search_res = await search_tasks("Flat Task")
    print("Search Result:")
    print(search_res)
    if "Flat Task #simple" in search_res:
        print("✅ Success: Search results show visible tasks correctly.")
    else:
        print("❌ Failure: Search failed to find a visible task.")

    # -- TEST 6: Reopen Task Logic --
    print("\n6. Testing reopen_task logic...")
    add_res = await add_task(list_id, "Task to Close and Reopen")
    print(f"Add task result: {add_res}")
    
    # Try to extract ID from add_task result directly
    id_match = re.search(r"ID: (\d+)", add_res)
    if not id_match:
        # Fallback to tree
        tree_v6 = await get_tree(list_id, depth=1)
        print(f"v6 Tree:\n{tree_v6}")
        id_match = re.search(r"Task to Close and Reopen .* \(ID: (\d+)\)", tree_v6)
    
    if id_match:
        target_id = id_match.group(1)
        from src.server import close_task, reopen_task
        print(f"Closing task {target_id}...")
        await close_task(list_id, target_id)
        print(f"Reopening task {target_id}...")
        reopen_res = await reopen_task(list_id, target_id)
        print(f"Reopen result: {reopen_res}")
        if "Task reopened" in reopen_res:
            print("✅ Success: Task reopened without error.")
        else:
            print(f"❌ Failure: Unexpected response from reopen_task")
    else:
         print("❌ Failure: Could not identify task ID for reopen test.")

    # -- TEST 7: Regression Check (Bug #0 & #1 Verification) --
    print("\n7. Testing Regression Scenarios (ID Mismatch & 403 checks)...")
    repro_list = f"MCP_REPRO_{int(time.time())}"
    repro_res = await create_list(repro_list)
    repro_match = re.search(r"ID: (\d+)", repro_res)
    if repro_match:
        r_lid = repro_match.group(1)
        # Immediate import (Bug #0 check)
        await import_tasks(r_lid, "Regression Task 1\nRegression Task 2")
        
        # Add task + Note (Bug #1 check)
        r_add_res = await add_task(r_lid, "Note Target")
        r_tm = re.search(r"ID: (\d+)", r_add_res)
        if r_tm:
            r_tid = r_tm.group(1)
            r_note = await from.src.server import add_note # dynamic import needed or reuse if top-level
            # Wait, better to import at top or assume available if imported in this file.
            # Checking imports... add_note is NOT imported in original file.
            from src.server import add_note
            r_note_res = await add_note(r_lid, r_tid, "Regression Note Test")
            if "Note added" in r_note_res:
                print("✅ Success: Regression scenarios passed (No ID mismatch or 403).")
            else:
                print(f"❌ Failure: Add Note failed: {r_note_res}")
        else:
             print("❌ Failure: Could not parse ID for Note Target.")
    else:
        print("❌ Failure: Could not create list for regression check.")

    print("\n🏁 COMPLEX Live Verification Completed.")

async def main():
    try:
        await run_complex_live_tests()
    finally:
        from src.server import shutdown
        print("\n🧹 Cleaning up client connections...")
        await shutdown()

if __name__ == "__main__":
    asyncio.run(main())
