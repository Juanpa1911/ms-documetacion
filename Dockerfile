FROM python:3.13.7-slim

ENV FLASK_CONTEXT=production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/home/flaskapp/.venv/bin:$PATH

RUN useradd --create-home --home-dir /home/flaskapp flaskapp

# Dividir instalación de dependencias para reducir uso de memoria
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /home/flaskapp

# Instalar uv como root, luego cambiar permisos
ADD https://astral.sh/uv/install.sh /tmp/uv-installer.sh
RUN chmod +x /tmp/uv-installer.sh && \
    /tmp/uv-installer.sh && \
    rm /tmp/uv-installer.sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv && \
    mv /root/.local/bin/uvx /usr/local/bin/uvx

USER flaskapp

COPY --chown=flaskapp:flaskapp ./pyproject.toml ./uv.lock ./
RUN uv sync --locked

COPY --chown=flaskapp:flaskapp ./app ./app
COPY --chown=flaskapp:flaskapp ./wsgi.py .

EXPOSE 5000
CMD ["/home/flaskapp/.venv/bin/granian", "--interface", "wsgi", "wsgi:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "4", "--blocking-threads", "4", "--backlog", "2048", "--http", "auto"]