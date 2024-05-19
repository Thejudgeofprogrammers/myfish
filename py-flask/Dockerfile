FROM python:3.10.14-alpine3.19

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./templates ./templates
COPY ./static ./static
COPY ./src ./src
COPY ./server.py ./

CMD [ "python", "./server.py" ]

# Собираем образ нашего приложения и выполняем скачивание всех нужных библиотек для его работы