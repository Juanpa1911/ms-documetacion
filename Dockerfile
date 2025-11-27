FROM python:3.12-slim

ENV FLASK_CONTEXT=production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH=$PATH:/home/flaskapp/.venv/bin

# Instalar dependencias del sistema para WeasyPrint (GTK/Pango) - Solo necesario en Linux
RUN apt-get update && apt-get install -y \
    build-essential \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --home-dir /home/flaskapp flaskapp

WORKDIR /home/flaskapp

USER flaskapp

ADD https://astral.sh/uv/install.sh ./uv-installer.sh
RUN sh ./uv-installer.sh && rm ./uv-installer.sh

COPY ./pyproject.toml ./uv.lock ./
RUN uv sync --locked

COPY ./app ./app
COPY ./wsgi.py .

RUN chown -R flaskapp:flaskapp /home/flaskapp

ENV VIRTUAL_ENV="/home/flaskapp/.venv"

EXPOSE 5000

CMD ["granian", "--interface", "wsgi", "wsgi:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "4"]
