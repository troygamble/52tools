import os
import json
import asyncio
import re
from jinja2 import Environment, FileSystemLoader
from openai import AsyncOpenAI
from dotenv import load_dotenv
import aiofiles
import random
import argparse
import logging

# ===============================================
# ✅ Load environment variables from .env file
# ===============================================
load_dotenv()

# ===============================================
# ✅ Set up logging
# ===============================================
logging.basicConfig(
    filename="generation_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ===============================================
# ✅ Set up Async OpenAI client
# ===============================================
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ===============================================
# ✅ Global settings from .env
# ===============================================
base_url = ""


# ===============================================
# ✅ Utility: Slugify tool names for safe filenames
# ===============================================
def slugify(name):
    """Convert tool name to a safe slug for filenames and URLs."""
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

# ===============================================
# ✅ Utility: Retry logic with exponential backoff and rate limit handling
# ===============================================
async def call_with_retry(func, retries=3):
    for attempt in range(retries):
        try:
            return await func()
        except Exception as e:
            if hasattr(e, 'status_code') and e.status_code == 429:
                logging.warning(f"Rate limit reached. Retrying... ({attempt + 1}/{retries})")
                await asyncio.sleep(10)
            elif attempt < retries - 1:
                await asyncio.sleep(random.uniform(1, 3) * (attempt + 1))
            else:
                logging.error(f"API call failed after {retries} attempts: {e}")
                raise e

# ===============================================
# ✅ Save JSON asynchronously
# ===============================================
async def save_json_async(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    async with aiofiles.open(path, 'w', encoding="utf-8") as f:
        await f.write(json.dumps(data, indent=4))

# ===============================================
# ✅ Flexible JSON parsing
# ===============================================
def parse_json_flexibly(raw_content):
    try:
        return json.loads(raw_content)
    except json.JSONDecodeError:
        json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        return {"html": raw_content.strip()}

# ===============================================
# ✅ Prompt generation for SEO and content
# ===============================================
def generate_seo_prompt(tool_name):
    return f"""
    Generate an SEO-optimized title, description, keywords, and canonical URL for a web tool named '{tool_name}'.
    Return the output strictly in valid JSON format without any extra text or explanations.
    {{
        "title": "...",
        "description": "...",
        "keywords": "...",
        "long_tail_content": "..."
    }}
    """

def generate_content_prompt(tool_name):
    return f"""
    Generate functional HTML and JS for the tool '{tool_name}'. Return the output strictly in valid JSON format:
    {{
        "html": "..."
    }}
    """

# ===============================================
# ✅ Load tools list with fallback
# ===============================================
def load_tools_list():
    try:
        if os.path.exists("tools/tools_list.json"):
            with open("tools/tools_list.json", "r", encoding="utf-8") as f:
                tools = json.load(f).get("tools", [])
                logging.info(f"Loaded {len(tools)} tools from tools_list.json.")
                return tools
        elif os.path.exists("tools.txt"):
            with open("tools.txt", "r", encoding="utf-8") as f:
                tools = [{"name": line.strip()} for line in f if line.strip()]
                logging.info(f"Loaded {len(tools)} tools from tools.txt.")
                return tools
        logging.warning("No tools found. Returning empty list.")
        return []
    except Exception as e:
        logging.error(f"Failed to load tools list: {e}")
        return []

# ===============================================
# ✅ Load tools metadata
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
# ✅ Generate navigation JSON
# ===============================================
async def generate_navigation_json(tools_list):
    nav_list = [{"name": tool["name"], "slug": slugify(tool["name"])} for tool in tools_list]
    os.makedirs("tools", exist_ok=True)
    await save_json_async("tools/tools_list.json", {"tools": nav_list})

# ===============================================
# ✅ Generate individual tool pages with async file handling
# ===============================================
async def generate_tool_page(tool_name, log_file, semaphore, force_regenerate=False):
    tool_slug = slugify(tool_name)
    cache_file = f"cache/{tool_slug}.json"
    tool_dir = f"tools/{tool_slug}"

    async with semaphore:
        try:
            if os.path.exists(cache_file) and not force_regenerate:
                async with aiofiles.open(cache_file, 'r', encoding="utf-8") as cache_f:
                    cached_data = json.loads(await cache_f.read())
                seo_content, tool_content = cached_data.get("seo", {}), cached_data.get("html", {})
            else:
                seo_response = await call_with_retry(lambda: client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": generate_seo_prompt(tool_name)}]
                ))
                content_response = await call_with_retry(lambda: client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": generate_content_prompt(tool_name)}]
                ))

                seo_content = parse_json_flexibly(seo_response.choices[0].message.content)
                tool_content = parse_json_flexibly(content_response.choices[0].message.content)

                await save_json_async(cache_file, {"seo": seo_content, "html": tool_content})

            required_fields = ["title", "description", "keywords"]
            if not all(field in seo_content for field in required_fields):
                logging.error(f"Missing required SEO fields for {tool_name}: {seo_content}")
                return

            # ✅ Extract only the <body> content from the HTML
            full_html = tool_content.get("html", "")
            body_match = re.search(r"<body.*?>(.*?)</body>", full_html, re.DOTALL)
            tool_html_content = body_match.group(1) if body_match else full_html

            # ✅ Updated: Pass base_url to the template for dynamic path handling
            rendered_page = template.render(
                base_url=base_url,
                tool_title=seo_content.get("title", "Untitled Tool"),
                tool_description=seo_content.get("description", "No description available."),
                tool_keywords=seo_content.get("keywords", ""),
                canonical_url=f"{base_url}/tools/{tool_slug}/index.html",
                navigation="",
                tool_content=tool_html_content + seo_content.get("long_tail_content", ""),
                depth=2
            )

            os.makedirs(tool_dir, exist_ok=True)
            async with aiofiles.open(f"{tool_dir}/index.html", "w", encoding="utf-8") as f:
                await f.write(rendered_page)

            logging.info(f"[SUCCESS] Generated page for {tool_name}")

            # ✅ Save the raw tool HTML separately for reference
            async with aiofiles.open(f"{tool_dir}/tool_code.html", "w", encoding="utf-8") as f:
                await f.write(full_html)

        except Exception as e:
            logging.error(f"[ERROR] Failed {tool_name}: {e}")

