FROM python:3.9.7-slim-buster
COPY . ./app
RUN pip -r requirements.txt install
CMD ["python", "./app.py"]
