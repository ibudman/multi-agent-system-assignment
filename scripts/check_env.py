import os


required_vars = ["OPENAI_API_KEY", "TAVILY_API_KEY", "MONGODB_URI"]

for var in required_vars:
    value = os.getenv(var)
    print(f"{var} loaded? {bool(value)}")
