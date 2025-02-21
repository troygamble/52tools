import os
import json
import asyncio
import re
from jinja2 import Environment, FileSystemLoader
from openai import AsyncOpenAI
from dotenv import load_dotenv
import aiofiles
import random

# ===============================================
# ✅ Load environment variables from .env file
# ===============================================
load_dotenv()

# ===============================================
# ✅ Set up Async OpenAI client
# ===============================================
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ===============================================
# ✅ Global settings from .env
# ===============================================
base_url = os.getenv("BASE_URL", "https://tool52.com")

# ===============================================
# ✅ Utility: Slugify tool names for safe filenames
# ===============================================
def slugify(name):
    """Convert tool name to a safe slug for filenames and URLs."""
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

# ===============================================
# ✅ Read successful tools from generation_log.txt
# ===============================================
completed_tools = set()
if os.path.exists("generation_log.txt"):
    with open("generation_log.txt", "r", encoding="utf-8") as log_file:
        for line in log_file:
            if line.startswith("[SUCCESS]"):
                tool_name = line.split(" for ")[-1].strip()
                completed_tools.add(tool_name)

# ===============================================
# ✅ Read tool names from tools.txt (excluding completed)
# ===============================================
with open("tools.txt", "r", encoding="utf-8") as f:
    tools = [line.strip() for line in f if line.strip() and line.strip() not in completed_tools]

# ===============================================
# ✅ Set up Jinja2 environment for HTML rendering
# ===============================================
env = Environment(loader=FileSystemLoader("."))
template = env.get_template("base_template.html")

# ===============================================
# ✅ Utility: Retry logic with exponential backoff
# ===============================================
async def call_with_retry(func, retries=3):
    for attempt in range(retries):
        try:
            return await func()
        except Exception as e:
            if attempt < retries - 1:
                await asyncio.sleep(random.uniform(1, 3) * (attempt + 1))
            else:
                raise e

# ===============================================
# ✅ Utility: Save JSON data asynchronously
# ===============================================
async def save_json_async(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    async with aiofiles.open(path, 'w', encoding="utf-8") as f:
        await f.write(json.dumps(data, indent=4))

# ===============================================
# ✅ Attempt flexible JSON parsing from raw response
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
# ✅ Improved prompt generation with strict JSON formatting instructions
# ===============================================
def generate_seo_prompt(tool_name):
    return f"""
    Generate an SEO-optimized title, description, keywords, and canonical URL for a web tool named '{tool_name}'.
    Return the output strictly in valid JSON format without any extra text or explanations.
    The JSON must have the following structure:
    {{
        "title": "...",
        "description": "...",
        "keywords": "...",
        "long_tail_content": "..."
    }}
    Ensure all values are properly escaped and the JSON is valid.
    """

def generate_content_prompt(tool_name):
    return f"""
    Generate functional HTML and JS for the tool '{tool_name}'. Return the output strictly in valid JSON format with this structure:
    {{
        "html": "..."
    }}
    Ensure all content is escaped properly and the JSON is valid. Do not include any explanations.
    """

# ===============================================
# ✅ Function: generate_tool_page with enhanced parsing and improved prompts
# ===============================================
async def generate_tool_page(tool_name, log_file, semaphore, force_regenerate=False):
    tool_slug = slugify(tool_name)
    cache_file = f"cache/{tool_slug}.json"
    tool_dir = f"tools/{tool_slug}"

    async with semaphore:
        try:
            # Check cache unless force_regenerate is True
            if os.path.exists(cache_file) and not force_regenerate:
                async with aiofiles.open(cache_file, 'r', encoding="utf-8") as cache_f:
                    cached_data = json.loads(await cache_f.read())
                seo_content, tool_content = cached_data.get("seo", {}), cached_data.get("html", {})
            else:
                # Fetch SEO and HTML content from OpenAI with enhanced prompts
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

            # Validate critical fields before rendering
            required_fields = ["title", "description", "keywords"]
            if not all(field in seo_content for field in required_fields):
                async with aiofiles.open(log_file, "a", encoding="utf-8") as log:
                    await log.write(f"[ERROR] Missing required SEO fields for {tool_name}: {seo_content}\n")
                print(f"[ERROR] Missing required SEO fields for {tool_name}: {seo_content}")
                return

            # Render final HTML
            rendered_page = template.render(
                tool_title=seo_content.get("title", "Untitled Tool"),
                tool_description=seo_content.get("description", "No description available."),
                tool_keywords=seo_content.get("keywords", ""),
                canonical_url=f"{base_url}/tools/{tool_slug}/index.html",
                navigation="",
                tool_content=tool_content.get("html", "") + seo_content.get("long_tail_content", "")
            )

            os.makedirs(tool_dir, exist_ok=True)
            async with aiofiles.open(f"{tool_dir}/index.html", "w", encoding="utf-8") as f:
                await f.write(rendered_page)

            async with aiofiles.open(log_file, "a", encoding="utf-8") as log:
                await log.write(f"[SUCCESS] Generated page for {tool_name}\n")

            print(f"[SUCCESS] Generated page for {tool_name}")

        except Exception as e:
            async with aiofiles.open(log_file, "a", encoding="utf-8") as log:
                await log.write(f"[ERROR] Failed {tool_name}: {e}\n")
            print(f"[ERROR] Failed {tool_name}: {e}")

# ===============================================
# ✅ Generate navigation JSON for dynamic loading (only successful tools)
# ===============================================
async def generate_navigation_json():
    nav_list = [{"name": tool, "slug": slugify(tool)} for tool in completed_tools]
    os.makedirs("tools", exist_ok=True)
    await save_json_async("tools/tools_list.json", {"tools": nav_list})

# ===============================================
# ✅ Main async function with concurrency control
# ===============================================
async def main(force_regenerate=False):
    os.makedirs("cache", exist_ok=True)
    os.makedirs("tools", exist_ok=True)
    log_file = "generation_log.txt"

    semaphore = asyncio.Semaphore(5)  # Max 5 concurrent tasks
    await generate_navigation_json()
    await asyncio.gather(*(generate_tool_page(tool, log_file, semaphore, force_regenerate) for tool in tools))

    print("🎉 All pages generated! Check 'generation_log.txt' for details.")

# ===============================================
# ✅ Script Entry Point
# ===============================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate tool pages with optional force regeneration.")
    parser.add_argument("--force", action="store_true", help="Force regeneration of all tools, ignoring cache.")
    args = parser.parse_args()

    asyncio.run(main(force_regenerate=args.force))
