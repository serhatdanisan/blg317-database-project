FROM python:latest

COPY requirements.txt requirements.txt
COPY .env .env
RUN pip install --no-cache-dir -r requirements.txt

COPY app app

EXPOSE 5000

CMD ["python", "/app/run.py"]

