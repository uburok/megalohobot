FROM python:3.10.0-alpine3.14
WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

VOLUME /var/lib/
CMD ["python", "./app.py"]
