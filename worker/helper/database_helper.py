from quarter_lib.akeyless import get_target
from sqlalchemy import create_engine

DB_USER_NAME, DB_HOST_NAME, DB_PASSWORD, DB_PORT, DB_NAME = get_target("private")


def create_sqlalchemy_engine():
	return create_engine(f"mysql+pymysql://{DB_USER_NAME}:{DB_PASSWORD}@{DB_HOST_NAME}:{DB_PORT}/{DB_NAME}")
