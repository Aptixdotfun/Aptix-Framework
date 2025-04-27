FROM python:3.10-slim
WORKDIR /AptixBot

# Copy requirements first for better layer caching
COPY requirements.txt /AptixBot/

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /AptixBot/

# Create non-root user for security
RUN groupadd -r aptix && useradd -r -g aptix aptix \
    && chown -R aptix:aptix /AptixBot
USER aptix

# Expose ports
EXPOSE 6185 
EXPOSE 6186

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:6185/health || exit 1

# Set entrypoint
CMD [ "python", "main.py" ]
