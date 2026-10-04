FROM python:3.13-slim

RUN apt-get update &&  \
    apt-get install --no-install-recommends -y \
    git \
    gettext \
    binutils \
    libproj-dev \
    gcc `# install pre-commit` \
    gdal-bin \
    ca-certificates \
    libnss3-tools \
    p11-kit-modules && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY certs/russian-trusted-sub-ca.crt certs/russian-trusted-root-ca.crt /usr/local/share/ca-certificates/
# Chromium trusts the NSS shared DB, not the OpenSSL bundle from update-ca-certificates.
# p11-kit-trust points that DB at the system CA store.
RUN update-ca-certificates \
    && mkdir -p /root/.pki/nssdb \
    && certutil -d sql:/root/.pki/nssdb -N --empty-password \
    && modutil -dbdir sql:/root/.pki/nssdb -force -add p11-kit-trust \
        -libfile "$(find /usr/lib -name p11-kit-trust.so -print -quit)"

COPY ./pyproject.toml .
RUN pip install . && playwright install --with-deps chromium-headless-shell

WORKDIR /code
COPY . /code