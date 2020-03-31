# Use an official Python runtime as a parent image
FROM python:3.7

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY './requirements.txt' /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

COPY . .

# Make port 80 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
ENTRYPOINT ["python", "IDFCarpoolServer.py"]
