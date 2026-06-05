# 1. Base Image: Use a lightweight version of Python 3.12
FROM python:3.12-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements and install dependencies
# We use --no-cache-dir to keep the container size small
COPY week_06/production_python/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Bring in the API logic and Database from Week 5
COPY week_05/sql_fastapi/crud.py .
COPY week_05/sql_fastapi/pydantic_models.py .
COPY week_05/sql_fastapi/documents.db .

# 5. Bring in the environment secrets from Week 6
COPY week_06/production_python/.env .

# 6. Expose the port that FastAPI will broadcast on
EXPOSE 8000

# 7. Start the Uvicorn engine inside the container
CMD ["uvicorn", "crud:app", "--host", "0.0.0.0", "--port", "8000"]