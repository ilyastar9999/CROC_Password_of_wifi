import psycopg2
import json
import time
import locale
from datetime import datetime
#import sqlite3
import parse_google

AUTO_CLEAR_IN_START = True

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

def parse_data(field):
    file = open("config.json")
    data = json.load(file)[field]
    return data

conn = psycopg2.connect(port=parse_data("port"), host=parse_data("host"), dbname=parse_data("dbname"), user=parse_data("user"), password=parse_data("password"))

# TODO: use logging library
print('sucsessful connect to db')
#conn = sqlite3.connect('db.sql')

cursor = conn.cursor()

conn.rollback()

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

def check_auth_user(email):
    sqlite3_select_query = """SELECT auth FROM users WHERE email = %s;"""
    cursor.execute(sqlite3_select_query, (email, ))
    conn.commit()
    try:
        if cursor.fetchall()[0][0]:
            return True
        else:
            return False
    except:
        conn.rollback()
        return True

def auth_user(email):
    sqlite3_select_query = """Update users SET auth = true WHERE email = %s;"""
    cursor.execute(sqlite3_select_query, (email, ))
    return

def check_not_auth_user_is_exist(email):
    sqlite3_select_query = """SELECT email FROM users WHERE email =%s;"""
    cursor.execute(sqlite3_select_query, (email, ))
    conn.commit()
    return cursor.fetchall()

def create_all():
    try:
        sqlite_select_query = """CREATE TABLE IF NOT EXISTS marks(id SERIAL PRIMARY KEY, value TEXT, email TEXT, class_id TEXT, name INTEGER);  
    CREATE TABLE IF NOT EXISTS users(id SERIAL PRIMARY KEY, name TEXT, password TEXT, auth BOOLEAN, email TEXT UNIQUE);
    CREATE TABLE IF NOT EXISTS classes(id SERIAL PRIMARY KEY, name TEXT, password TEXT, members TEXT ARRAY, homework TEXT, homework_date TEXT, teachers TEXT ARRAY, names TEXT ARRAY, link TEXT, sheet TEXT);
    CREATE TABLE IF NOT EXISTS requests(id SERIAL PRIMARY KEY, email TEXT, class_id TEXT, name TEXT);"""
        cursor.execute(sqlite_select_query)
        conn.commit() 
        create_user("Admin Adminovich", parse_data("secret_key"), "schoolsilaeder@gmail.com")
        auth_user('schoolsilaeder@gmail.com')
    except:
        print('failed creating all tables, please try again')
    return

def delete_all():
    try:    
        sqlite_select_query = """DROP TABLE marks; DROP TABLE users; DROP TABLE classes;"""
        cursor.execute(sqlite_select_query)
        conn.commit()
        
        #return True
    except:
        conn.rollback()
      #  return False

def get_is_user_logged_in(email, password):
    sqlite3_select_query = """SELECT auth FROM users WHERE email=%s AND password=%s;"""
    cursor.execute(sqlite3_select_query, (email, password, ))
    conn.commit()
    ans = cursor.fetchall()
    
    if ans != []:
        if email == 'schoolsilaeder@gmail.com':
            return True
        return ans[0][0]
    else:
        return False
    
def get_homework(email):
    if email == "schoolsilaeder@gmail.com":
        sqlite3_select_query = """SELECT name, homework, homework_date FROM classes;"""
        cursor.execute(sqlite3_select_query)
        conn.commit()
        return cursor.fetchall()
    sqlite3_select_query = """SELECT name, homework, homework_date FROM classes WHERE %s = ANY(members);"""
    cursor.execute(sqlite3_select_query, (email, ))
    conn.commit()
    return cursor.fetchall()

def get_marks(email):
    if email == "schoolsilaeder@gmail.com":
        sqlite3_select_query = """SELECT class_id, value, name FROM marks;"""
        cursor.execute(sqlite3_select_query)
        conn.commit()
    else:
        sqlite3_select_query = """SELECT class_id, value, name FROM marks WHERE email = %s;"""
        cursor.execute(sqlite3_select_query, (email, ))
        conn.commit()
    ans = cursor.fetchall()
    ans1 = {}
    for i in ans:
        name = get_name_of_class(i[0])
        desc = get_topics_of_marks(i[0])[0][0]
        
        
        if name == False:
            continue
        try:
            ans1[name].append([i[1], desc[i[2]]])
        except:
            ans1[name] = [[i[1], desc[i[2]]]]
    
    sqlite3_select_query = """SELECT name, names, link, sheet, members, id FROM classes WHERE %s = ANY(members) AND link IS NOT NULL;"""
    cursor.execute(sqlite3_select_query, (email, ))
    conn.commit()
    ans = cursor.fetchall()
    for i in ans:
        ind = i[-2].index(email)
        res = []
        name = i[1]
        for j in name:
            res.append(parse_google.get_data_from_google_sheet(i[3], j, i[2]))
        
        for j in res:
            try:
                ans1[i[0]].append([j[ind], j[0]])
            except:
                ans1[i[0]] = [[j[ind], j[0]]]
    
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

def get_link_by_class_id(id):
    sqlite3 = 'SELECT link FROM classes WHERE id = %s;'
    cursor.execute(sqlite3, (id, ))
    conn.commit()
    return cursor.fetchall()[0][0]

def get_sheet_by_class_id(id):
    sqlite3 = 'SELECT sheet FROM classes WHERE id = %s;'
    cursor.execute(sqlite3, (id, ))
    conn.commit()
    return cursor.fetchall()[0][0]

