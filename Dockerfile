# Start from official Python image
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install all libraries
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of your code
COPY . .

# Tell Docker your app runs on port 5000
EXPOSE 5000

# Command to run your app
CMD ["python", "app.py"]