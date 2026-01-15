FROM python:3.11-slim-bullseye

# Install system dependencies for WeasyPrint (GTK+, fonts, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-liberation \
    fonts-dejavu \
    libffi-dev \
    libgdk-pixbuf2.0-0 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgobject-2.0-0 \
    libcairo2 \
    libexpat1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir .

# Create export directory
RUN mkdir -p /app/exports

# Set entry point
CMD ["jasper", "interactive"]
