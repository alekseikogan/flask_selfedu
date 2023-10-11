from flask import (Flask, abort, flash, redirect, render_template, request,
                   session, url_for)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwertyuioplkjhgfdsazxcvbnm'

menu = [{'name': 'Установка', 'url': 'install-flask'},
        {'name': 'Первое приложение', 'url': 'first-app'},
        {'name': 'Обратная связь', 'url': 'contact'}]


@app.route('/')
def index():
    return render_template(
        'index.html',
        title='Главная страница сайта',
        menu=menu)


@app.route('/about')
def about():
    return render_template(
        'about.html',
        title='О сайте',
        menu=menu)


@app.route('/profile/<username>')
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f'Профиль пользователя: {username}'


@app.route('/contact', methods=['POST', 'GET'])
def contact():
    if request.method == 'POST':
        if len(request.form['username']) > 2:
            flash('Сообщение отправлено.', category='success')
        else:
            flash('Ошибка отправки!', category='error')
        print(request.form)
    return render_template('contact.html', title='Обратная связь', menu=menu)


@app.errorhandler(404)
def pagenotfound(error):
    return render_template(
        'page404.html',
        title='Упс, такой страницы нет...',
        menu=menu), 404


@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST' and request.form['username'] == 'alekseikogan' and request.form['psw'] == 'StelsDelta200':
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))

    return render_template('login.html', title='Авторизация', menu=menu)


if __name__ == '__main__':
    app.run(debug=True)
