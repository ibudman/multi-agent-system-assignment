import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Force-load .env from the project root
env_path = Path(__file__).resolve().parent.parent / ".env"
loaded = load_dotenv(dotenv_path=env_path)

print("Loaded .env?", loaded)
print("env_path =", env_path)
print("OPENAI_API_KEY present?", bool(os.getenv("OPENAI_API_KEY")))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.responses.create(
    model="gpt-4.1-mini",
    input="Say 'OpenAI setup works' in one short sentence."
)

print(response.output_text)