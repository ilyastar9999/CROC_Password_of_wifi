from flask import Flask, request, render_template, redirect, make_response, flash, session, url_for
import jwt
import json
from flask_mail import Message, Mail
import re
from werkzeug.utils import secure_filename
import os
import parse
import db_code as db
import random
import parse_google
import datetime
from authlib.integrations.flask_client import OAuth
import authlib
import auth0

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/\x00'

def parse_data(field):
    file = open("config.json")
    data = json.load(file)[field]
    return data

def add_field_to_config(a, b):
    with open('config.json', 'r') as file:
        config = json.load(file)
    config[a] = b
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=parse_data("AUTH0_CLIENT_ID"),
    client_secret=parse_data("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{parse_data("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'schoolsilaeder@gmail.com'  
app.config['MAIL_DEFAULT_SENDER'] = 'schoolsilaeder@gmail.com'  
app.config['MAIL_PASSWORD'] = parse_data("mail_password")
app.config['UPLOAD_FOLDER'] = './static/'
app.config['BASE_URL'] = 'http://server.silaeder.ru:11702/confirm/'
app.config['SECRET_KEY'] = parse_data("secret_key")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

mail_sender = Mail(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail_sender.send(msg)

#generates every token, use only this
def gen_token(email):
    return jwt.encode(payload={"email": email, "trash": random.randint(1, 100000), "date": datetime.datetime.now()}, key=app.config['SECRET_KEY'])

#gets email from token and checks time
def get_token_email(token):
    try:
        payload = jwt.decode(token, key=app.config['SECRET_KEY'], algorithms="HS256")
        if datetime.datetime.now() - payload['date'] > datetime.timedelta(hours=2): # do not use expires in cookies like expires=120, 
            return None
        return payload['email']
    except:
        return None

#get user's role from email using .tsv data
def get_role(email):
    data1, data2 = parse.parse_csv()
    if email in data2:
        return "teacher"
    elif email in data1:
        return "student"
    elif email == "schoolsilaeder@gmail.com":
        return "admin"
    else:
        return None

#checks token on pages, returns user's role
def check_and_redirect(token):
    if not token:
        flash('Not authorized')
        return make_response(redirect("/login/"))
    email = get_token_email(token)
    if not email:
        flash('Invalid token, please relogin')
        return make_response(redirect("/login/"))
    role = get_role(email)
    if not role:
        flash('Invalid token, please relogin')
        return make_response(redirect("/login/"))
    return [email, role]

@app.route('/', methods=['GET'])
def main():
    token = session.get('jwt', None)
    admin = False
    if token:
        email = get_token_email(token)
        if email:
            if get_role(email) == 'admin':
                admin = True
    return render_template('what_it_is.html', logged_in=request.cookies.get("jwt"), admin=admin)

@app.route("/login/", methods=["GET", "POST"])
def login():
    # if request.method == "GET":
    #     return render_template("login.html")
    # else:
    #     login = request.form["login"]
    #     password = request.form["password"]
    #     if not db.is_user_exists(login):
    #         flash('Account not found')
    #         return redirect('/login')
    #     if db.get_is_user_logged_in(login, password): # login == email
    #         token = gen_token(login)
    #         resp = make_response(redirect("/"))
    #         session['jwt'] = token
    #         if not session.modified:
    #             session.modified = True
    #         return resp
    #     else:
    #         if db.check_auth_user(login):
    #             flash('Wrong password')
    #         else:
    #             flash('Account not confirmed')
    #         return redirect("/login")
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )   

@app.route('/register/', methods=['GET', 'POST'])
def register():
    # if request.method == 'GET':
    #     return render_template('register.html')
    # else:
    #     form = request.form
    #     password = form['password']
    #     password2 = form['password2']
    #     email = form['email']
    #     name = form['name']

    #     if email == "" or name == "" or password == "" or password2 == "":
    #         flash("All fields are required")
    #         return redirect('/register')

    #     if not re.match(r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$", email):
    #         flash("Invalid email address")
    #         return redirect('/register')

    #     parsed = parse.parse_csv()
    #     if email in parsed[0]:
    #         type_user = 'pipl'
    #     elif email in parsed[1]:
    #         type_user = 'teacher'
    #     else:
    #         flash("Email is not registered in Silaeder. Please check your email or write to administrator(@ilyastarcek)")
    #         return redirect('/register')
    #     if len(password) < 8:
    #         flash("Password must be at least 8 characters long")
    #         return redirect('/register')

    #     hasDigits, hasUpperCase, hasLowerCase, hasSpecialCharecters, hasSpases = False, False, False, False, True

    #     for i in password:
    #         if (i.isdigit()):
    #             hasDigits = True
    #         elif (i.isupper()):
    #             hasUpperCase = True
    #         elif (i.islower()):
    #             hasLowerCase = True
    #         elif (i == ' '):
    #             flash('Spaces are not allowed in')
    #         else:
    #             hasSpecialCharecters = True 

    #     if not hasDigits:
    #         flash("Password must contain at least one digit")
    #         return redirect('/register')
        
    #     if not hasUpperCase:
    #         flash("Password must contain at least one uppercase letter")
    #         return redirect('/register')
        
    #     if not hasLowerCase:
    #         flash("Password must contain at least one lowercase letter")
    #         return redirect('/register')
        
    #     if not hasSpecialCharecters:
    #         flash("Password must contain at least one special character")
    #         return redirect('/register')

    #     if password!= password2:
    #         flash("Passwords don't match")
    #         return redirect('/register')
        
    #     if not db.create_user(name, password, email):
    #         flash("Email is already registered")
    #         return redirect('/register')
    #     else:
    #         token = gen_token(email)
    #         confirm_url = app.config['BASE_URL'] + '/confirm/' + token
    #         send_email(email, "Silaeder School Account confirmation", render_template('mail.html', confirm_url=confirm_url))
    #         flash("A confirmation link has been sent to your email")
    #         return redirect('/login')
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    try:
        token = oauth.auth0.authorize_access_token()
        app.logger.debug(token)
    except authlib.integrations.base_client.errors.OAuthError as e:
        if "Please verify your email before continuing" in str(e):
            flash(['error', "Please verify your email before continuing"])
            return redirect('/')
        else:
            return str(e)
    app.logger.debug(token)
    token2 = gen_token(token['userinfo']['nickname'])
    session['jwt'] = token2
    return redirect('/')


@app.route("/marks/", methods=["GET"])
def marks():
    token = session.get('jwt', None)
    __ans = check_and_redirect(token)
    if type(__ans) == list:
        email, role = __ans[0], __ans[1]
    else:
        return __ans
    if role == "student" or role == 'admin':
        marks = list(db.get_marks(email).items())
        name = db.get_name(email)
        return render_template("marks.html", admin=(role=='admin'), ans=marks, name = name)
    if role == "teacher":
        flash('You are not a student')
        return redirect("/")

@app.route("/homework/", methods=["GET"])
def homeworks():
    token = session.get('jwt', None)
    __ans = check_and_redirect(token)
    if type(__ans) == list:
        email, role = __ans[0], __ans[1]
    else:
        return __ans
    if role == "student" or role == 'admin':
        homeworks = db.get_homework(email)
        name = db.get_name(email)
        return render_template("homework.html", admin=(role=='admin'), ans=homeworks, name=name)
    if role == "teacher":
        flash('You are not a student')
        return redirect("/")
    
@app.route('/classes/', methods=['GET'])
def classes():
    token = session.get('jwt', None)
    __ans = check_and_redirect(token)
    if type(__ans) == list:
        email, role = __ans[0], __ans[1]
    else:
        return __ans
    if role == "student":
        return redirect("/homework")
    if role == "teacher" or role == "admin":
        classes = db.get_classes_by_teacher(email)
        name = db.get_name(email)
        return render_template("Main Teacher.html", admin=role=='admin', ans=classes, name=name)
        
# @app.route('/confirm/<token>/', methods=['GET'])
# def confirm_email(token):
#     email = get_token_email(token)
#     if not email:
#         flash('The confirmation link is invalid or expired. Please check your email')
#         return redirect('/login')
#     if db.check_not_auth_user_is_exist(email) == []:
#         flash('This link is for not registered account')
#         return redirect('/registration')
#     token = jwt.encode(payload={"name": email, "role": get_role(email), "trash": random.randint(1, 100000)}, key=app.config['SECRET_KEY'])
#     if db.check_auth_user(email):
#         flash('Account already confirmed. Please login')
#         return redirect('/login')
#     else:
#         db.auth_user(email)
#         flash('You have confirmed your account. Thank you for joining us!')
#         resp = make_response(redirect("/"))
#         if not session.modified:
#             session.modified = True
#         return resp

@app.route('/logout/', methods=['GET'])
def logout():
    resp = make_response(redirect("/"))
    session.clear()
    if not session.modified:
        session.modified = True
    flash('Goodbye!')
    return resp

@app.route('/classes/add/', methods=['GET', 'POST'])
def class_add():
    token = session.get('jwt', None)
    __ans = check_and_redirect(token)
    if type(__ans) == list:
        email, role = __ans[0], __ans[1]
    else:
        return __ans
    if role == "student":
        flash("Access denied")
        return redirect('/homework')
    if request.method == 'GET':
        return render_template('class_add.html', type='common')
    else:
        form = request.form
        name = form['name']
        if name == "":
            flash("Class name is required")
            return redirect('/classes/add')
        password = form['password']
        if password == "":
            for i in range(random.randint(4, 10)):
                password += random.choice('qwertyuiopasdfghjklzxcvbnmQAZWSXEDCRFVTGBYHNUJMIK,OL.P_()')
        db.create_class(name, password, email)
        flash("Class added")
        return redirect('/classes')

@app.route('/classes/add_google_class/', methods=['GET', 'POST'])
def class_google_add():
    token = session.get('jwt', None)
    __ans = check_and_redirect(token)
    if type(__ans) == list:
        email, role = __ans[0], __ans[1]
    else:
        return __ans
    if role == "student":
        flash("Access denied")
        return redirect('/homework')
    if request.method == 'GET':
        return render_template('class_add.html', type='google')
    else:
        form = request.form
        name = form['name']
        sheet = form['sheet']
        col = form['col']
        for i in col:
            if i not in 'QWERTYUIOPASDFGHJKLZXCVBNM:1234567890':
                flash('Student column is not valid')
                return redirect('/classes/add_google_class/')
        link = form['link']
        
        if link == '':
            flash("Link is required")
            return redirect('/classes/add_google_class')
        if link.find('/d/') == -1:
            flash("Link is invalid")
            return redirect('/classes/add_google_class')
        link = link[link.find('/d/')+3:]
        if link.find('/') == -1:
            flash("Link is invalid")
            return redirect('/classes/add_google_class')
        link = link[:link.find('/')]
        
        if sheet == '':
            flash("List name is required")
            return redirect('/classes/add_google_class')
        if name == "":
            flash("Class name is required")
            return redirect('/classes/add_google_class')
        members = parse_google.get_data_from_google_sheet(sheet, col, link)
        if members == False:
            flash("Invalid table data")
            return redirect('/classes/add_google_class')
        if members == []:
            flash("Nothing in requested google table data")
            return redirect('/classes/add_google_class')
        password = form['password']
        if password == "":
            for i in range(random.randint(4, 10)):
                password += random.choice('qwertyuiopasdfghjklzxcvbnmQAZWSXEDCRFVTGBYHNUJMIK,OL.P_()')
        
        db.create_google_class(name, password, email, members, link, sheet)
        flash("Class added")
        return redirect('/classes')

@app.route('/classes/<id>/', methods=['GET'])
def class_view(id):
    if not db.is_class_exists(id):
        flash('Class not found')
        return redirect('/')
    token = session.get('jwt', None)
    __ans = check_and_redirect(token)
    if type(__ans) == list:
        email, role = __ans[0], __ans[1]
    else:
        return __ans
    if not db.is_teacher_in_class(id, email):
        flash("Access denied")
        return redirect('/classes')
        
    password = list(db.get_class_by_id(id)[0])
    #
    name = password[1]
    password = password[2]
    names, ans = db.get_marks_by_class(id)
    date = db.get_homework_data_by_class_id(id)
    teachers = ', '.join(db.get_teachers_by_class_id(id)[0][0])
    #
    return render_template('Class.html', admin=role=='admin', name=name, ans=ans, names=names, id=id, password=password, homework=db.get_homework_by_class_id(id), homework_date=date, teachers=teachers, type=db.get_class_type(id), rangee=list(range(len(names)-1)))

@app.route('/classes/<id>/requests/', methods=['GET', 'POST'])
def google_class_requests(id):
    if not db.is_class_exists(id):
        flash('Class not found')
        return redirect('/classes')
    token = session.get('jwt', None)
    __ans = check_and_redirect(token)
    if type(__ans) == list:
        email, role = __ans[0], __ans[1]
    else:
        return __ans
    if not db.is_teacher_in_class(id, email):
        flash("Access denied")
        return redirect('/classes')
    if db.get_class_type(id) == 'common':
        flash("Request for adding to class is not supporting for common classes")
        return redirect("/classes/"+str(id)+'/')
    
    if request.method == "GET":
        a = db.get_class_requests(id)
        
        return render_template('connect_google.html', members=db.get_class_members_for_requests(id), requests=a, id=id)
    else:
        form = request.form
        
        result = form['submit']
        f_email = form['email']
        name = form['name']
        if result == 'Update':
            member = form['member']
            db.aprove_request_to_class(id, f_email, member, name)
            flash(f'User {name} sucssesfuly sign with {member}')
            return redirect("/classes/"+str(id)+'/requests')
        else:
            db.decline_request_to_class(id, f_email, name)
            flash(f'Request from user {name} sucssesfuly deleted')
            return redirect("/classes/"+str(id)+'/requests')

@app.route('/classes/<id>/add_student/', methods=['GET', 'POST'])
def add_student(id):
    if not db.is_class_exists(id):
        flash('Class not found')
        return redirect('/classes')
    token = session.get('jwt', None)
    __ans = check_and_redirect(token)
    if type(__ans) == list:
        email, role = __ans[0], __ans[1]
    else:
        return __ans
    if role != 'student':
        flash("Access denied")
        return redirect('/classes')
    if db.is_student_in_class(id, email):
        flash("You already in class")
        return redirect('/classes')
    if not db.is_class_exists(id):
        flash("No class exists")
        return redirect('/classes')
    if request.method == 'GET':
        if db.get_class_type(id) == 'google':
            return render_template('add_student.html', members=db.get_class_members(id))
        return render_template('add_student.html')
    else:
        form = request.form
        password = form['password']
        if db.check_class_password(id, password):
            if db.get_class_type(id) == 'google':
                if db.is_request_send(id, email):
                    flash('You request already sended')
                    return redirect('/classes')
                if db.add_student_to_google(id, email):
                    flash('You request sucssesfuly sended')
                    return redirect('/classes')
                flash('ERROR')
                return redirect('/classes')
            else:
                if db.add_class_member(id, email):
                    flash('You sucssesfuly added')
                    return redirect('/classes')
        else:
            flash("Invalid password")
            return redirect('/classes/'+str(id)+'/add_student')

@app.route('/classes/<id>/delete_col/<ind>', methods=['GET'])
def delete_col(id, ind):
    if not db.is_class_exists(id):
        flash('Class not found')
        return redirect('/classes')
    token = session.get('jwt', None)
    __ans = check_and_redirect(token)
    if type(__ans) == list:
        email, role = __ans[0], __ans[1]
    else:
        return __ans
    if role == 'student':
        flash("Access denied") 
        return redirect('/classes')
    if not db.is_teacher_in_class(id, email):
        flash("Access denied")
        return redirect('/classes')
    db.delete_col_in_class(id, int(ind))
    flash('Column deleted sucssesfuly')
    return redirect('/classes/' + str(id)+'/')

@app.route('/classes/<id>/add_teacher/', methods=['GET', 'POST'])  
def add_teacher(id):
    if not db.is_class_exists(id):
        flash('Class not found')
        return redirect('/classes')
    token = session.get('jwt', None)
    __ans = check_and_redirect(token)
    if type(__ans) == list:
        email, role = __ans[0], __ans[1]
    else:
        return __ans
    if role == 'student':
        flash("Access denied") # Может всё же access?
        return redirect('/classes')
    if not db.is_teacher_in_class(id, email):
        flash("Access denied")
        return redirect('/classes')
    if request.method == 'GET':
        return render_template('add_teacher.html', id=id)
    else:
        form = request.form
        email = form['email']
        if db.is_user_exists(email):
            if db.add_teacher(id, email):
                flash('Teacher added successfully')
                return redirect("/classes/"+str(id)+'/')
            else:
                return "Error"
        else:
            flash('No such user')
            return redirect(f"/classes/{id}/add_teacher")

@app.route('/classes/<id>/edit_homework/', methods=['GET', 'POST'])
def edit_homework(id):
    if not db.is_class_exists(id):
        flash('Class not found')
        return redirect('/classes')
    token = session.get('jwt', None)
    __ans = check_and_redirect(token)
    if type(__ans) == list:
        email, role = __ans[0], __ans[1]
    else:
        return __ans
    if role != 'student' and db.is_teacher_in_class(id, email):
        if request.method == 'GET':
            return render_template('edit_homework.html', id=id)
        else:
            form = request.form
            text = form['text']
            if db.update_homework(id, text):
                flash('Homework updated successfully')
                return redirect(f"/classes/{id}")
            else:
                return 'ERROR'
    else:
        flash("Access denied")
        return redirect('/classes')

@app.route('/classes/<id>/edit_marks/', methods=['GET', 'POST']) #write
def edit_marks(id):
    token = session.get('jwt', None)
    __ans = check_and_redirect(token)
    if type(__ans) == list:
        email, role = __ans[0], __ans[1]
    else:
        return __ans
    if role == 'student':
        flash("Access denied")
        return redirect('/classes')
    if not db.is_class_exists(id):
        flash('Class not found')
        return redirect('/classes')
    if db.get_class_members(id)[0][0] == None:
        flash('Nobody in class. Please add members to your class')
        return redirect(f'/classes/{id}/')
    
    if request.method == 'GET':
        if db.get_class_type(id) == 'common':
            names, ans = db.get_marks_by_class(id)
            
            return render_template('edit_marks.html', id=id, names=names, ans=ans, iss=list(range(len(ans))), jss=list(range(len(ans[0]))), mxi=len(ans), mxj=len(ans[0]))
        else:
            return render_template('add_col.html', id=id)
    else:
        if db.get_class_type(id) == 'common':
            #try:
            form = dict(request.form)
            
            mxi = max([int(i.split('-')[0]) for i in form.keys() if i.find('-') != -1])
            mxj = max([int(i.split('-')[1]) for i in form.keys() if i.find('-') != -1])
            a = [[form[str(i)+'-'+str(j)] for j in range(1, mxj+1)] for i in range(1, mxi+1)]
            names = request.form.getlist('names[]')
            
            
            db.update_marks(id, a, names)
        #except:
        #       return 'ERROR: EDIT MARK'
            flash('Marks updated successfully')
            return redirect(f'/classes/{id}/')
        else:
            col = request.form['col']
            check = parse_google.get_data_from_google_sheet(db.get_sheet_by_class_id(id), col, db.get_link_by_class_id(id))
            if check == False:
                flash("Invalid table data")
                return redirect('/classes/'+str(id)+'/edit_marks/')
            if check == []:
                flash("Nothing in requested google table data")
                return redirect('/classes/'+str(id)+'/edit_marks/')
            db.add_google_col_to_marks(id, col)
            flash('Column added successfully')
            return redirect('/classes/'+str(id)+'/')
            

@app.route('/change_password/', methods=['GET', 'POST'])
def change_password():
    token = session.get('jwt', None)
    __ans = check_and_redirect(token)
    if type(__ans) == list:
        email, role = __ans[0], __ans[1]
    else:
        return __ans
    if request.method == 'GET':
        return render_template('change_pass.html')
    else:
        form = request.form
        old_pass = form['old_pass']
        password = form['new_pass']
        password2 = form['new_pass2']
        if db.get_is_user_logged_in(email, old_pass):
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
                return redirect('/change_password')
            
            if not hasUpperCase:
                flash("Password must contain at least one uppercase letter")
                return redirect('/change_password')
            
            if not hasLowerCase:
                flash("Password must contain at least one lowercase letter")
                return redirect('/change_password')
            
            if not hasSpecialCharecters:
                flash("Password must contain at least one special character")
                return redirect('/change_password')

            if password!= password2:
                flash("Passwords don't match")
                return redirect('/change_password')

            flash('Updated password sucsesfuly')
            db.change_password(email, password)
            return redirect('/classes')
        else:
            flash("Invalid old password")
        
@app.route("/change_name/", methods=['GET', 'POST'])
def change_name():
    token = session.get('jwt', None)
    __ans = check_and_redirect(token)
    if type(__ans) == list:
        email, role = __ans[0], __ans[1]
    else:
        return __ans
    if request.method == 'GET':
        return render_template('change_name.html')
    else:
        form = request.form
        if (form['name'] == ''):
            flash("All felds are reqired")
            return redirect("/change_name")
        if not db.update_name(email, form['name']):
            return 'ERROR'
        flash('Name update sucssesfuly')
        return redirect('/classes')

@app.route('/flag.txt', methods=['GET'])
def test2():
    return 'Flag! - PB{pb_fl4g_f0r_y0u}'

@app.route('/s3cr37_P@63_F0r_C7Fs_@nd_160r/', methods=['GET'])
def test():
    return redirect('https://www.youtube.com/watch?v=s8hlfPqdRFw')

if __name__== '__main__':
    app.run("0.0.0.0", port=11802, debug=True)

