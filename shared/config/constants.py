import os

from quarter_lib.akeyless import get_secrets

redis_pwd = get_secrets("infrastructure/celery-redis")

if os.getenv("IS_CONTAINER") == "True":
    REDIS_URL = f"redis://default:{redis_pwd}@celery-redis-master.default.svc.cluster.local:6379"
else:
    REDIS_URL = f"redis://default:{redis_pwd}@localhost:6379"
