FROM python:3.7.4-alpine
  
WORKDIR /app

COPY . /app

RUN apk add --no-cache --virtual .build-deps gcc musl-dev python3-dev libffi-dev openssl-dev \
     && pip install -r requirements.txt \
     && apk del .build-deps gcc musl-dev python3-dev libffi-dev openssl-dev

HEALTHCHECK --interval=15s --timeout=3s \
 CMD curl -f http://localhost:${PORT}/ || exit 1

CMD gunicorn --bind 0.0.0.0:${PORT} --workers ${GUNICORN_NUM_WORKERS} --threads ${GUNICORN_NUM_THREADS} run:app
