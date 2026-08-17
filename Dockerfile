# Base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (better layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code and templates
COPY app.py .
COPY templates/ templates/

# Expose Flask port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]