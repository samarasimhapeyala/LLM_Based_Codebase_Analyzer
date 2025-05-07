# Use a lightweight Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Copy .env file if it exists (important for loading environment variables)
COPY .env .env

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Expose app port (update if different)
EXPOSE 8000

# Start your app
CMD ["python", "app.py"]

