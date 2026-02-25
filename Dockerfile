# Base image
FROM python:3.10-slim-bullseye

# Accept proxy arguments from Jenkins
ARG http_proxy
ARG https_proxy
ARG HTTP_PROXY
ARG HTTPS_PROXY

# Set proxy environment variables inside the container
ENV http_proxy=http://icache.intracomtel.com:80
ENV https_proxy=http://icache.intracomtel.com:80
ENV HTTP_PROXY=http://icache.intracomtel.com:80
ENV HTTPS_PROXY=http://icache.intracomtel.com:80

# Optional: force Debian to use HTTP instead of HTTPS (many proxies break HTTPS)
RUN sed -i 's|https://deb.debian.org|http://deb.debian.org|g' /etc/apt/sources.list && \
    sed -i 's|https://security.debian.org|http://security.debian.org|g' /etc/apt/sources.list

# Install required packages
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        python3-dev \
        libyaml-dev \
        libffi-dev \
        tk \
        tcl && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /smokeTime

# Copy your application
COPY . .

# Default command
CMD ["python3", "smokeTime.py"]
