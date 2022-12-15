FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN python3 -m pip install --upgrade pip && pip3 install -r /app/requirements.txt --no-cache-dir

COPY . .

ADD entrypoint.sh /entrypoint.sh

RUN chmod a+x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000"]