FROM debian:bookworm

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && apt-get install -y curl git python3-pip python3-setuptools python3-dev zlib1g-dev libjpeg-dev

RUN mkdir -p /opt/image_resizer
RUN mkdir -p /images

COPY requirements.txt .

RUN pip3 install --break-system-packages -r requirements.txt

WORKDIR /opt/image_resizer
RUN chmod -R g+rwx ./
