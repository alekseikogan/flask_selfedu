import datetime
import os
import sqlite3

from flask import (Flask, abort, flash, g, make_response, redirect,
                   render_template, request, session, url_for)
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from werkzeug.security import check_password_hash, generate_password_hash

from FDataBase import FDataBase
from UserLogin import UserLogin
from forms import LoginForm, RegisterForm
from admin.admin import admin

DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = os.urandom(20).hex()
USERNAME = 'admin'
PASSWORD = '123'
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))
app.permanent_session_lifetime = datetime.timedelta(days=10)
app.register_blueprint(admin, url_prefix='/admin')

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"

dbase = None


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, dbase)


@app.before_request
def before_request():
    """Устанавливает соединение с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


def connect_db():
    """Устанавливает соединение с БД"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


@app.teardown_appcontext
def close_db(error):
    """Закрывает соединение с БД"""
    if hasattr(g, 'link_db'):
        g.link_db.close()


def create_db():
    """Создает таблицы в БД"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    """Получает соединение с БД"""
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.route("/")
def index():
    """Главная страница"""
    if 'visits' in session:
        session['visits'] = session.get('visits') + 1
        session.modified = True
    else:
        session['visits'] = 1
    print(f'session col = {session["visits"]}')
    return render_template(
        'index.html',
        menu=dbase.getMenu(),
        cars=dbase.getCarsAnonce())


@app.route("/add_car", methods=["POST", "GET"])
@login_required
def addCar():
    """Добавление автомобиля в таблицу"""
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addCar(
                request.form['name'],
                request.form['post'],
                request.form['url'],)
            if not res:
                flash('Ошибка добавления авто', category='error')
            else:
                flash('Авто добавлена успешно', category='success')
        else:
            flash('Ошибка добавления авто', category='error')

    return render_template(
        'add_car.html',
        menu=dbase.getMenu(),
        title="Добавление авто")


@app.route("/car/<alias>")
@login_required
def showCar(alias):
    """Страница автомобиля"""
    title, car = dbase.getCar(alias)
    if not title:
        abort(404)

    return render_template(
        'car.html', menu=dbase.getMenu(), title=title, car=car)


@app.route('/login', methods=['POST', 'GET'])
def login():
    """Авторизация"""
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    form = LoginForm()
    if form.validate_on_submit():
        user = dbase.getUserByEmail(form.email.data)
        if user and check_password_hash(user['psw'], form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get('next') or url_for('profile'))
        flash('Неверная пара логин/пароль', 'error')

    return render_template(
        'login.html',
        menu=dbase.getMenu(),
        title='Авторизация',
        form=form)

    # if request.method == 'POST':
    #     user = dbase.getUserByEmail(request.form['email'])
    #     if user and check_password_hash(user['psw'], request.form['psw']):
    #         userlogin = UserLogin().create(user)
    #         rm = True if request.form.get('remainme') else False
    #         login_user(userlogin, remember=rm)
    #         return redirect(request.args.get('next') or url_for('profile'))
    #     flash('Неверная пара логин/пароль', 'error')


@app.route("/logout")
def logout():
    """Выйти из системы"""
    logout_user()
    flash('Вы вышли из системы!', 'success')
    return redirect(url_for('login'))


@app.route("/register", methods=["POST", "GET"])
def register():
    """Регистрация"""
    form = RegisterForm()
    if form.validate_on_submit():
        hash = generate_password_hash(request.form['psw'])
        res = dbase.addUser(form.name.data, form.email.data, hash)
        if res:
            flash("Вы успешно зарегистрированы", "success")
            return redirect(url_for('login'))
        else:
            flash("Ошибка при добавлении в БД", "error")

    return render_template(
        'register.html',
        menu=dbase.getMenu(),
        title='Регистрация',
        form=form)

    # if request.method == 'POST':
    #     if len(request.form['name']) > 4 and len(request.form['email']) > 4 and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
    #         hash = generate_password_hash(request.form['psw'])
    #         res = dbase.addUser(
    #             request.form['name'],
    #             request.form['email'],
    #             hash)
    #         if res:
    #             flash("Регистрация прошла успешно!", "success")
    #             return redirect(url_for('login'))
    #         else:
    #             flash("Ошибка при добавлении в БД", "error")
    #     else:
    #         flash("Неверно заполнены поля", "error")


@app.route('/profile')
@login_required
def profile():
    """Профиль пользователя"""
    return render_template(
        'profile.html',
        menu=dbase.getMenu(),
        title='Профиль')


@app.route('/userava')
@login_required
def userava():
    """Получение объекта фото пользователя"""
    img = current_user.getAvatar(app)
    if not img:
        return ''

    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/upload')
@login_required
def upload():
    """Загрузка фотографии профиля пользователя"""
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.veryfyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка обновления аватара", "error")
                    return redirect(url_for('profile'))
                flash("Аватар обновлен", "success")
            except FileNotFoundError:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")

    return redirect(url_for('profile'))


if __name__ == '__main__':
    app.run(debug=True)
