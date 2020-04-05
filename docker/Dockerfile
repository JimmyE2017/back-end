FROM python:3.8
ARG API_HOME=/usr/src/app

ADD . ${API_HOME}
WORKDIR ${API_HOME}
EXPOSE 5000
RUN pip install --upgrade pip \
    && pip install -r ${API_HOME}/requirements.txt
