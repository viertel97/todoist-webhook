from quarter_lib.akeyless import get_target
import pymysql

DB_USER_NAME, DB_HOST_NAME, DB_PASSWORD, DB_PORT, DB_NAME = get_target("private")


def create_server_connection():
	return pymysql.connect(
		user=DB_USER_NAME,
		host=DB_HOST_NAME,
		password=DB_PASSWORD,
		port=int(DB_PORT),
		database=DB_NAME,
		cursorclass=pymysql.cursors.DictCursor,
	)

def close_server_connection(connection):
	connection.close()