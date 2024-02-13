Based on tacnchinhiong's [decoupled-celery-example](https://github.com/tanchinhiong/decoupled-celery-example)
# Decoupled Celery & FastAPI example + Helm Deployment


This repo is an example of how the [Celery](https://docs.celeryproject.org/en/stable/) application and Celery worker can be decoupled and executed in different containers.


## Deployment
In the helm-chart (cd-folder) i am using two deployment yaml's which use the same container and differentiate by their starting command.
The first deployment is the celery worker which is responsible for the database handling and the other one is the celery application + FastAPI to receive the webhooks.