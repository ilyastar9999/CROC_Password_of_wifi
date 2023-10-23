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

def create_user(name, password, email):
    try:
        cursor.execute("""INSERT INTO users (name, password, auth, email) VALUES (%s, %s, %s, %s)""", (name, password, False, email))
        conn.commit()
        return True
    except:
        return False

def check_auth_user(username):
    sqlite3_select_query = """SELECT auth FROM users WHERE email = %s;"""
    cursor.execute(sqlite3_select_query, (username, ))
    conn.commit()
    try:
        if cursor.fetchall()[0][0]:
            return True
        else:
            return False
    except:
        return True

def auth_user(username):
    sqlite3_select_query = """Update users SET auth = true WHERE email = %s;"""
    cursor.execute(sqlite3_select_query, (username, ))
    return

def check_not_auth_user_is_exist(username):
    sqlite3_select_query = """SELECT email FROM users WHERE email =%s;"""
    cursor.execute(sqlite3_select_query, (username, ))
    conn.commit()
    return cursor.fetchall()

def create_all():
    sqlite_select_query = ["""CREATE TABLE IF NOT EXISTS marks(id SERIAL PRIMARY KEY, value INTEGER, user_id SERIAL)""", 
"""CREATE TABLE IF NOT EXISTS users(id SERIAL PRIMARY KEY, name TEXT, password TEXT, auth BOOLEAN, email TEXT UNIQUE);""",
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

def delete_all():
    sqlite_select_query = ["""DROP TABLE IF EXISTS marks;""", """DROP TABLE IF EXISTS users;""", """DROP TABLE IF EXISTS classes;"""]
    cursor.execute(sqlite_select_query[0])
    cursor.execute(sqlite_select_query[1])
    cursor.execute(sqlite_select_query[2])
    conn.commit()
    return True