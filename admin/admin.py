import sqlite3

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)

menu = [{'url': '.index', 'title': 'Панель'},
        {'url': '.listcars', 'title': 'Список авто'},
        {'url': '.listusers', 'title': 'Список users'},
        {'url': 'index', 'title': 'Сайт'},
        {'url': '.logout', 'title': 'Выйти'}]

db = None  # ссылается на соединение с БД

admin = Blueprint(
    'admin', __name__, template_folder='templates', static_folder='static')


@admin.before_request
def before_request():
    global db
    db = g.get('link_db')


@admin.teardown_request
def teardown_request(request):
    global db
    db = None
    return request


@admin.route('/')
def index():
    if not isLogged():
        return redirect(url_for('.login'))

    return render_template('admin/index.html', menu=menu, title='Админ-панель')


def login_admin():
    """Вход в админ-панель"""
    session['admin_logged'] = 1


def isLogged():
    """Зашел админ в панель или нет"""
    return True if session.get('admin_logged') else False


def logout_admin():
    """Выход из админ-панели"""
    session.pop('admin_logged', None)


@admin.route('/login', methods=["POST", "GET"])
def login():
    if isLogged():
        return redirect(url_for('.index'))

    if request.method == "POST":
        if request.form['user'] == "admin" and request.form['psw'] == "12345":
            login_admin()
            return redirect(url_for('.index'))
        else:
            flash("Неверная пара логин/пароль", "error")

    return render_template('admin/login.html', title='Админ-панель')


@admin.route('/logout', methods=["POST", "GET"])
def logout():
    if not isLogged():
        return redirect(url_for('.login'))

    logout_admin()

    return redirect(url_for('.login'))


@admin.route('/listcars')
def listcars():
    if not isLogged():
        return redirect(url_for('.login'))

    list = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f'SELECT title, text, url FROM posts')
            list = cur.fetchall()
        except sqlite3.Error as e:
            print("Ошибка получения статей из БД " + str(e))
    return render_template(
        'admin/listcars.html',
        title='Список авто',
        menu=menu, list=list)


@admin.route('/listusers')
def listusers():
    if not isLogged():
        return redirect(url_for('.login'))

    list = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f'SELECT name, email FROM users ORDER BY time DESC')
            list = cur.fetchall()
        except sqlite3.Error as e:
            print("Ошибка получения пользователетей из БД " + str(e))
    return render_template(
        'admin/listusers.html',
        title='Список пользователей',
        menu=menu, list=list)
