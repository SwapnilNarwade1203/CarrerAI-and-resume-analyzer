# Use the official lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files to the working directory
COPY . /app/

# Expose port 8000 (Render will route public port 80/443 to this)
EXPOSE 8000

# Make the entrypoint script executable
RUN chmod +x /app/docker-entrypoint.sh

# Use the entrypoint script to run migrations, collectstatic, and start Gunicorn
ENTRYPOINT ["/app/docker-entrypoint.sh"]
