import boto3
import os
from PIL import Image
from resizeimage import resizeimage
import tempfile



class GenericFile:
    def __init__(self, body_string):
        self._body_string = body_string
        self._thumbnail_name, self._mimetype = self.parse_filename(self._body_string)
        self._full_handler = None
        self._thumbnail_handler = None

    def __del__(self):
        self._full_handler.close()

    def get_file(self):
        pass

    def save_thumbnail(self):
        pass

    @staticmethod
    def parse_filename(body_string):
        file_name = body_string.rsplit('.', 1)[0]
        file_extension = body_string.rsplit('.', 1)[1]
        thumbnail_name = file_name + '_m.' + file_extension
        mimetype = 'image/png' if file_extension == 'png' else 'image/jpeg'
        return thumbnail_name, mimetype

    def resize_image(self):
        with Image.open(self._full_handler) as image:
            img = resizeimage.resize_thumbnail(image, [385, 385]).convert('RGB')
            img.save(self._thumbnail_handler, image.format)
            self._thumbnail_handler.seek(0)


class LocalFile(GenericFile):
    def __init__(self, body_string, path):
        self._path = path
        super().__init__(body_string=body_string)

    def get_file(self):
        self._full_handler = open(os.path.join(self._path, self._body_string), 'rb')

    def save_thumbnail(self):
        with open(os.path.join(self._path, self._thumbnail_name), 'wb') as self._thumbnail_handler:
            self.resize_image()


class S3File(GenericFile):
    def __init__(self, body_string, bucket):
        self._bucket = bucket
        self._s3_client = boto3.client('s3')
        super().__init__(body_string=body_string)

    def get_file(self):
        self._full_handler = tempfile.TemporaryFile()
        self._s3_client.download_fileobj(self._bucket, self._body_string, self._full_handler)

    def save_thumbnail(self):
        with tempfile.TemporaryFile() as self._thumbnail_handler:
            self.resize_image()
            self._s3_client.upload_fileobj(self._thumbnail_handler, self._bucket, self._thumbnail_name,
                                           ExtraArgs={'ACL': 'public-read', 'ContentType': self._mimetype})
