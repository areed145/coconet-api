FROM python:3.7-slim-buster

LABEL maintainer="areed145@gmail.com"

WORKDIR /web-app

COPY . /web-app

# We copy just the requirements.txt first to leverage Docker cache
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

#ENV MONGODB_CLIENT 'mongodb://kk6gpv:kk6gpv@mongo-mongodb-replicaset-0.mongo-mongodb-replicaset.default.svc.cluster.local,mongo-mongodb-replicaset-1.mongo-mongodb-replicaset.default.svc.cluster.local,mongo-mongodb-replicaset-2.mongo-mongodb-replicaset.default.svc.cluster.local/?replicaSet=db'
ENV MONGODB_CLIENT 'mongodb+srv://kk6gpv:kk6gpv@cluster0-kglzh.azure.mongodb.net/test?retryWrites=true&w=majority'
ENV MAPBOX_TOKEN 'pk.eyJ1IjoiYXJlZWQxNDUiLCJhIjoiY2phdzNsN2ZoMGh0bjMybzF3cTkycWYyciJ9.4aS7z-guI2VDlP3duMg2FA'
ENV SID 'KTXHOUST1941'
ENV PORT 80
ENV DEBUG_MODE 0

EXPOSE 80

CMD ["gunicorn", "app:app", "--config=config.py"]
#CMD ["python", "app.py"]