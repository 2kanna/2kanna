# Use an official Python runtime as the base image
FROM python:3.11 as builder

# Set the working directory in the container
WORKDIR /app

# Set environment variables to avoid creating .pyc files and ensure output is unbuffered
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install the dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libmariadb-dev 

# Copy the required files into the container
COPY ./requirements.txt ./

# Build the wheel repository
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# Use a slim image for the final stage
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    procps

# Copy the wheels and requirements file from the builder stage
COPY --from=builder /wheels /wheels
COPY --from=builder /app/requirements.txt .

COPY ./setup.cfg ./pyproject.toml ./

# Install the dependencies from the wheels
RUN pip install --no-cache /wheels/*

# Copy the application code into the container
COPY ./src ./src

# Install the python package
RUN pip install --no-cache-dir .
