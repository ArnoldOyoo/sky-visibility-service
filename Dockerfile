FROM python:3.11-slim

WORKDIR /code

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app directory
COPY ./app ./app

# Set Python path
ENV PYTHONPATH=/code

EXPOSE 8000

# Run with python -m to ensure proper module resolution
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]