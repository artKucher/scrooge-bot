FROM python:3.13-slim

RUN apt-get update &&  \
    apt-get install --no-install-recommends -y \
    git \
    gettext \
    binutils \
    libproj-dev \
    gcc `# install pre-commit` \
    gdal-bin \
    ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY certs/russian-trusted-sub-ca.crt certs/russian-trusted-root-ca.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates

COPY ./pyproject.toml .
RUN pip install . && playwright install --with-deps chromium-headless-shell

WORKDIR /code
COPY . /code