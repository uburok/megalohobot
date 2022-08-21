FROM python:3.10.0-alpine3.14
WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
RUN mkdir /opt/megalohobot/

CMD ["python", "./app.py"]

LABEL how_to_build = "docker build -t megalohobot ."
LABEL how_to_run = "docker run -d --restart=always -v /opt/megalohobot:/opt/megalohobot --name megalohobot megalohobot"
