import os
from dotenv import load_dotenv
from pathlib import Path


env_path = Path(__file__).resolve().parent.parent / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

required_vars = ["OPENAI_API_KEY", "TAVILY_API_KEY", "MONGODB_URI"]

for var in required_vars:
    value = os.getenv(var)
    print(f"{var} loaded? {bool(value)}")
