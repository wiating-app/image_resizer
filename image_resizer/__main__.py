from .image_resizer import callback
from dotenv import load_dotenv, find_dotenv
from os import environ as env
from rabbit_queue import RabbitQueue


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

QUEUE_NAME = env.get('IMAGE_RESIZER_QUEUE')

iq = RabbitQueue(QUEUE_NAME)
iq.consume(callback)

