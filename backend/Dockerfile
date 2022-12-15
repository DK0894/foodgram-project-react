FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip3 install --upgrade pip && pip3 install -r /app/requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000" ]