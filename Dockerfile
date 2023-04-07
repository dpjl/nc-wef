FROM python:3.9.16-alpine3.17

WORKDIR /app

COPY requirements.txt ./
RUN apk add --update --no-cache git && pip install --no-cache-dir -r requirements.txt && apk del git

COPY main.py .
COPY watcher ./watcher

CMD [ "python", "./main.py" ]