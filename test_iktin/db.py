import psycopg2
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
cursor = conn.cursor()