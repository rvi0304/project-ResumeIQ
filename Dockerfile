FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

COPY . .

ENV PORT 8080
EXPOSE 8080

CMD gunicorn --bind 0.0.0.0:$PORT app:app
