from dotenv import load_dotenv
import os

load_dotenv()
print("API KEY:", os.getenv("OPENAI_API_KEY"))
print("BASE URL:", os.getenv("BASE_URL"))
print("ADSENSE CODE:", os.getenv("ADSENSE_CODE"))
