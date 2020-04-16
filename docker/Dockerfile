FROM python:3.8-slim
ARG API_HOME=/usr/src

COPY . ${API_HOME}

WORKDIR ${API_HOME}

RUN pip install --upgrade pip \
    && pip install -r ${API_HOME}/requirements.txt

EXPOSE 5000
