# Dockerfile

# --- Stage 1: Build Stage ---
FROM python:3.12-slim as builder

# Set the working directory inside the container
WORKDIR /app

# Install build dependencies required for some Python packages
RUN apt-get update && apt-get install -y build-essential libpq-dev

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies into a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt


# --- Stage 2: Final Stage ---
# Use a smaller, non-root base image for the final application for better security
FROM python:3.12-slim as final

# Set the working directory
WORKDIR /app

# Copy the virtual environment with installed dependencies from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy the application code into the container
COPY . .

# Set the PATH to include the venv, so we can run the app directly
ENV PATH="/opt/venv/bin:$PATH"

# Expose the port the app runs on
EXPOSE 8080

# The command to run the application using a production-grade WSGI server (Gunicorn)
RUN useradd --create-home appuser
USER appuser
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "run:flask_app"]