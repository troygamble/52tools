### ✅ **Full Updated `generate_index.py`**

import os
import json
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

# ===============================================
# ✅ Load environment variables from .env file
# ===============================================
load_dotenv()

# ===============================================
# ✅ Global settings from .env
# ===============================================
base_url = os.getenv("BASE_URL", "https://yourusername.github.io")
adsense_code = os.getenv("ADSENSE_CODE", "<!-- AdSense placeholder -->")

# ===============================================
# ✅ Read tool names and metadata from files
# ===============================================
with open("tools.txt", "r") as f:
    tools = [line.strip() for line in f if line.strip()]

# NEW: Reading tool descriptions if available
if os.path.exists("tools_metadata.json"):
    with open("tools_metadata.json", "r") as meta_file:
        tools_metadata = json.load(meta_file)
else:
    tools_metadata = {tool: "A powerful and free online tool designed to simplify your daily tasks." for tool in tools}

# ===============================================
# ✅ Set up Jinja2 environment for HTML rendering
# ===============================================
env = Environment(loader=FileSystemLoader("."))
template = env.get_template("base_template.html")

# ===============================================
# ✅ Function: generate_index_page
# ===============================================
def generate_index_page():
    try:
        # ✅ Create HTML content for the list of tools with descriptions
        tools_list_html = "".join([
            f'<li><a href="/tools/{tool.lower().replace(" ", "-")}/index.html"><strong>{tool}</strong>: {tools_metadata.get(tool, "")}</a></li>'
            for tool in tools
        ])

        # ✅ Long-tail SEO content for better search visibility
        long_tail_content = """
        <section>
            <h2>Welcome to 52tools - Your One-Stop Shop for Online Tools</h2>
            <p>Explore our collection of 52 highly optimized online tools, designed to boost productivity, simplify daily tasks, and provide essential functionalities for developers, content creators, and businesses.</p>
            <p>Each tool comes with intuitive interfaces, powerful functionality, and optimized SEO content to ensure you can find what you need quickly and efficiently.</p>
            <p>Bookmark this page to access new tools as they are added. We continuously expand and refine our collection to meet evolving needs.</p>
        </section>
        """

        # ✅ Render the final index.html page using the base template
        rendered_index = template.render(
            tool_title="52tools - The Ultimate Collection of Online Tools",
            tool_description="Explore 52 powerful and free online tools designed for your daily needs.",
            tool_keywords="online tools, free tools, productivity",
            canonical_url=f"{base_url}/index.html",
            navigation=tools_list_html,
            tool_content=long_tail_content,
            adsense_code=adsense_code
        )

        # ✅ Write the index.html to the project root
        with open("index.html", "w") as f:
            f.write(rendered_index)
        print("✅ Successfully generated index.html with descriptions.")

    except Exception as e:
        print(f"❌ Error generating index.html: {e}")

# ===============================================
# ✅ Script Entry Point
# ===============================================
if __name__ == "__main__":
    generate_index_page()

# ===============================================
# 🎯 KEY FEATURES:
# - ✅ Dynamically lists all tools from tools.txt with descriptions.
# - ✅ Incorporates global AdSense code.
# - ✅ SEO-optimized title, description, and keywords.
# - ✅ Long-tail SEO content for enhanced search visibility.
# - ✅ Automatically updates whenever tools.txt changes.
# - ✅ Fully integrated with existing navigation structure.
# ===============================================