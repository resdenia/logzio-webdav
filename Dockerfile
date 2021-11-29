FROM python:3
WORKDIR /usr/var/app
RUN apt-get update -y
RUN apt-get install -y python
RUN apt-get install python3-pip -y
RUN pip3 install webdavclient3
# COPY ./requirements.txt ./requirements.txt
COPY ./ ./
RUN pip3 install --no-cache-dir -r requirements.txt
CMD [ "python3", "-u", "/usr/var/app/watcher.py" ]