# ===============================================
# ✅ Set up Jinja2 environment with validation
# ===============================================
try:
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("base_template.html")
except Exception as e:
    logging.critical(f"Template loading failed: {e}")
    raise

# ===============================================
# ✅ Main async function with concurrency control
# ===============================================
async def main(force_regenerate=False, refresh_only=False):
    os.makedirs("tools", exist_ok=True)
    tools_list = load_tools_list()
    tools_metadata = load_tools_metadata()

    if refresh_only:
        logging.info("🔄 Refreshing pages without API calls...")
        await asyncio.gather(*[
            generate_tool_page(tool["name"], "generation_log.txt", asyncio.Semaphore(5), force_regenerate=False)
            for tool in tools_list
        ])
    else:
        logging.info("🚀 Generating pages with full processing...")
        semaphore = asyncio.Semaphore(5)
        await asyncio.gather(*[
            generate_tool_page(tool["name"], "generation_log.txt", semaphore, force_regenerate)
            for tool in tools_list
        ])

    await generate_navigation_json(tools_list)
    logging.info("🎉 All pages processed! Check 'generation_log.txt' for details.")

# ===============================================
# ✅ Script Entry Point
# ===============================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate or refresh tool pages.")
    parser.add_argument("--force", action="store_true", help="Force regenerate all pages (costly).")
    parser.add_argument("--refresh", action="store_true", help="Refresh pages without API calls.")
    args = parser.parse_args()

    asyncio.run(main(force_regenerate=args.force, refresh_only=args.refresh))
