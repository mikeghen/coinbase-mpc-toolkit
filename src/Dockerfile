# src/Dockerfile

# Base image
FROM python:3.10-slim

# Install PostgreSQL development libraries
RUN apt-get update && apt-get install -y \
    libpq-dev gcc

# Set working directory
WORKDIR /src

# Copy requirements.txt and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port the Flask app runs on
EXPOSE 5000

# Define the command to run the Flask app
CMD ["python", "server.py"]
