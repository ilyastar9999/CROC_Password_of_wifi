from flask import Flask, request, render_template, redirect, make_response, flash
import jwt
import json
from flask_mail import Message, Mail
import re
from werkzeug.utils import secure_filename
import os
import parse
#import db_code as db
import random

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

def parse_data(field):
    file = open("config.json")
    data = json.load(file)[field]

    return data

#db.delete_all()
#db.create_all()

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'silaederprojects@gmail.com'  
app.config['MAIL_DEFAULT_SENDER'] = 'silaederprojects@gmail.com'  
#app.config['MAIL_PASSWORD'] = parse_data("mail_password")
app.config['UPLOAD_FOLDER'] = './static/'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

mail_sender = Mail(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=parse_data('mail')
    )
    mail_sender.send(msg)

def generate_confirmation_token(email):
    return jwt.encode(payload={"name": email, "trash": random.randint(1, 100000)}, key=parse_data("secret_key"))


def confirm_token(token):
    try:
    	return jwt.decode(token, key=parse_data("secret_key"), algorithms="HS256")["name"]
    except:
    	return False


def check_jwt(token, username):
    try:
        payload = jwt.decode(token, key=parse_data("secret_key"), algorithms="HS256")
    except:
        return False

    if payload["name"] == username:
        return True
    else:
        return False

def role(username):
    data, data1 = parse.parse_csv()
    if username in data:
        return "student"
    elif username in data1:
        return "teacher"
    elif username == "admin":
        return "admin"

@app.route("/user", methods=["GET"])
def user():
    token = request.cookies.get("jwt")
    if not token:
        flash('You are not logged in')
        return redirect("/login", code=302)
    email = confirm_token(token)
    if not email:
        flash('Invalid token')
        return redirect("/login", code=302)
    role = role(email)
    if not role:
        flash('Invalid token')
        return redirect("/login", code=302)
    data = db.get_user_by_email(email)
    if data != []:
        return render_template("user.html", data=data)
    else:
        flash('User not found')
        return redirect("/login", code=403)

@app.route("/marks", methods=["GET"])
def marks():
    token = request.cookies.get("jwt")
    if not token:
        flash('You are not logged in')
        return redirect("/login", code=302)
    email = confirm_token(token)
    if not email:
        flash('Invalid token')
        return redirect("/login", code=302)
    role = role(email)
    if role == "student":
        marks = db.get_marks(email)
        name = db.get_name(email)
        return render_template("marks.html", ans=marks, name = name)
    if role == "teacher":
        return redirect("/", code=302)

@app.route("/homework", methods=["GET"])
def homeworks():
    token = request.cookies.get("jwt")
    if not token:
        flash('You are not logged in')
        return redirect("/login", code=302)
    email = confirm_token(token)
    if not email:
        flash('Invalid token')
        return redirect("/login", code=302)
    role = role(email)
    if role == "student":
        homeworks = db.get_homework(email)
        name = db.get_name(email)
        return render_template("index.html", ans=homeworks, name = name)
    if role == "teacher":
        return redirect("/", code=302)

