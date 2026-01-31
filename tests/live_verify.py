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
    print("\n5. Verifying search with breadcrumbs...")
    search_res = await search_tasks("Deepest")
    print("Search Result:")
    # The actual breadcrumb includes @meeting as part of content
    if "Level 1 Root > Level 2 Child > Level 3 Grandchild @meeting > Level 4 Great-Grandchild > Level 5 Deepest Leaf" in search_res:
        print("✅ Success: Search results show full breadcrumb path.")
    else:
        print("❌ Failure: Breadcrumbs incomplete in search.")

    print("\n🏁 COMPLEX Live Verification Completed.")

if __name__ == "__main__":
    asyncio.run(run_complex_live_tests())
