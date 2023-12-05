# pull official base image
FROM alpine:3.18

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1



# install system dependencies
RUN apk add --no-cache postgresql-dev gcc python3 python3-dev musl-dev libffi-dev socat openssh-client curl
RUN apk add build-base
RUN apk add git

# install dependencies
RUN python3 -m ensurepip
RUN rm -r /usr/lib/python*/ensurepip
RUN pip3 install --upgrade pip setuptools
RUN rm -r /root/.cache

RUN pip3 install poetry

COPY ./poetry.lock .
COPY ./pyproject.toml .
RUN poetry config virtualenvs.create false
RUN poetry install

# COPY ./requirements.txt .
# RUN pip3 install -r requirements.txt

# copy build.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