@app.route('/', methods=['GET'])
def main():
    token = request.cookies.get("jwt")
    if not token:
        flash('You are not logged in')
        return redirect("/login", code=302)
    email = confirm_token(token)
    if not email:
        flash('Invalid token')
        return redirect("/login", code=302)
    role = role(email)
    if not role:
        flash('Invalid token')
        return redirect("/login", code=302)
    if role == "student":
        return redirect("/homeworks", code=302)
    if role == "teacher":
        classes = db.get_classes_by_teacher(email)
        name = db.get_name(email)
        return render_template("index.html", classes=classes, name = name)
        

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("Signin Template.html")
    
    else:
        login = request.form["login"]
        password = request.form["password"]

        if db.get_is_user_logged_in(login, password):
            token = jwt.encode(payload={"name": login, "role": role(login), "trash": random.randint(1, 100000)}, key=parse_data("secret_key"))
            resp = make_response(redirect("/"))
            resp.set_cookie("jwt", token)
            return resp
        else:
            flash('Wrong email or password')
            return redirect("/login", code=302)
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('Login Template.html')
    else:
        form = request.form
        password = form['password']
        password2 = form['password2']
        email = form['email']
        name = form['name']

        if email == "" or name == "" or password == "" or password2 == "":
            flash("All fields are required")
            return redirect('/register')

        if not re.match(r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$", email):
            flash("Invalid email address")
            return redirect('/register')

        parsed = parse.parse_csv()
        if email in parsed[0]:
            type_user = 'pipl'
        elif email in parsed[1]:
            type_user = 'teacher'
        else:
            flash("Email is not registered in Silaeder. Please check your email or write to administrator(@ilyastarcek)")
            return redirect('/register')
        if len(password) < 8:
            flash("Password must be at least 8 characters long")
            return redirect('/register')

        hasDigits, hasUpperCase, hasLowerCase, hasSpecialCharecters, hasSpases = False, False, False, False, True

        for i in password:
            if (i.isdigit()):
                hasDigits = True
            elif (i.isupper()):
                hasUpperCase = True
            elif (i.islower()):
                hasLowerCase = True
            elif (i == ' '):
                flash('Spaces are not allowed in')
            else:
                hasSpecialCharecters = True 

        if not hasDigits:
            flash("Password must contain at least one digit")
            return redirect('/register')
        
        if not hasUpperCase:
            flash("Password must contain at least one uppercase letter")
            return redirect('/register')
        
        if not hasLowerCase:
            flash("Password must contain at least one lowercase letter")
            return redirect('/register')
        
        if not hasSpecialCharecters:
            flash("Password must contain at least one special character")
            return redirect('/register')

        if password!= password2:
            flash("Passwords don't match")
            return redirect('/register')
        
        if not db.create_user(name, password, email):
            flash("Email is already registered")
            return redirect('/register')
        else:
            token = generate_confirmation_token(email)
            confirm_url = "http://server.silaeder.ru:11702/confirm/" + token
            send_email(email, "Silaeder School confirmation", render_template('mail.html', confirm_url=confirm_url))
            flash("A confirmation email has been sent to your email")
            return redirect('/login')
        
@app.route('/confirm/<token>', methods=['GET'])
def confirm_email(token):
    print(token)
    try:
        username = confirm_token(token)
        print(username)
    except:
        flash('The confirmation link is invalid. Check your email')
        return redirect('/', code=302)
    if db.check_not_auth_user_is_exist(username) == []:
        flash('This is link for not registered account')
        return redirect('/registration', code=302)
    token = jwt.encode(payload={"name": username, "role": role(username), "trash": random.randint(1, 100000)}, key=parse_data("secret_key"))
    if db.check_auth_user(username):
        print(db.check_auth_user(username))
        flash('Account already confirmed . Please login')
        return redirect('/login', code=302)
    else:
        db.auth_user(username)
        flash('You have confirmed your account. Thanks!')
        resp = make_response(redirect("/", code=302))
        resp.set_cookie("jwt", token)
        return resp

@app.route('/logout', methods=['GET'])
def logout():
    resp = make_response(redirect("/login", code=302))
    resp.set_cookie("jwt", "", expires=0)
    return resp

@app.route('/classes/add', methods=['GET', 'POST'])
def class_add():
    if request.method == 'GET':
        token = request.cookies.get("jwt")
        if not token:
            flash('You are not logged in')
            return redirect("/login", code=302)
        email = confirm_token(token)
        if not email:
            flash('Invalid token')
            return redirect("/login", code=302)
        role = role(email)
        if not role:
            flash('Invalid token')
            return redirect("/login", code=302)
        if role == 'teacher':
            return render_template('class_add.html')
        else:
            flash("Asset denied")
            return redirect('/', code=403)
    else:
        token = request.cookies.get("jwt")
        if not token:
            flash('You are not logged in')
            return redirect("/login", code=302)
        email = confirm_token(token)
        if not email:
            flash('Invalid token')
            return redirect("/login", code=302)
        role = role(email)
        if not role:
            flash('Invalid token')
            return redirect("/login", code=302)
        if role != 'teacher':
            flash("Asset denied")
            return redirect('/', code=403)
        form = request.form
        name = form['name']
        if name == "":
            flash("Class name is required")
            return redirect('/classes/add', code=302)
        password = form['password']
        if password == "":
            for i in range(random.randint(4, 10)):
                password += random.choice('qwertyuiopasdfghjklzxcvbnmQAZWSXEDCRFVTGBYHNUJMIK,OL.P_()')
        if db.create_class(name, password, email):
            flash("Class created successfully")
            return redirect('/', code=200)


@app.route('/classes/<id>', methods=['GET'])
def class_view(id):
    data = db.get_class_by_id(id)
    return render_template('class_view.html', data=data)

@app.route('/classes/<id>/add_student', methods=['GET', 'POST'])
def add_student():
    token = request.cookies.get("jwt")
    if not token:
        flash('You are not logged in')
        return redirect("/login", code=302)
    email = confirm_token(token)
    if not email:
        flash('Invalid token')
        return redirect("/login", code=302)
    role = role(email)
    if not role:
        flash('Invalid token')
        return redirect("/login", code=302)
    if role != 'student':
        flash("Asset denied")
        return redirect('/', code=403)
    if not db.is_class_exists(id):
        flash("No class exists")
        return redirect('/', code=404)
    if request.method == 'GET':
        return render_template('add_student.html')
    else:
        form = request.form
        password = form['password']
        if db.check_class_password(id, password):
            if db.add_student(id, email):
                flash('You sucssesfuly added')
                return redirect('/classes/'+str(id)+'/', code=200)
        else:
            flash("Invalid password")
            return redirect('/', code=403)

@app.route('/classes/<id>/add_teacher', methods=['GET', 'POST'])  
def add_teacher(id):
    token = request.cookies.get("jwt")
    if not token:
        flash('You are not logged in')
        return redirect("/login", code=302)
    email = confirm_token(token)
    if not email:
        flash('Invalid token')
        return redirect("/login", code=302)
    role = role(email)
    if not role:
        flash('Invalid token')
        return redirect("/login", code=302)
    if role != 'teacher':
        flash("Asset denied")
        return redirect('/', code=403)
    if request.method == 'GET':
        return render_template('add_teacher.html')
    else:
        form = request.form
        email = form['email']
        if db.is_user_exists(email):
            if db.add_user(email):
                flash('Teacher added successfully')
                return redirect("/classes<", code=200)
            else:
                return "Error"
        else:
            flash('No such user')
            return redirect(f"/classes/{id}/add_teacher", code=302)

@app.route('/classes/<id>/edit_homework', methods=['GET', 'POST'])
def edit_homework(id):
    token = request.cookies.get("jwt")
    if not token:
        flash('You are not logged in')
        return redirect("/login", code=302)
    email = confirm_token(token)
    if not email:
        flash('Invalid token')
        return redirect("/login", code=302)
    role = role(email)
    if not role:
        flash('Invalid token')
        return redirect("/login", code=302)
    if role == 'teacher':
        if request.method == 'GET':
            return render_template('class_add.html')
        else:
            form = request.form
            text = form['text']
            if db.update_homework(id, text):
                flash('Homework updated successfully')
                redirect(f"/classes/{id}", code=200)
            else:
                return 'ERROR'
    else:
        flash("Asset denied")
        return redirect('/', code=403)

@app.route('/classes/<id>/student/<student_id>', methods=['GET'])
def view_student(id, student_id):
    token = request.cookies.get("jwt")
    if not token:
        flash('You are not logged in')
        return redirect("/login", code=302)
    email = confirm_token(token)
    if not email:
        flash('Invalid token')
        return redirect("/login", code=302)
    role = role(email)
    if not role:
        flash('Invalid token')
        return redirect("/login", code=302)
    if role != 'teacher':
        flash("Asset denied")
        return redirect('/', code=403)
    stu_data = db.get_student_by_id_in_class(id, student_id)
    marks = db.get_stydent_marks_in_class(id, student_id)
    return render_template('student.html')

#
if __name__== '__main__':
    app.run("0.0.0.0", port=11702, debug=True)