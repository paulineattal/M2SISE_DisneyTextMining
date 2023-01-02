FROM python:3.9-slim
RUN apt-get update
RUN apt-get install nano

RUN mkdir wd
WORKDIR wd
COPY requirements.txt ./requirements.txt
RUN pip3 install -U pip
RUN pip3 install -U wheel
RUN pip3 install -U setuptools
RUN pip3 install -r requirements.txt
COPY . ./
 
CMD [ "gunicorn", "--workers=5", "--threads=1", "-b 0.0.0.0:80", "app:server"]
