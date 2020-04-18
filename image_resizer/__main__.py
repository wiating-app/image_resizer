from celery import Celery
from dotenv import load_dotenv, find_dotenv
import logging
from os import environ as env

from .image_resizer import LocalFile, S3File


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

STORE_PROPERTY = env.get('S3_BUCKET')

logging.basicConfig(level=logging.INFO)

QUEUE_NAME = env.get('IMAGE_RESIZER_QUEUE')

app = Celery(QUEUE_NAME, broker='amqp://localhost')

@app.task
def resize_image(body):
    body_string = body.decode("utf-8")
    store_property = STORE_PROPERTY.split('//', 1)[1]

    if STORE_PROPERTY.startswith('file://'):
        thumbnail = LocalFile(body_string=body_string, path=store_property)
    elif STORE_PROPERTY.startswith('s3://'):
        thumbnail = S3File(body_string=body_string, bucket=store_property)

    try:
        thumbnail.get_file()
        thumbnail.save_thumbnail()
        logging.info(body_string)
    except IOError: # in case of input file malfunction
        logging.info("File broken " + body_string)