def get_marks_by_class(id_class):
    query = """SELECT members FROM classes WHERE id = %s;"""
    cursor.execute(query, (id_class, ))
    conn.commit()
    aaa = cursor.fetchall()[0][0]
    if aaa == None:
        return [], []
    members = [[get_name(i), i] if '@' in i else i for i in aaa]
    
    query = """SELECT names FROM classes WHERE id = %s;"""
    cursor.execute(query, (id_class, ))
    conn.commit()
    fetchal = list(cursor.fetchall()[0])
    
    if get_class_type(id_class) == 'common':
        members = [[get_name(i), i] for i in aaa]
        if fetchal == [None]:
            
            return ['Student'], [[members[i][0]] for i in range(len(members))]
        names = ['Student'] + fetchal[0]
        ans = []
        for i in range(len(members)):
            
            query = """SELECT value, name FROM marks WHERE class_id = %s AND email = %s ORDER BY name;"""
            cursor.execute(query, (id_class, members[i][1], ))
            conn.commit()
            a = [list(i) for i in cursor.fetchall()]
            
            if a == []:
                
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
            
            ans.append([members[i][0]] + b)
        return names, ans
    else:
        members = [get_name(i) if '@' in i else i for i in aaa]
        
        if fetchal == [None]:
            names = ['Student']
            ans = [[i] for i in members]
            return names, ans
        fetchale = fetchal[0]
        ans = []
        link = get_link_by_class_id(id_class)
        sheet = get_sheet_by_class_id(id_class)
        
        for i in range(len(fetchale)):
            ans.append(parse_google.get_data_from_google_sheet(sheet, fetchale[i], link))
        names = ['Student'] + [i[0] for i in ans]
        ans1 = [[members[i] if j == 0 else ans[j-1][i+1] for j in range(len(ans)+1)] for i in range(len(members))]
        print(ans1, ans)
        return names, ans1

def change_password(email, password):
    query = """UPDATE users SET password = %s WHERE email=%s;"""
    cursor.execute(query, (password, email, ))
    conn.commit()
    return

def get_topics_of_marks(id):
    query = """SELECT names FROM classes WHERE id=%s;"""
    cursor.execute(query, (id, ))
    conn.commit()
    return cursor.fetchall()

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
    
    query = """UPDATE classes SET names = %s WHERE id = %s;"""
    cursor.execute(query, (names, id, ))
    conn.commit()
    members = get_class_members(id)
    for j in range(len(a)):
        for i in range(len(a[j])):
            
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
        conn.rollback()
        return False

def get_class_type(id):
    sqlite3_query = """SELECT link FROM classes WHERE id = %s;"""    
    cursor.execute(sqlite3_query, (id, ))
    conn.commit()
    ans = cursor.fetchall()
    if ans[0][0] == None:
        return 'common'
    else:
        return 'google'

def add_class_members(id, members):
    for i in members:
        if not add_class_member(id, i):
            return False
    return True

def create_google_class(class_name, password, teacher_email, members, link, sheet):
    #try:
        now = datetime.now()
        sqlite3_select_query = """INSERT INTO classes (name, password, teachers, homework_date, link, sheet) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;"""
        cursor.execute(sqlite3_select_query, (class_name, password, [teacher_email], f'{str(now.day)}.{str(now.month)}.{str(now.year)}', link, sheet, ))
        conn.commit()
        id = cursor.fetchall()
        
        return add_class_members(id[0][0], members)
    #except:
        #conn.rollback()
        #return False
    
def add_student_to_google(id, email):
    sqlite3_query = 'INSERT INTO requests(class_id, email, name) VALUES (%s, %s, %s);'
    cursor.execute(sqlite3_query, (id, email, get_name(email), ))
    conn.commit()
    return True

def is_request_send(id, email):
    sqlite3_query = 'SELECT id FROM requests WHERE class_id = %s AND email = %s;'
    cursor.execute(sqlite3_query, (id, email, ))
    conn.commit()
    return cursor.fetchall() != []

def decline_request_to_class(id, email, name):
    sqlite3_query = 'DELETE FROM requests WHERE class_id=%s AND email=%s;'
    cursor.execute(sqlite3_query, (id, email, ))
    conn.commit()
    return True

def aprove_request_to_class(id, email, name, member):
    decline_request_to_class(id, email, name)
    sqlite3_query = 'SELECT members FROM classes WHERE id = %s;'
    cursor.execute(sqlite3_query, (id, ))
    conn.commit()
    a = cursor.fetchall()[0][0]
    a[a.index(name)] = email
    sqlite3 = 'UPDATE classes SET members = %s WHERE id = %s;'
    cursor.execute(sqlite3, (a, id, ))
    conn.commit()
    return True

def get_class_members_for_requests(id):
    a = get_class_members(id)[0][0]
    b = []
    for i in a:
        if '@' not in i:
            b.append(i)
    return b

def get_class_requests(id):
    sqlite3 = 'SELECT name, email FROM requests WHERE class_id = %s;'
    cursor.execute(sqlite3, (id,))
    conn.commit()
    return cursor.fetchall()

def add_google_col_to_marks(id, col):
    sqlite3 = 'UPDATE classes SET names = array_append(names, %s) WHERE id = %s;'
    cursor.execute(sqlite3, (col, id, ))
    conn.commit()
    return True

def delete_col_in_class(id, ind):
    sqlite3 = 'SELECT names FROM classes WHERE id = %s;'
    cursor.execute(sqlite3, (id,))
    conn.commit()
    a = cursor.fetchall()[0][0]
    indd = ind + 1
    a = a[:ind] + a[indd:]
    
    sqlite3 = 'UPDATE classes SET names = %s WHERE id = %s;'
    cursor.execute(sqlite3, (a, id, ))
    conn.commit()
    sqlite3 = 'DELETE FROM marks WHERE class_id = %s AND name = %s;'
    cursor.execute(sqlite3, (id, ind, ))
    conn.commit()
    return True

#DEBUG
#create_all()
print("created all")

