import os
from dotenv import load_dotenv

load_dotenv()

required_vars = ["OPENAI_API_KEY", "TAVILY_API_KEY", "MONGODB_URI"]

for var in required_vars:
    value = os.getenv(var)
    print(f"{var} loaded? {bool(value)}")