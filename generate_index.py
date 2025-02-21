import os
import json
import re
import logging
from jinja2 import Environment, FileSystemLoader, TemplateError
from dotenv import load_dotenv

# ===============================================
# ✅ Configure Logging
# ===============================================
logging.basicConfig(
    filename="index_generation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ===============================================
# ✅ Load environment variables from .env file
# ===============================================
load_dotenv()

# ===============================================
# ✅ Global settings from .env
# ===============================================
base_url = os.getenv("BASE_URL", "https://troygamble.github.io/52tools")


# ===============================================
# ✅ Utility: Slugify tool names for safe filenames
# ===============================================
def slugify(name):
    """Convert tool name to a safe slug for filenames and URLs."""
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

# ===============================================
# ✅ Load tools metadata from tools/tools_list.json
# ===============================================
def load_tools_list():
    try:
        if os.path.exists("tools/tools_list.json"):
            with open("tools/tools_list.json", "r", encoding="utf-8") as f:
                tools = json.load(f).get("tools", [])
                logging.info(f"Loaded {len(tools)} tools from tools_list.json.")
                return tools
        logging.warning("tools/tools_list.json not found. Returning empty list.")
        return []
    except Exception as e:
        logging.error(f"Failed to load tools list: {e}")
        return []

# ===============================================
# ✅ Load tool descriptions from tools_metadata.json
# ===============================================
def load_tools_metadata():
    try:
        if os.path.exists("tools_metadata.json"):
            with open("tools_metadata.json", "r", encoding="utf-8") as f:
                metadata = json.load(f)
                logging.info(f"Loaded metadata for {len(metadata)} tools.")
                return metadata
        logging.warning("tools_metadata.json not found.")
        return {}
    except Exception as e:
        logging.error(f"Failed to load tools metadata: {e}")
        return {}

# ===============================================
# ✅ Set up Jinja2 environment for HTML rendering
# ===============================================
try:
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("base_template.html")
    logging.info("Jinja2 environment and template loaded successfully.")
except TemplateError as e:
    logging.critical(f"Template loading failed: {e}")
    raise

# ===============================================
# ✅ Function: generate_index_page (homepage only)
# ===============================================
def generate_index_page():
    try:
        tools_list = load_tools_list()
        if not tools_list:
            logging.warning("No tools found to include in the index page.")

        tools_metadata = load_tools_metadata()

        # ✅ Create HTML content for the list of tools with available metadata
        tools_list_html = "".join([
            f'<li><a href="/tools/{slugify(tool["name"])}/index.html">'
            f'<strong>{tool["name"]}</strong>: '
            f'{tools_metadata.get(tool["name"], {}).get("description", "Description coming soon.")}'
            f'</a></li>'
            for tool in tools_list
        ])

        all_keywords = [
            kw
            for tool in tools_list
            for kw in tools_metadata.get(tool["name"], {}).get("keywords", [])
        ]

        # ✅ Long-tail SEO content for better search visibility
        long_tail_content = """
        <section>
            <h2>Welcome to 52tools - Your One-Stop Shop for Online Tools</h2>
            <p>Explore our collection of 52 highly optimized online tools, designed to boost productivity, simplify daily tasks, and provide essential functionalities for developers, content creators, and businesses.</p>
            <p>Each tool comes with intuitive interfaces, powerful functionality, and optimized SEO content to ensure you can find what you need quickly and efficiently.</p>
            <p>Bookmark this page to access new tools as they are added. We continuously expand and refine our collection to meet evolving needs.</p>
        </section>
        """

        # ✅ Render the final index.html page using enriched SEO data
        try:
            rendered_index = template.render(
                tool_title="52tools - The Ultimate Collection of Online Tools",
                tool_description="Explore 52 powerful and free online tools designed for your daily needs.",
                tool_keywords=", ".join(set(all_keywords)),
                canonical_url=f"{base_url}/index.html",
                navigation=tools_list,
                tool_content=long_tail_content + f'<ul>{tools_list_html}</ul>',
                depth=0 #added depth for main index
            )
            logging.info("Template rendered successfully.")
        except TemplateError as e:
            logging.error(f"Error rendering template: {e}")
            return

        # ✅ Write the index.html to the project root
        try:
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(rendered_index)
            logging.info("index.html generated successfully.")
        except Exception as e:
            logging.error(f"Failed to write index.html: {e}")

    except Exception as e:
        logging.critical(f"Critical failure in generate_index_page: {e}")

# ===============================================
# ✅ Script Entry Point
# ===============================================
if __name__ == "__main__":
    generate_index_page()
    logging.info("Index page generation script completed.")
