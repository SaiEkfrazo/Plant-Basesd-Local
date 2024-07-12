# FROM python:3.9

# # Set environment variables
# ENV PYTHONUNBUFFERED 1
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV vin_env 1

# # Set the working directory in the container
# WORKDIR /app

# # Copy the local code to the container image
# COPY . /app

# # Install any needed packages specified in requirements.txt
# RUN pip install --upgrade pip && \
#     pip install -r requirements.txt && \
#     pip install gunicorn daphne

# # Expose port 8000
# EXPOSE 8000

# # Define a command to start the Django application with daphne
# CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "vin.asgi:application"]


FROM python:3.9

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV vin_env 1

# Set the working directory in the container
WORKDIR /app

# Copy the local code to the container image
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn daphne celery redis

# Expose port 8000
EXPOSE 8000

# Define a command to start the Django application with daphne
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "vin.asgi:application"]
