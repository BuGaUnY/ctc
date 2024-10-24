# Use the official Python image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "projectmanager.wsgi:application", "--bind", "0.0.0.0:8000"]
