from dotenv import load_dotenv
load_dotenv()

from services.file_processor import FileProcessorService
from multiprocessing.spawn import freeze_support
import multiprocessing
import time

import pika.exceptions

from services.rabbitmq import RabbitMQService


service = RabbitMQService()

def consume_messages():
    while True:
        try:
            file_processor = FileProcessorService()
            service.consume("reports", file_processor.process)
            return
        except pika.exceptions.ChannelClosedByBroker as e:
            if e.reply_code == 404:
                print("Channel not found, reconnecting...")
                time.sleep(5)
        except pika.exceptions.AMQPConnectionError:
            print("Conexión perdida. Reintentando en 5 segundos...")
            time.sleep(5)

process = multiprocessing.Process(target=consume_messages)

if __name__ == "__main__":
    freeze_support()
    process.start()

