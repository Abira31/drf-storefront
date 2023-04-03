FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /storefront
WORKDIR /storefront
COPY ./requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt