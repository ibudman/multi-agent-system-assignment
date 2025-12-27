import os
from pathlib import Path
from dotenv import load_dotenv
from tavily import TavilyClient

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

res = client.search(
    query="LangGraph Tavily multi-agent example",
    max_results=5
)

print("Got results:", len(res.get("results", [])))
print("Top title:", res["results"][0]["title"] if res.get("results") else None)