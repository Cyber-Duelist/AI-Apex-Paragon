FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for sqlite and some python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose Streamlit port
EXPOSE 7860

# Run Streamlit
CMD ["streamlit", "run", "src/app.py", "--server.port", "7860", "--server.address", "0.0.0.0", "--server.enableXsrfProtection", "false", "--server.enableCORS", "false"]
