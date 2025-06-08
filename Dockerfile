# Use official Python runtime as a parent image
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

# Copy all your app files to container
COPY . .

# Expose port 8080 for Flask app
ENV PORT 8080
EXPOSE 5000

# Command to run your Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
