 .#python:3.10-slim
FROM python:3.10-slim

WORKDIR /smokeTime

# Install build tools required for PyYAML and other packages 
#RUN apt-get update && apt-get install -y \ build-essential \ python3-dev \ libyaml-dev \ && rm -rf /var/lib/apt/lists/*

#RUN apt-get update && apt-get install -y \
#    build-essential \
#    python3-dev \
#    libyaml-dev \
#    && rm -rf /var/lib/apt/lists/*

#RUN apt-get update && apt-get install -y \
#    build-essential \
#    python3-dev \
#    libyaml-dev \
#    libffi-dev \
#    && rm -rf /var/lib/apt/lists/*

#RUN apt-get update && apt-get install -y \
#    tk \
#    tcl \
#    libx11-6 \
#    libxext6 \
#    libxrender1 \
#    libxft2 \
#    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libyaml-dev \
    libffi-dev \
    tk \
    tcl \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .

#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir --disable-pip-version-check --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org -r requirements.txt

COPY . .

CMD ["python", "smokeTime.py"]


