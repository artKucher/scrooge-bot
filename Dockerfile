FROM python:3.13-slim

RUN apt-get update &&  \
    apt-get install --no-install-recommends -y \
    git \
    gettext \
    binutils \
    libproj-dev \
    gcc `# install pre-commit` \
    gdal-bin && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY ./pyproject.toml .
RUN pip install . && playwright install-deps chromium-headless-shell && playwright install chromium-headless-shell

WORKDIR /code
COPY . /code