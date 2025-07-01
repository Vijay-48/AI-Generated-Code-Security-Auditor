<<<<<<< HEAD
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p chroma_db && chmod 777 chroma_db

EXPOSE 8000

=======
# Stage 1: Build Python from source
FROM debian:bookworm-slim AS python-builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libssl-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Download and compile Python 3.11
RUN curl -O https://www.python.org/ftp/python/3.11.9/Python-3.11.9.tgz \
    && tar -xzf Python-3.11.9.tgz \
    && cd Python-3.11.9 \
    && ./configure --enable-optimizations \
    && make -j $(nproc) \
    && make altinstall \
    && cd .. \
    && rm -rf Python-3.11.9*

# Stage 2: Create final image
FROM debian:bookworm-slim

# Copy Python from builder
COPY --from=python-builder /usr/local/ /usr/local/

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV WORKDIR /usr/src/app
WORKDIR $WORKDIR

# Install security tools
RUN pip3.11 install --no-cache-dir bandit semgrep

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3.11 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create and set permissions for chroma_db
RUN mkdir -p chroma_db && chown -R 1000:1000 chroma_db

# Expose the application port
EXPOSE 8000

# Run the application
>>>>>>> 6beaaa9d992e786be91fc4cc04bf2dff00a41321
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]