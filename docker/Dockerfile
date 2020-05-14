FROM python:3.7-slim
ARG API_HOME=/usr/src

ADD ./requirements.txt .
RUN pip3 install -r requirements.txt

COPY app /app/
ADD wsgi.py /
WORKDIR /

EXPOSE 5000

CMD ["gunicorn", "-w", "1", "--bind", "0.0.0.0:5000", "wsgi:app"]
