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
print('sucsessful connect to db')
#conn = sqlite3.connect('db.sql')

cursor = conn.cursor()

conn.rollback()

def parse_data(field):
    file = open("config.json")
    data = json.load(file)[field]

    return data

def get_all_users():
    query = """SELECT * FROM users;"""
    cursor.execute(query)
    conn.commit()
    return cursor.fetchall()

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
    sqlite_select_query = ["""CREATE TABLE IF NOT EXISTS marks(id SERIAL PRIMARY KEY, value INTEGER, email TEXT, subject INTEGER, name TEXT);""",  
"""CREATE TABLE IF NOT EXISTS users(id SERIAL PRIMARY KEY, name TEXT, password TEXT, auth BOOLEAN, email TEXT UNIQUE);""",
"""CREATE TABLE IF NOT EXISTS classes(id SERIAL PRIMARY KEY, name TEXT, password TEXT, members TEXT ARRAY, homework TEXT, teachers TEXT ARRAY);"""]
    cursor.execute(sqlite_select_query[0])
    cursor.execute(sqlite_select_query[1])
    cursor.execute(sqlite_select_query[2])
    conn.commit() 
    try:
        create_user("Admin Adminovich", parse_data("secret_key"), "schoolsilaeder@gmail.com")
        auth_user('schoolsilaeder@gmail.com')
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

def get_is_user_logged_in(username, password):
    sqlite3_select_query = """SELECT auth FROM users WHERE email=%s AND password=%s;"""
    cursor.execute(sqlite3_select_query, (username, password, ))
    conn.commit()
    ans = cursor.fetchall()
    print(ans)
    if ans != []:
        return ans[0]
    else:
        return False
    
def get_homework(username):
    sqlite3_select_query = """SELECT name, homework FROM classes WHERE %s = ANY(members);"""
    cursor.execute(sqlite3_select_query, (username, ))
    conn.commit()
    return cursor.fetchall()

def get_marks(username):
    sqlite3_select_query = """SELECT subject, value FROM marks WHERE email = %s;"""
    cursor.execute(sqlite3_select_query, (username, ))
    conn.commit()
    ans = cursor.fetchall()
    ans1 = {}
    for i in ans:
        if i[0] in ans1.keys():
            ans1[i[0]] = [i[1]]
        else:
            ans1[i[0]].append(i[1])
    return ans1

def get_name(email):
    sqlite3_select_query = """SELECT name FROM users WHERE email = %s;"""
    cursor.execute(sqlite3_select_query, (email, ))
    conn.commit()
    return cursor.fetchall()[0][0]

def get_classes_by_teacher(email):
    if email == "schoolsilaeder@gmail.com":
        sqlite3_select_query = """SELECT name FROM classes;"""
        cursor.execute(sqlite3_select_query)
    else:
        sqlite3_select_query = """SELECT name FROM classes WHERE %s = ANY(teachers);"""
        cursor.execute(sqlite3_select_query, (email, ))
    conn.commit()
    return cursor.fetchall()

def get_class_by_id(id):
    sqlite3_select_query = """SELECT * FROM classes WHERE id = %s;"""
    cursor.execute(sqlite3_select_query, (id, ))
    conn.commit()
    return cursor.fetchall()

def create_class(class_name, password, teacher_email):
    try:
        sqlite3_select_query = """INSERT INTO classes (name, password, teachers) VALUES (%s, %s, %s);"""
        cursor.execute(sqlite3_select_query, (class_name, password, [teacher_email], ))
        conn.commit()
        return True
    except:
        return False
    
def is_class_exists(id):
    sqlite3_select_query = """SELECT * FROM classes WHERE id = %s;"""
    cursor.execute(sqlite3_select_query, (id, ))
    conn.commit()
    if cursor.fetchall() != []:
        return True
    else:
        return False

def check_class_password(id, password):
    sqlite3_select_query = """SELECT password FROM classes WHERE id = %s;"""
    cursor.execute(sqlite3_select_query, (id, ))
    conn.commit()
    if cursor.fetchall()[0][0] == password:
        return True
    else:
        return False

def add_class_member(id, email):
    try:
        sqlite3_select_query  = """SELECT ARRAY_APPEND(members, %s) FROM classes WHERE id = %s;"""
        cursor.execute(sqlite3_select_query, (email, id, ))
        conn.commit()
        return True
    except:
        return False

def get_user_by_email(email):
    sqlite3_select_query = """SELECT * FROM users WHERE email = %s;"""
    cursor.execute(sqlite3_select_query, (email, ))
    conn.commit()
    return cursor.fetchall()

def update_homework(id, text):
    try:
        sqlite3_select_query = """UPDATE classes SET homework = %s WHERE id = %s;"""
        cursor.execute(sqlite3_select_query, (id, ))
        conn.commit()
        return True
    except:
        return False

def is_user_exists(email):
    sqlite3_select_query = """SELECT * FROM users WHERE email = %s;"""
    cursor.execute(sqlite3_select_query, (email, ))
    conn.commit()
    if cursor.fetchall() != []:
        return True
    else:
        return False
    
def add_teacher(id, email):
    try:
        sqlite3_select_query = """SELECT ARRAY_APPEND(teachers, %s) FROM classes WHERE id = %s;"""
        cursor.execute(sqlite3_select_query, (email, ))
        conn.commit()
        return True
    except:
        return False

def get_marks_by_class(id_class):
    query = """SELECT members FROM classes WHERE id = %s;"""
    cursor.execute(query, (id_class, ))
    conn.commit()
    members = cursor.fetchall()
    query = """SELECT name FROM marks WHERE subject = %s ORDER BY name;"""
    ans = [''] + cursor.fetchall()
    for i in range(len(members)):
        query = """SELECT value FROM marks WHERE class_id = %s AND email = %s ORDER BY name;"""
        cursor.execute(query, (id_class, members[i], ))
        conn.commit()
        ans.append([members[i]] + cursor.fetchall())
    return ans

#DEBUG
print(get_all_users())