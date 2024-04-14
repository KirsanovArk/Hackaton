from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_toastr import Toastr  

import os
import shutil


app = Flask(__name__)
app.secret_key = 'Hackaton'  
toastr = Toastr()
toastr.init_app(app=app)


login_manager = LoginManager()
login_manager.login_view = 'login'  
login_manager.init_app(app)


UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


users = {'Жюри': {'password': '348'}, 'admin': {'password': 'admin'}
         }


class User(UserMixin):
    pass


@login_manager.user_loader
def user_loader(username):
    if username not in users:
        return
    user = User()
    user.id = username
    return user


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


@app.route('/')
@login_required  
def index():
    
    disk_usage = shutil.disk_usage("/")
    total = f"Всего: {disk_usage.total / (2**30):.2f} GB"
    used = f"Использовано: {disk_usage.used / (2**30):.2f} GB"
    free = f"Свободно: {disk_usage.free / (2**30):.2f} GB"
    
    
    filenames = os.listdir(app.config['UPLOAD_FOLDER'])
    
    
    return render_template('index.html', filenames=filenames, current_user=current_user, total=total, used=used, free=free)
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if username in users and password == users[username]['password']:
            user = User()
            user.id = username
            login_user(user)  
            return redirect(url_for('index'))
        else:
            flash('Введите корректные данные', 'error')  

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()  
    return redirect(url_for('login'))


@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return "Не указана часть файла"
    file = request.files['file']
    if file.filename == '':
        return "Файл не выбран"
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        path = os.path.join(request.base_url, file.filename)           
        file.save(filename)
        flash('Файл успешно загружен', 'info')  
        return redirect('/')


@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/delete/<filename>', methods=['POST', 'GET'])
@login_required
def delete_file(filename):
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Файл успешно удален', 'info')  
        return redirect(url_for('index'))
    except Exception as e:
        return str(e)


if __name__ == '__main__':
   
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    app.run(debug=True, port=4444)
