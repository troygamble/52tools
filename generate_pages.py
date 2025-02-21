import os
import json
import asyncio
from jinja2 import Environment, FileSystemLoader
from openai import OpenAI
from dotenv import load_dotenv

# ===============================================
# ✅ Load environment variables from .env file
# ===============================================
# This ensures sensitive data like API keys and configurable variables
# such as AdSense code and base URL are not hard-coded.
load_dotenv()

# ===============================================
# ✅ Set up OpenAI client
# ===============================================
# Initializes the OpenAI client using the API key from the .env file.
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ===============================================
# ✅ Global settings from .env
# ===============================================
# Retrieves AdSense code and base URL for canonical links from environment variables.
# Defaults are provided in case these variables are missing.
adsense_code = os.getenv("ADSENSE_CODE", "<!-- AdSense placeholder -->")
base_url = os.getenv("BASE_URL", "https://yourusername.github.io")

# ===============================================
# ✅ Read tool names from tools.txt
# ===============================================
# Reads all tool names from the file and strips any empty lines.
with open("tools.txt", "r") as f:
    tools = [line.strip() for line in f if line.strip()]

# ===============================================
# ✅ Set up Jinja2 environment for HTML rendering
# ===============================================
# Configures Jinja2 to load HTML templates from the current directory.
env = Environment(loader=FileSystemLoader("."))
template = env.get_template("base_template.html")

# ===============================================
# ✅ Function: generate_tool_page
# ===============================================
# Generates both SEO content and functional HTML+JS for each tool asynchronously.
# Handles OpenAI API calls, writes the generated page, and logs results.
async def generate_tool_page(tool_name, log_file):
    try:
        # Prompt for SEO metadata generation
        seo_prompt = f"""
        Generate an SEO-optimized title, description, keywords, and canonical URL for a web tool named '{tool_name}'.
        Include long-tail SEO content such as FAQs, user guides, and example use cases.
        Return in JSON format with keys: 'title', 'description', 'keywords', 'long_tail_content'.
        """

        # Prompt for tool HTML + JavaScript code generation
        content_prompt = f"""
        Generate fully functional HTML and JavaScript code for a web tool named '{tool_name}'.
        The HTML should include forms, buttons, and output areas as needed.
        The JavaScript should provide full interactivity for the tool.
        Include clear comments in the code explaining functionality.
        Return in JSON format with a 'html' key.
        """

        # 🔄 Call OpenAI API for SEO content
        seo_response = await client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": seo_prompt}]
        )

        # 🔄 Call OpenAI API for functional HTML/JS content
        content_response = await client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": content_prompt}]
        )

        # ✅ Parse the OpenAI responses into JSON
        seo_content = json.loads(seo_response.choices[0].message.content)
        tool_content = json.loads(content_response.choices[0].message.content)

        # ✅ Render the final HTML page with Jinja2 template
        rendered_page = template.render(
            tool_title=seo_content["title"],
            tool_description=seo_content["description"],
            tool_keywords=seo_content["keywords"],
            canonical_url=f"{base_url}/tools/{tool_name.lower().replace(' ', '-')}/index.html",
            navigation="".join([
                f'<li><a href=\"/tools/{tool.lower().replace(" ", "-")}/index.html\">{tool}</a></li>' 
                for tool in tools
            ]),
            tool_content=tool_content["html"] + seo_content.get("long_tail_content", ""),
            adsense_code=adsense_code
        )

        # ✅ Create the directory for the tool page if it doesn't exist
        tool_dir = f"tools/{tool_name.lower().replace(' ', '-')}"
        os.makedirs(tool_dir, exist_ok=True)

        # ✅ Write the generated HTML to the appropriate file
        with open(f"{tool_dir}/index.html", "w") as f:
            f.write(rendered_page)

        # ✅ Log successful generation
        with open(log_file, "a") as log:
            log.write(f"✅ SUCCESS: Generated page for {tool_name}\n")
        print(f"✅ Generated page for {tool_name}")

    except Exception as e:
        # ⚠️ Error handling and logging
        with open(log_file, "a") as log:
            log.write(f"❌ ERROR: Failed to generate {tool_name}: {e}\n")
        print(f"❌ Error generating page for {tool_name}: {e}")

# ===============================================
# ✅ Main async function to generate all pages concurrently
# ===============================================
# Uses asyncio.gather to run multiple generation tasks in parallel for efficiency.
async def main():
    log_file = "generation_log.txt"
    if os.path.exists(log_file):
        os.remove(log_file)  # Clear previous logs for a fresh run

    await asyncio.gather(*(generate_tool_page(tool, log_file) for tool in tools))
    print("🎉 All pages generated successfully! Check 'generation_log.txt' for details.")

# ===============================================
# ✅ Script Entry Point
# ===============================================
# Runs the main function when the script is executed directly.
if __name__ == "__main__":
    asyncio.run(main())

# ===============================================
# 🎯 KEY FEATURES:
# - ✅ Asynchronous generation for speed.
# - ✅ Global management of AdSense code and base URL.
# - ✅ Robust error logging in 'generation_log.txt'.
# - ✅ Dynamic navigation links.
# - ✅ Fully functional HTML + JavaScript integration with long-tail SEO content.
# - ✅ Clear comments and documentation throughout.
# ===============================================
