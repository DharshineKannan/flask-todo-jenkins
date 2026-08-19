# Base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Run the application as an unprivileged user
RUN groupadd --system app && useradd --system --gid app --create-home app

# Copy requirements first (better layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code and templates
COPY --chown=app:app app.py wsgi.py ./
COPY --chown=app:app templates/ templates/

USER app

# Expose Flask port
EXPOSE 5000

# Run the app with a production WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--access-logfile", "-", "--error-logfile", "-", "wsgi:app"]
