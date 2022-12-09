FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app

RUN python3 -m pip install --upgrade pip

RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY ./ /app

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8002"]