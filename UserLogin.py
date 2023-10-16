from flask import url_for
from flask_login import UserMixin


class UserLogin(UserMixin):
    def fromDB(self, user_id, db):
        """При создании юзера в декораторе user_loader """
        self.__user = db.getUser(user_id)
        return self

    def create(self, user):
        """Когда юзер авторизуется на сайте"""
        self.__user = user
        return self

    def get_id(self):
        """Получение id пользователя"""
        return str(self.__user['id'])

    def getName(self):
        """Получение имени пользователя"""
        return self.__user['name'] if self.__user else "Без имени"

    def getEmail(self):
        """Получение email пользователя"""
        return self.__user['email'] if self.__user else "Без email"

    def getAvatar(self, app):
        """Получение автара"""
        img = None
        if not self.__user['avatar']:
            try:
                print(f'app.root_path = {app.root_path}')
                with app.open_resource(app.root_path + url_for('static', filename='images/default.png'), "rb") as f:
                    img = f.read()
            except FileNotFoundError as e:
                print("Не найден аватар по умолчанию: "+str(e))
        else:
            img = self.__user['avatar']

        return img

    def verifyExt(self, filename):
        """Проверка что фото расширения .png"""
        ext = filename.rsplit('.', 1)[1]
        if ext == "png" or ext == "PNG":
            return True
        return False
