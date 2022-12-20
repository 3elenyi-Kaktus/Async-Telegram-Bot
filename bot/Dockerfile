FROM python:latest

WORKDIR ./my_bot

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./bot/code ./app

ENV TELEGRAM_TOKEN ${TELEGRAM_TOKEN}

CMD ["python", "./app/main.py"]
