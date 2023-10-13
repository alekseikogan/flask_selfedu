import datetime
import os
import sqlite3

from flask import (Flask, abort, flash, g, make_response, redirect,
                   render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from FDataBase import FDataBase

DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = os.urandom(20).hex()
USERNAME = 'admin'
PASSWORD = '123'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))
app.permanent_session_lifetime = datetime.timedelta(days=10)

dbase = None


@app.before_request
def before_request():
    """Устанавливает соединение с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.route("/")
def index():
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
def addCar():
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
def showCar(alias):
    title, car = dbase.getCar(alias)
    if not title:
        abort(404)

    return render_template(
        'car.html', menu=dbase.getMenu(), title=title, car=car)


@app.route('/login', methods=['POST', 'GET'])
def login():
    return render_template(
        'login.html',
        menu=dbase.getMenu(),
        title='Авторизация')


@app.route("/logout")
def logout():
    res = make_response("Вы больше не авторизованы!</p>")
    res.set_cookie("logged", "", 0)
    return res


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(
                request.form['name'],
                request.form['email'],
                hash)
            if res:
                flash("Регистрация прошла успешно!", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля", "error")

    return render_template(
        'register.html',
        menu=dbase.getMenu(),
        title='Регистрация')


if __name__ == '__main__':
    app.run(debug=True)
