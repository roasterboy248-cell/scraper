# Use the official Scrapling image as base
FROM ghcr.io/d4vinci/scrapling:latest

# Set working directory
WORKDIR /app

# Install FastAPI and uvicorn on top of Scrapling
RUN pip install fastapi uvicorn --break-system-packages

# Copy our API wrapper
COPY main.py .

# Expose port
EXPOSE 10000

# Start the API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
