import os
import json
import re

def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

tools_dir = './tools'
tools = []

# Scan the tools folder for subdirectories
if os.path.exists(tools_dir):
    for tool_folder in os.listdir(tools_dir):
        if os.path.isdir(os.path.join(tools_dir, tool_folder)):
            tool_name = tool_folder.replace('-', ' ').title()
            tools.append({"name": tool_name, "slug": tool_folder})

# Write to tools_list.json
os.makedirs(tools_dir, exist_ok=True)
with open(os.path.join(tools_dir, 'tools_list.json'), 'w', encoding='utf-8') as f:
    json.dump({"tools": tools}, f, indent=4)

print(f"✅ Regenerated tools_list.json with {len(tools)} tools.")
