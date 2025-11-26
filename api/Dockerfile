FROM python:3.11-slim

WORKDIR /workspace

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code into 'api' directory to support 'from api.app...' imports
COPY . api/

# Set PYTHONPATH to workspace root
ENV PYTHONPATH=/workspace

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "api.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
