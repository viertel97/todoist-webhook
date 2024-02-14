FROM python:3.11-slim-buster
ARG PAT

COPY . .

COPY requirements.txt .

RUN pip install -r requirements.txt

ENV IS_CONTAINER=True

EXPOSE 9400
ENTRYPOINT /docker-entrypoint.sh $0 $@
CMD [ "fastapi" ]