FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

COPY . /usr/src/flask

RUN pip3 install --user -r /usr/src/flask/requirements.txt

CMD ["pyhton", "app.py"]