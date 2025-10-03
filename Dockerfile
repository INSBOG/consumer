FROM python:3.11-alpine

ARG RABBITMQ_HOST
ARG RABBITMQ_USER
ARG RABBITMQ_PASS
ARG RABBITMQ_PORT
ARG SOCKET_URI

ENV RABBITMQ_HOST=$RABBITMQ_HOST
ENV RABBITMQ_USER=$RABBITMQ_USER
ENV RABBITMQ_PASS=$RABBITMQ_PASS
ENV RABBITMQ_PORT=$RABBITMQ_PORT
ENV SOCKET_URI=$SOCKET_URI

# Establecer la variable de entorno para deshabilitar el buffer de Python
ENV PYTHONUNBUFFERED=1

RUN apk update && apk add --no-cache py-pip

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["./entrypoint.sh"]