import psycopg2
import json
#import sqlite3

config_file = open("config.json")
config_data = json.load(config_file)
host = config_data["db_host"]
port = config_data["db_port"]
user = config_data["db_user"]
database = config_data["db_name"]
password = config_data["db_pass"]

conn = psycopg2.connect(
    host=host,
    port=port,
    database=database,
    user=user,
    password=password
)

#conn = sqlite3.connect('db.sql')

cursor = conn.cursor()

conn.rollback()

def parse_data(field):
    file = open("config.json")
    data = json.load(file)[field]

    return data

def create_all():
    sqlite_select_query = ["""CREATE TABLE IF NOT EXISTS marks(id SERIAL PRIMARY KEY, value INTEGER, user_id SEREAL)""", 
"""CREATE TABLE IF NOT EXISTS users(id SERIAL PRIMARY KEY, name TEXT, surname TEXT, password TEXT, auth BOOLEAN, email TEXT UNIQUE);""",
"""CREATE TABLE IF NOT EXISTS classes(id SERIAL PRIMARY KEY, name TEXT, members );"""]
    cursor.execute(sqlite_select_query[0])
    cursor.execute(sqlite_select_query[1])
    conn.commit() 
    try:
        create_user("admin", "silaederprojects@gmail.com", parse_data("secret_key"), "Admin", "Adminovich")
        auth_user('admin')
    except:
        pass
    return