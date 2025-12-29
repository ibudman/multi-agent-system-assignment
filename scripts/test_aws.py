import os
from dotenv import load_dotenv
from pathlib import Path
import boto3

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

session = boto3.Session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name="us-east-1"
)

sts = session.client("sts")
identity = sts.get_caller_identity()

print("AWS identity OK:")
print(identity["Arn"])
