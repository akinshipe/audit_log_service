FROM python:3.11-slim

# Set the working directory in the container to /usr/local/src/app
WORKDIR /usr/local/src/app

# Copy the current directory contents into the container at /usr/local/src/app
COPY . /usr/local/src/app


RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Define environment variable
ENV UVICORN_HOST=0.0.0.0
ENV UVICORN_PORT=8000
ENV UVICORN_LOG_LEVEL=info

# Run uvicorn when the container launches
CMD ["uvicorn", "log_service.app_entry_point:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "warning"]
