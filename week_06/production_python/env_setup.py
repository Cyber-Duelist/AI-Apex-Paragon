import os
import sys
from dotenv import load_dotenv

load_dotenv()

app_name = os.getenv("APP_NAME")
env = os.getenv("ENV")
db_path = os.getenv("DB_PATH")
secret_key = os.getenv("SECRET_KEY")

print("=== APP CONFIGURATION ===")
print(f"App Name   : {app_name}")
print(f"Environment: {env}")
print(f"DB Path    : {db_path}")
print(f"Secret Key : {secret_key}")

if not secret_key:
    print("ERROR: SECRET_KEY not set")
    sys.exit(1)

print("All config loaded successfully.")