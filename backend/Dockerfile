FROM dhi.io/python:3.13-debian13-sfw-dev

WORKDIR /app

RUN apt-get update && apt-get full-upgrade -y && \
    apt-get autoremove -y && \
    apt-get install build-essential zlib1g-dev libjpeg-dev liblcms2-dev libpng-dev libfreetype-dev libwebp-dev -y

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "fastapi", "run", "--host", "0.0.0.0" ]