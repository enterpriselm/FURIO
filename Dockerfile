# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set working directory in container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Run the app with Gunicorn and Uvicorn
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "api:app", "--workers", "4", "--timeout", "120"]
