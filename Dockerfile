FROM python:alpine as build
ARG PAT
RUN apk upgrade --no-cache
WORKDIR /source
COPY requirements.txt /source/
COPY docker-entrypoint.sh /source/

RUN python3 -m venv /source/venv
RUN . /source/venv/bin/activate && python3 -m ensurepip --upgrade && python3 -m pip install -r /source/requirements.txt

# Build the final image
FROM python:alpine as final
ENV IS_CONTAINER=True
RUN apk upgrade --no-cache
WORKDIR /source
COPY --from=build /source /source
ENTRYPOINT /docker-entrypoint.sh $0 $@
CMD . /source/venv/bin/activate && fastapi


