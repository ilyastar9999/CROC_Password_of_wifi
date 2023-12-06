import psycopg2
import json
import time
import locale
from datetime import datetime
#import sqlite3

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

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
        conn.rollback()
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
        conn.rollback()
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
    sqlite_select_query = ["""CREATE TABLE IF NOT EXISTS marks(id SERIAL PRIMARY KEY, value TEXT, email TEXT, class_id TEXT, name INTEGER);""",  
"""CREATE TABLE IF NOT EXISTS users(id SERIAL PRIMARY KEY, name TEXT, password TEXT, auth BOOLEAN, email TEXT UNIQUE);""",
"""CREATE TABLE IF NOT EXISTS classes(id SERIAL PRIMARY KEY, name TEXT, password TEXT, members TEXT ARRAY, homework TEXT, homework_date TEXT, teachers TEXT ARRAY, names TEXT ARRAY);"""]
    cursor.execute(sqlite_select_query[0])
    cursor.execute(sqlite_select_query[1])
    cursor.execute(sqlite_select_query[2])
    conn.commit() 
    create_user("Admin Adminovich", parse_data("secret_key"), "schoolsilaeder@gmail.com")
    auth_user('schoolsilaeder@gmail.com')
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
        if username == 'schoolsilaeder@gmail.com':
            return True
        return ans[0][0]
    else:
        return False
    
def get_homework(username):
    if username == "schoolsilaeder@gmail.com":
        sqlite3_select_query = """SELECT name, homework FROM classes;"""
        cursor.execute(sqlite3_select_query)
        conn.commit()
        return cursor.fetchall()
    sqlite3_select_query = """SELECT name, homework FROM classes WHERE %s = ANY(members);"""
    cursor.execute(sqlite3_select_query, (username, ))
    conn.commit()
    return cursor.fetchall()

def get_marks(username):
    if username == "schoolsilaeder@gmail.com":
        sqlite3_select_query = """SELECT class_id, value FROM marks;"""
        cursor.execute(sqlite3_select_query)
        conn.commit()
    else:
        sqlite3_select_query = """SELECT class_id, value FROM marks WHERE email = %s;"""
        cursor.execute(sqlite3_select_query, (username, ))
        conn.commit()
    ans = cursor.fetchall()
    ans1 = {}
    for i in ans:
        name = get_name_of_class(i[0])
        if name == False:
            continue
        try:
            ans1[name].append(i[1])
        except:
            ans1[name] = [i[0]]
    print(ans1)
    return ans1

def get_name(email):
    sqlite3_select_query = """SELECT name FROM users WHERE email = %s;"""
    cursor.execute(sqlite3_select_query, (email, ))
    conn.commit()
    ans = cursor.fetchall()
    if ans != []:
        return ans[0][0]
    return False

def get_classes_by_teacher(email):
    if email == "schoolsilaeder@gmail.com":
        sqlite3_select_query = """SELECT name, id FROM classes;"""
        cursor.execute(sqlite3_select_query)
    else:
        sqlite3_select_query = """SELECT name, id FROM classes WHERE %s = ANY(teachers);"""
        cursor.execute(sqlite3_select_query, (email, ))
    conn.commit()
    a = cursor.fetchall()
    print(a)
    return a

def get_class_by_id(id):
    sqlite3_select_query = """SELECT * FROM classes WHERE id = %s;"""
    cursor.execute(sqlite3_select_query, (id, ))
    conn.commit()
    return cursor.fetchall()

def create_class(class_name, password, teacher_email):
    try:
        now = datetime.now()
        sqlite3_select_query = """INSERT INTO classes (name, password, teachers, homework_date) VALUES (%s, %s, %s, %s);"""
        cursor.execute(sqlite3_select_query, (class_name, password, [teacher_email], f'{str(now.day)}.{str(now.month)}.{str(now.year)}', ))
        conn.commit()
        return True
    except:
        conn.rollback()
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
        sqlite3_select_query  = """UPDATE classes SET members = array_append(members, %s) WHERE id = %s;"""
        cursor.execute(sqlite3_select_query, (email, id, ))
        conn.commit()
        return True
    except:
        conn.rollback()
        return False

def get_user_by_email(email):
    sqlite3_select_query = """SELECT * FROM users WHERE email = %s;"""
    cursor.execute(sqlite3_select_query, (email, ))
    conn.commit()
    return cursor.fetchall()

def update_homework(id, text):
    try:
        now = datetime.now()
        sqlite3_select_query = """UPDATE classes SET homework = %s, homework_date = %s WHERE id = %s;"""
        cursor.execute(sqlite3_select_query, (text, f'{str(now.day)}.{str(now.month)}.{str(now.year)}', id, ))
        conn.commit()
        return True
    except:
        conn.rollback()
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
        sqlite3_select_query = """UPDATE classes SET teachers = array_append(teachers, %s) WHERE id = %s;"""
        cursor.execute(sqlite3_select_query, (email, id, ))
        conn.commit()
        return True
    except:
        conn.rollback()
        return False

