# Use the Python 3.11 slim base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the script into the container
COPY update_dns.py /app

# Install the required libraries
RUN pip install --no-cache-dir requests schedule

# Run the script
CMD ["python", "update_dns.py"]