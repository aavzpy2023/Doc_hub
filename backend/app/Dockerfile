# --- Stage 1: Build Stage ---
# Use a full Python image to build dependencies, which may require build tools.
FROM python:3.11-slim-bookworm AS builder

# Install system-level dependencies required for building Python packages and for runtime.
# Using --no-install-recommends reduces image size.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    pandoc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/venv
# Create a virtual environment
RUN python -m venv .

# Activate the virtual environment for subsequent commands
ENV PATH="/opt/venv/bin:$PATH"

# Copy only the requirements file first to leverage Docker layer caching.
# If requirements.txt doesn't change, this layer won't be rebuilt.
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Final Stage ---
# Use a minimal base image for the final product to reduce size and attack surface.
FROM python:3.11-slim-bookworm AS final

# Install only the necessary runtime system dependencies.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    pandoc \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment with pre-installed packages from the builder stage.
COPY --from=builder /opt/venv /opt/venv

WORKDIR /code

# Copy the application source code.
# This is one of the last steps, so changes here won't invalidate the dependency layers.
COPY ./app /code/app

# Activate the virtual environment in the final image.
ENV PATH="/opt/venv/bin:$PATH"

# Expose the port the application will run on.
EXPOSE 8000

# The command to run the FastAPI application.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]