def get_marks_by_class(id_class):
    query = """SELECT members FROM classes WHERE id = %s;"""
    cursor.execute(query, (id_class, ))
    conn.commit()
    aaa = cursor.fetchall()[0][0]
    if aaa == None:
        return [], []
    members = [[get_name(i), i] for i in aaa]
    print(members)
    query = """SELECT names FROM classes WHERE id = %s;"""
    cursor.execute(query, (id_class, ))
    conn.commit()
    fetchal = list(cursor.fetchall()[0])
    print(fetchal, 'fdsakjhgfcx')
    if fetchal == [None]:
        print([[members[i][0]] for i in range(len(members))])
        return ['Student'], [[members[i][0]] for i in range(len(members))]
    names = ['Student'] + fetchal[0]
    ans = []
    for i in range(len(members)):
        print(members[i][0])
        query = """SELECT value, name FROM marks WHERE class_id = %s AND email = %s ORDER BY name;"""
        cursor.execute(query, (id_class, members[i][1], ))
        conn.commit()
        a = [list(i) for i in cursor.fetchall()]
        print(a, 'iuygfd')
        if a == []:
            print('fix')
            for j in range(len(names)-1):
                query = """INSERT INTO marks (class_id, name, email, value) VALUES (%s, %s, %s, %s);"""
                cursor.execute(query, (id_class, j, members[i][1], '', ))
                conn.commit()
            ans.append([members[i][0]] + [''] * (len(names)-1))
            continue
        b = []
        for k in range(0, len(a)):
            if a[k][1] == k:
                b.append(a[k][0])
            else:
                b.append('')
        print(names)
        ans.append([members[i][0]] + b)
    return names, ans

def change_password(email, password):
    query = """UPDATE users SET password = %s WHERE email=%s;"""
    cursor.execute(query, (password, email, ))
    conn.commit()
    return

def get_topics_of_marks(id):
    query = """SELECT name FROM marks WHERE class_id=%s;"""
    cursor.execute(query, (id, ))
    conn.commit()
    return list(set(cursor.fetchall()))

def is_student_in_class(id, email):
    if email == 'schoolsilaeder@gmail.com':
        return True
    query = """SELECT id FROM classes WHERE id = %s AND %s = ANY(members);"""
    cursor.execute(query, (id, email, ))
    conn.commit()
    return cursor.fetchall() != []

def is_teacher_in_class(id, email):
    if email == 'schoolsilaeder@gmail.com':
        return True
    query = """SELECT id FROM classes WHERE id = %s AND %s = ANY(teachers);"""
    cursor.execute(query, (id, email, ))
    conn.commit()
    return cursor.fetchall() != []

def get_class_members(id):
    query = """SELECT members FROM classes WHERE id = %s;"""
    cursor.execute(query, (id, ))
    conn.commit()
    return cursor.fetchall()

def is_mark_exsist(id, name, email):
    query = """SELECT id FROM marks WHERE class_id = %s AND name = %s AND email = %s;"""
    cursor.execute(query, (id, name, email, ))
    conn.commit()
    return cursor.fetchall() 

def update_marks(id, a, names):
    print(a)
    query = """UPDATE classes SET names = %s WHERE id = %s;"""
    cursor.execute(query, (names, id, ))
    conn.commit()
    members = get_class_members(id)
    for j in range(len(a)):
        for i in range(len(a[j])):
            print()
            ans = is_mark_exsist(id, j, members[0][0][i])
            if ans == []:
                query = """INSERT INTO marks (class_id, name, email, value) VALUES (%s, %s, %s, %s);"""
                cursor.execute(query, (id, j, members[0][0][i], a[j][i]))
                conn.commit()
            else:
                query = """UPDATE marks SET value = %s WHERE id = %s;"""
                cursor.execute(query, (a[j][i], ans[0][0], ))
                conn.commit()

def get_homework_by_class_id(id):
    query = """SELECT homework FROM classes WHERE id = %s;"""
    cursor.execute(query, (id, ))
    conn.commit()
    return cursor.fetchall()

def get_name_of_class(email):
    sqlite3_select_query = """SELECT name FROM classes WHERE id = %s;"""
    cursor.execute(sqlite3_select_query, (email, ))
    conn.commit()
    ans = cursor.fetchall()
    if ans != []:
        return ans[0][0]
    return False

def get_homework_data_by_class_id(id):
    sqlite3_select_query = """SELECT homework_date FROM classes WHERE id = %s;"""
    cursor.execute(sqlite3_select_query, (id, ))
    conn.commit()
    return cursor.fetchall()[0][0]

def get_teachers_by_class_id(id):
    sqlite3_select_query = """SELECT teachers FROM classes WHERE id = %s;"""
    cursor.execute(sqlite3_select_query, (id, ))
    conn.commit()
    return cursor.fetchall()

def update_name(email, password):
    try:
        sqlite3_query = """UPDATE users SET name=%s WHERE email=%s;"""
        cursor.execute(sqlite3_query, (password, email, ))
        conn.commit()
        return True
    except:
        return False
#DEBUG
print(get_all_users())