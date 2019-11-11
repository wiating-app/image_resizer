import boto3
from botocore.exceptions import ClientError
import logging
import os
from PIL import Image
from resizeimage import resizeimage
import tempfile

from dotenv import load_dotenv, find_dotenv
from os import environ as env


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

S3_BUCKET = env.get('S3_BUCKET')

logging.basicConfig(level=logging.INFO)


def callback(ch, method, properties, body):
    body_string = body.decode("utf-8")
    file_name = body_string.rsplit('.', 1)[0]
    file_extension = body_string.rsplit('.', 1)[1]
    mimetype = 'image/png' if file_extension == 'png' else 'image/jpeg'
    s3_client = boto3.client('s3')
    with tempfile.TemporaryFile() as fp:
        logging.info(body_string)
        s3_client.download_fileobj(S3_BUCKET, body_string, fp)
        fp_m = tempfile.TemporaryFile()
        with Image.open(fp) as image:
            img = resizeimage.resize_contain(image, [385, 385]).convert('RGB')
            img.save(fp_m, image.format)
            fp_m.seek(0)
        s3_client.upload_fileobj(fp_m, S3_BUCKET, file_name + '_m.' + file_extension, ExtraArgs={'ACL': 'public-read', 'ContentType': mimetype})
        fp_m.close()
    logging.info(body_string)
    ch.basic_ack(delivery_tag = method.delivery_tag)

