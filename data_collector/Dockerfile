# Get python image v.3.8.6
FROM python:3.8.6

# Create container app directory
WORKDIR /usr/src/app

# Copy file and install app dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents to container
COPY . /usr/src/app

# Copy config file from main directory
COPY ../config_file.ini /usr/src/app

# Expose port for postgresql connection
EXPOSE 8000

# Start app
CMD ["python", "-u", "main.py"]