# Use an official Python runtime as the base image
FROM python:3.12-slim

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the app code
COPY ./src .

# Expose port 8000 and run the command to start the application
EXPOSE 8000
CMD ["uvicorn", "main:app --host 0.0.0.0 --port 8000"]
