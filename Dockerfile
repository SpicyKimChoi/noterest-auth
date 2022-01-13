FROM python:3.9

ADD requirements.txt .
RUN python -m pip install --upgrade pip \
    && pip install --trusted-host pypi.python.org -r requirements.txt