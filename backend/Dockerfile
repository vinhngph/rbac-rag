FROM dhi.io/python:3.13.14-debian13-sfw-dev AS BUILDER

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/venv/bin:$PATH"

WORKDIR /app

RUN apt-get update && apt-get full-upgrade -y && \
    apt-get autoremove -y && \
    apt-get install -y \
    build-essential zlib1g-dev libjpeg-dev liblcms2-dev libpng-dev libfreetype-dev libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /app/venv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --------------------------------------------
FROM dhi.io/python:3.13.14-debian13 AS RUNTIME

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/venv/bin:$PATH"

WORKDIR /app

USER nonroot

COPY --from=BUILDER --chown=nonroot:nonroot /app/venv /app/venv

COPY --chown=nonroot:nonroot . .

EXPOSE 8000

CMD [ "fastapi", "run" ]
