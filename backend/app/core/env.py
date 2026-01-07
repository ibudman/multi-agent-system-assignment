import os


REQUIRED_ENV_VARS = [
    "OPENAI_API_KEY",
    "TAVILY_API_KEY",
    "MONGODB_URI",
]


def validate_env() -> None:
    missing = [k for k in REQUIRED_ENV_VARS if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")
