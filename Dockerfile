FROM python:3.9.7-slim-buster
COPY . ./megalohobot
RUN pip -r requirements.txt install
CMD ["python", "./megalohobot/app.py"]
