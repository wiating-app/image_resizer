from celery import Celery
from dotenv import load_dotenv, find_dotenv
import logging
from os import environ as env

from .image_resizer import resize_image as ri


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

STORE_PROPERTY = env.get('S3_BUCKET')

logging.basicConfig(level=logging.INFO)

app = Celery('image_resizer', broker='amqp://localhost')


@app.task
def resize_image(body):
    return ri(body=body)
