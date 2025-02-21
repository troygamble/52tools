### Updated `generate_pages.py`

```python
import os
import json
import asyncio
from jinja2 import Environment, FileSystemLoader
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Global settings from .env
adsense_code = os.getenv("ADSENSE_CODE", "<!-- AdSense placeholder -->")
base_url = os.getenv("BASE_URL", "https://yourusername.github.io")

# Read tools from tools.txt
with open("tools.txt", "r") as f:
    tools = [line.strip() for line in f if line.strip()]

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader("."))
template = env.get_template("base_template.html")

# Function to generate content and tool logic using OpenAI
async def generate_tool_page(tool_name):
    try:
        seo_prompt = f"""
        Generate an SEO-optimized title, description, keywords, and canonical URL for a web tool named '{tool_name}'.
        Return in JSON format with keys: 'title', 'description', 'keywords'.
        """

        content_prompt = f"""
        Generate fully functional HTML and JavaScript code for a web tool named '{tool_name}'.
        The HTML should include forms, buttons, and output areas as needed.
        The JavaScript should provide full interactivity for the tool.
        Return in JSON format with a 'html' key.
        """

        seo_response = await client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": seo_prompt}]
        )

        content_response = await client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": content_prompt}]
        )

        seo_content = json.loads(seo_response.choices[0].message.content)
        tool_content = json.loads(content_response.choices[0].message.content)

        rendered_page = template.render(
            tool_title=seo_content["title"],
            tool_description=seo_content["description"],
            tool_keywords=seo_content["keywords"],
            canonical_url=f"{base_url}/tools/{tool_name.lower().replace(' ', '-')}/index.html",
            navigation="".join([f'<li><a href=\"/tools/{tool.lower().replace(" ", "-")}/index.html\">{tool}</a></li>' for tool in tools]),
            tool_content=tool_content["html"],
            adsense_code=adsense_code
        )

        tool_dir = f"tools/{tool_name.lower().replace(' ', '-')}"
        os.makedirs(tool_dir, exist_ok=True)

        with open(f"{tool_dir}/index.html", "w") as f:
            f.write(rendered_page)

        print(f"Generated page for {tool_name}")

    except Exception as e:
        print(f"Error generating page for {tool_name}: {e}")

# Main async function to generate all pages
async def main():
    await asyncio.gather(*(generate_tool_page(tool) for tool in tools))
    print("All pages generated successfully!")

if __name__ == "__main__":
    asyncio.run(main())
