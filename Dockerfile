FROM python:3.8.3
RUN mkdir /app
WORKDIR /app
RUN apt-get update
RUN apt-get install -y python3-pip
RUN apt-get -y update && apt-get -y install nginx
RUN pip3 install --upgrade pip
ADD requirements.txt /app/
RUN pip3 install -r requirements.txt
ADD nginx/nginx.conf /etc/nginx
ADD . /app/
RUN pip3 install -U flask-cors
RUN chmod +x ./run_flask_app.sh
ENTRYPOINT ["/bin/bash","run_flask_app.sh"]

