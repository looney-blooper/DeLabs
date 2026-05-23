# Use a lightweight Python 3.11 image
FROM python:3.11-slim

# Prevent Python from writing pyc files and keep stdout unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (required for some ML libraries or Postgres drivers)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements first to cache the pip install step
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the FastAPI server with hot-reloading
CMD ["uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "src", "--reload-exclude", "workspace", "--reload-exclude", "workspace/*"]